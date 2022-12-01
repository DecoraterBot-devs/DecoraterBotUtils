# coding=utf-8
"""
Client for DecoraterBot.
"""
import logging
import time
import os
import sys
import traceback

import consolechange
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
        self.somebool = False
        self.reload_normal_commands = False
        self.reload_reason = None
        self.desmod = None
        self.desmod_new = None
        self.rejoin_after_reload = False
        self.sent_prune_error_message = False
        self.is_bot_logged_in = False
        self.consoletext = BaseConfigReader(file='ConsoleWindow.json')[config.language]
        super(BotClient, self).__init__(
            command_prefix=config.bot_prefix,
            status=discord.Status.online,
            activity=discord.Streaming(
                name=self.consoletext['On_Ready_Game'][0],
                url=config.twitch_url),
            # intents=self.bot_intents,
            intents=discord.Intents.default(),
            **kwargs)
        self.stdout = open(os.path.join(sys.path[0], 'resources', 'Logs', 'console.log'), 'w')
        self.tree.on_error = self.on_app_command_error
        self.call_all()

    async def setup_hook(self) -> None:
        await self.load_all_default_plugins()

    async def load_all_default_plugins(self):
        """
        Handles loading all plugins that __init__
        used to load up.
        """
        self.remove_command("help")
        for plugins_cog in config.default_plugins:
            ret = await self.load_plugin(plugins_cog)
            if isinstance(ret, str):
                print(ret)

    async def load_bot_extension(self, extension_name):
        """
        loads an bot extension module.
        """
        try:
            await self.load_extension(f'.plugins.{extension_name}', package='DecoraterBotCore')
        except Exception:
            return str(traceback.format_exc())

    async def unload_bot_extension(self, extension_name):
        """
        unloads an bot extension module.
        """
        await self.unload_extension(f'.plugins.{extension_name}', package='DecoraterBotCore')

    async def load_plugin(self, plugin_name):
        """
        Loads up a plugin in the plugins folder in DecoraterBotCore.
        """
        err = await self.load_bot_extension(plugin_name)
        if err is not None:
            return err

    async def unload_plugin(self, plugin_name):
        """
        Unloads a plugin in the plugins folder in DecoraterBotCore.
        """
        await self.unload_bot_extension(plugin_name)

    async def reload_plugin(self, plugin_name):
        """
        Reloads a plugin in the plugins folder in DecoraterBotCore.
        """
        await self.unload_plugin(plugin_name)
        err = await self.load_plugin(plugin_name)
        if err is not None:
            return err

    def call_all(self):
        """
        calls all functions that __init__ used to
        call except for super.
        """
        handler = logging.StreamHandler(stream=self.stdout)
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
        level = logging.INFO
        discord.utils.setup_logging(handler=handler, formatter=formatter, level=level)
        consolechange.consoletitle(
            f'{self.consoletext["WindowName"][0]}{self.consoletext["WindowVersion"][0]}')

    async def login_helper(self):
        """
        Bot Login Helper.
        """
        await self.login_info()

    async def login_info(self):
        """
        Allows the bot to Connect / Reconnect.
        :return: Nothing or -1/-2 on failure.
        """
        _continue = True if config.config is not None and config.found is True else False
        if _continue:
            try:
                if config.bot_token is not None:
                    self.is_bot_logged_in = True
                    await self.start(config.bot_token)
            except discord.errors.GatewayNotFound:
                print(str(self.consoletext['Login_Gateway_No_Find'][0]))
                return
            except discord.errors.LoginFailure as e:
                if str(e) == "Improper credentials have been passed.":
                    print(str(self.consoletext['Login_Failure'][0]))
                    return
                elif str(e) == "Improper token has been passed.":
                    print(str(self.consoletext['Invalid_Token'][0]))
                    return
            except TypeError:
                pass
            except KeyboardInterrupt:
                pass
            except Exception:
                pass
        else:
            print(str(self.consoletext['Credentials_Not_Found'][0]))
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
        await self.tree.sync()
        await self.on_bot_login()

    async def on_bot_login(self):
        """
        Function that does the on_ready event stuff after logging in.
        :return: Nothing.
        """
        if self.logged_in_ is False:
            self.logged_in_ = True
            init()
            print(Fore.GREEN + Back.BLACK + Style.BRIGHT + str(
                self.consoletext['Window_Login_Text'][0]).format(
                self.user.name, self.user.id, discord.__version__))
            sys.stdout = self.stdout
            sys.stderr = open(os.path.join(
                sys.path[0], 'resources', 'Logs',
                'unhandled_tracebacks.log'), 'w')

    # Helpers.
    async def resolve_send_message_error(self, interaction: discord.Interaction):
        """
        Resolves errors when sending messages.
        """
        try:
            await interaction.user.send(
                content=self.consoletext['error_message'][0].format(
                    interaction.guild.name,
                    interaction.channel.name))
        except discord.errors.Forbidden:
            return

    # def bot_intents(self) -> discord.Intents:
    #     _intents = discord.Intents.default()
    #     _intents.members = True
    #     return _intents


config = BotCredentialsReader()
