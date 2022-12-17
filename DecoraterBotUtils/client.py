# coding=utf-8
"""
Client for DecoraterBot.
"""
import logging
import time
import os
import sys
import traceback
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from colorama import Fore, Back, Style, init

from .readers import *

__all__ = ['config', 'BotClient']


class BotClient(commands.Bot):
    """
    Bot Main client Class.
    This is where the Events are Registered.
    """
    def __init__(self, **kwargs):
        self.uptime_count_begin = time.time()
        self.logged_in_ = False
        self.is_bot_logged_in = False
        self.localization_reader = DbLocalizationReader()
        super(BotClient, self).__init__(
            description=self.localization_reader.get_str(5, config.language),
            command_prefix=commands.when_mentioned_or(),
            status=discord.Status.online,
            activity=discord.Streaming(
                name=self.localization_reader.get_str(3, config.language),
                url=self.localization_reader.get_str(6, config.language)),
            # intents=self.bot_intents,
            intents=discord.Intents.default(),
            pm_help=False,
            **kwargs)
        self.stdout = open(os.path.join(sys.path[0], 'resources', 'Logs', 'console.log'), 'w')
        self.stderr = open(os.path.join(sys.path[0], 'resources', 'Logs', 'unhandled_tracebacks.log'), 'w')
        self.tree.on_error = self.on_app_command_error
        handler = logging.StreamHandler(stream=self.stdout)
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
        level = logging.INFO
        discord.utils.setup_logging(handler=handler, formatter=formatter, level=level)

    async def __aexit__(self, *exc):
        self.localization_reader.close()
        await super(BotClient, self).__aexit__(*exc)

    class DbTranslator(app_commands.Translator):
        """
        Translates commands to another language using a database.
        """
        def __init__(self, localization_reader):
            self.localization_reader = localization_reader

        async def translate(self,
                            string: app_commands.locale_str,
                            locale: discord.Locale,
                            context: app_commands.TranslationContextTypes) -> Optional[str]:
            try:
                return self.localization_reader.get_str(int(string.extras['str_id']), str(locale))
            except KeyError:
                return None

    async def setup_hook(self) -> None:
        self.remove_command("help")
        await self.tree.set_translator(self.DbTranslator(self.localization_reader))
        for plugins_cog in config.default_plugins:
            ret = await self.load_bot_extension(plugins_cog)
            if isinstance(ret, str):
                print(ret)

    async def load_bot_extension(self, extension_name) -> None | str:
        """
        loads a bot extension module.
        """
        try:
            await self.load_extension(f'cogs.{extension_name}')
        except Exception:
            return str(traceback.format_exc())

    async def unload_bot_extension(self, extension_name) -> None:
        """
        unloads a bot extension module.
        """
        await self.unload_extension(f'cogs.{extension_name}')

    async def reload_bot_extension(self, extension_name) -> None | str:
        """
        reloads a bot extension module.
        """
        try:
            await self.reload_extension(f'cogs.{extension_name}')
        except Exception:
            return str(traceback.format_exc())

    async def start_bot(self) -> None:
        """
        Allows the bot to Connect / Reconnect.
        :return: Nothing.
        """
        _continue = True if config.config is not None and config.found is True else False
        if _continue:
            try:
                if config.bot_token is not None:
                    self.is_bot_logged_in = True
                    await self.start(config.bot_token)
            except discord.errors.GatewayNotFound:
                print(self.localization_reader.get_str(2, config.language))
                return
            except discord.errors.LoginFailure:
                print(self.localization_reader.get_str(1, config.language))
                return
            except TypeError:
                pass
            except KeyboardInterrupt:
                pass
            except Exception:
                pass
        else:
            print(self.localization_reader.get_str(0, config.language))
            return

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """..."""
        str(self)
        exceptioninfo = "".join(traceback.format_exception(error))
        if isinstance(error, app_commands.CommandInvokeError):
            await interaction.response.send_message(f"Error: ```py\n{exceptioninfo}\n``` (Invoke Error)")
        elif isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(f"Error: ```py\n{exceptioninfo}\n``` (Check Failure)")
        else:
            pass

    async def on_ready(self):
        """
        Bot Event.
        :return: Nothing.
        """
        await self.on_bot_login()

    async def on_bot_login(self):
        """
        Function that does the on_ready event stuff after logging in.
        :return: Nothing.
        """
        if self.logged_in_ is False:
            self.logged_in_ = True
            init()
            print(Fore.GREEN + Back.BLACK + Style.BRIGHT + self.localization_reader.get_str(
                4, config.language).format(
                self.user.name, self.user.id, discord.__version__, '\n'))
            sys.stdout = self.stdout
            sys.stderr = self.stderr
            await self.tree.sync()

    # def bot_intents(self) -> discord.Intents:
    #     _intents = discord.Intents.default()
    #     _intents.members = True
    #     _intents.presences = True
    #     return _intents


config = BotCredentialsReader()
