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

__all__ = ['BotClient']


class BotClient(commands.Bot):
    """
    Bot Main client Class.
    This is where the Events are Registered.
    """
    def __init__(
            self,
            readers: list[DbCredentialsReader | DbLocalizationReader],
            description: str,
            activity_name: str,
            activity_url: str,
            **kwargs):
        self.uptime_count_begin = time.time()
        self.logged_in_: bool = False
        self.is_bot_logged_in: bool = False
        if len(readers) != 2:
            raise RuntimeError('There must be 2 readers at all times.')
        if isinstance(readers[0], DbCredentialsReader):
            self.credentials_reader: DbCredentialsReader = readers[0]
        else:
            raise RuntimeError(
                f'The first reader must be the credentials reader. Got \'{readers[0].__class__.__name__}\'.')
        if isinstance(readers[1], DbLocalizationReader):
            self.db_translator = self.DbTranslator(readers[1])
        else:
            raise RuntimeError(
                f'The second reader must be the localizations reader. Got \'{readers[1].__class__.__name__}\'.')
        super(BotClient, self).__init__(
            description=description,
            command_prefix=[],
            help_command=None,
            status=discord.Status.online,
            activity=discord.Streaming(
                name=activity_name,
                url=activity_url),
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

    class DbTranslator(app_commands.Translator):
        """
        Translates commands to another language using a database.
        """
        def __init__(self, localization_reader):
            self.localization_reader: DbLocalizationReader = localization_reader

        async def translate(self,
                            string: app_commands.locale_str,
                            locale: discord.Locale,
                            context: app_commands.TranslationContextTypes) -> Optional[str]:
            try:
                return await self.localization_reader.get_str_async(
                    int(string.extras['str_id']),
                    str(locale))
            except KeyError:
                return None

    async def setup_hook(self) -> None:
        await self.tree.set_translator(self.db_translator)
        if self.logged_in_ is False:
            self.logged_in_ = True
            init()
            print(Fore.GREEN + Back.BLACK + Style.BRIGHT +
                  (await self.db_translator.translate(
                      app_commands.locale_str('', str_id=4),
                      discord.Locale(await self.credentials_reader.language),
                      app_commands.translator.OtherTranslationContext)).format(
                      self.user.name, self.user.id, discord.__version__, '\n'))
            sys.stdout = self.stdout
            sys.stderr = self.stderr
        for plugins_cog in await self.credentials_reader.default_cogs:
            ret = await self.load_bot_extension(plugins_cog)
            if isinstance(ret, str):
                print(ret)
        await self.tree.sync()

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
        try:
            if await self.credentials_reader.bot_token is not None:
                self.is_bot_logged_in = True
                await self.start(await self.credentials_reader.bot_token)
        except discord.errors.GatewayNotFound:
            print(await self.db_translator.translate(
                app_commands.locale_str('', str_id=2),
                discord.Locale(await self.credentials_reader.language),
                app_commands.translator.OtherTranslationContext))
            return
        except discord.errors.LoginFailure:
            print(await self.db_translator.translate(
                app_commands.locale_str('', str_id=1),
                discord.Locale(await self.credentials_reader.language),
                app_commands.translator.OtherTranslationContext))
            return
        except TypeError:
            pass
        except KeyboardInterrupt:
            pass
        except Exception as ex:
            traceback.print_exception(ex)
            pass

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """..."""
        str(interaction)
        str(self)
        exceptioninfo = "".join(traceback.format_exception(error))
        if isinstance(error, app_commands.CommandInvokeError):
            sys.stderr.write(f'Error: ```py\n{exceptioninfo}\n``` (Invoke Error)')
        elif isinstance(error, app_commands.CheckFailure):
            sys.stderr.write(f'Error: ```py\n{exceptioninfo}\n``` (Check Failure)')
        else:
            pass

    # def bot_intents(self) -> discord.Intents:
    #     _intents = discord.Intents.default()
    #     _intents.members = True
    #     _intents.presences = True
    #     return _intents
