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
        self._start = time.time()
        self.logged_in_ = False
        self.somebool = False
        self.reload_normal_commands = False
        self.reload_reason = None
        self.desmod = None
        self.desmod_new = None
        self.rejoin_after_reload = False
        self.sent_prune_error_message = False
        self.is_bot_logged_in = False
        super(BotClient, self).__init__(
            command_prefix='',
            status=discord.Status.online,
            activity=discord.Streaming(
                name=self.consoletext['On_Ready_Game'][0],
                url=self.BotConfig.twitch_url),
            # intents=self.bot_intents,
            intents=discord.Intents.default(),
            **kwargs)
        self.tree.on_error = self.on_app_command_error
        self.call_all()

    async def setup_hook(self) -> None:
        await self.load_all_default_plugins()

    @property
    def version(self):
        """
        returns the bot's version number.
        """
        return self.consoletext['WindowVersion'][0]

    @property
    def BotConfig(self):
        """
        Reads the bot's config data.
        """
        type(self)
        return config

    @property
    def consoletext(self):
        """
        returns the bot's
        console text.
        """
        consoledata = BaseConfigReader(file='ConsoleWindow.json').config
        consoledata = consoledata[self.BotConfig.language]
        return consoledata

    @property
    def commands_list(self):
        """
        retrieves a list of all the bot's registered commands.
        """
        plugin_list = []
        for command in self.commands:
            plugin_list.append(command)
        return plugin_list

    @property
    def uptime_count_begin(self):
        """
        returns the start time.
        """
        return self._start

    @property
    def credits(self):
        """
        returns the stuff that the Credits reader returns.
        """
        type(self)
        return PluginConfigReader(file="credits.json", credits=True)

    @property
    def credentials_check(self):
        """
        Checks if the Credentials.json
        file exists.
        """
        PATH = os.path.join(
            sys.path[0], 'resources', 'ConfigData', 'Credentials.json')
        return os.path.isfile(PATH) and os.access(PATH, os.R_OK)

    async def load_all_default_plugins(self):
        """
        Handles loading all plugins that __init__
        used to load up.
        """
        self.remove_command("help")
        for plugins_cog in self.BotConfig.default_plugins:
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

    def discord_logger(self):
        """
        Logger Data.
        """
        if self.BotConfig.discord_logger:
            self.set_up_discord_logger()

    def asyncio_logger(self):
        """
        Asyncio Logger.
        """
        if self.BotConfig.asyncio_logger:
            self.set_up_asyncio_logger()

    def set_up_loggers(self, loggers=None):
        """
        Logs Events from discord and/or asyncio stuff.
        """
        if loggers is not None:
            if loggers == 'discord':
                logger = logging.getLogger('discord')
                logger.setLevel(logging.DEBUG)
                handler = logging.FileHandler(
                    filename=os.path.join(
                        sys.path[0], 'resources', 'Logs', 'discordpy.log'),
                    encoding='utf-8', mode='w')
                handler.setFormatter(logging.Formatter(
                    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
                logger.addHandler(handler)
            elif loggers == 'asyncio':
                self.loop.set_debug(True)
                asynciologger = logging.getLogger('asyncio')
                asynciologger.setLevel(logging.DEBUG)
                asynciologgerhandler = logging.FileHandler(
                    filename=os.path.join(
                        sys.path[0], 'resources', 'Logs', 'asyncio.log'),
                    encoding='utf-8', mode='w')
                asynciologgerhandler.setFormatter(logging.Formatter(
                    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
                asynciologger.addHandler(asynciologgerhandler)

    def set_up_discord_logger(self):
        """
        Sets up the Discord Logger.
        """
        self.set_up_loggers(loggers='discord')

    def set_up_asyncio_logger(self):
        """
        Sets up the asyncio Logger.
        """
        self.set_up_loggers(loggers='asyncio')

    def changewindowtitle(self):
        """
        Changes the console's window Title.
        """
        consolechange.consoletitle(
            self.consoletext['WindowName'][0] + self.version)

    # def changewindowsize(self):
    #     """
    #     Changes the Console's size.
    #     """
    #     # not used but avoids issues with this being a classmethod.
    #     type(self)
    #     consolechange.consolesize(80, 23)

    def call_all(self):
        """
        calls all functions that __init__ used to
        call except for super.
        """
        self.asyncio_logger()
        self.discord_logger()
        self.changewindowtitle()
        # if self.BotConfig.change_console_size:
        #     self.changewindowsize()
        # self.login_helper()

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
        _continue = False
        if self.BotConfig.config is None:
            if self.credentials_check:
                _continue = True
            else:
                print(str(self.consoletext['Credentials_Not_Found'][0]))
                return
        else:
            _continue = True
        if _continue:
            try:
                if self.BotConfig.bot_token is not None:
                    self.is_bot_logged_in = True
                    await self.start(
                        self.BotConfig.bot_token)
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

    def on_bot_error(self, funcname, tbinfo, err):
        """
        This Function is for Internal Bot use only.
        It is for catching any Errors and writing them to a file.

        Usage
        =====
        :param funcname: Must be a string with the name of the function
        that caused an Error.
            raises the Errors that happened if empty string or None is
            given.
        :param tbinfo: string data of the traceback info. Must be a
            string for this to not Error itself.
            raises the Errors that happened if empty string or None is
            given.
        :param err: Error Data from Traceback. (RAW)
        """
        str(self)
        if bool(funcname):
            if bool(tbinfo):
                exception_data = 'Ignoring exception caused at {0}:\n' \
                                 '{1}'.format(funcname, tbinfo)
                logfile = os.path.join(
                    sys.path[0], 'resources', 'Logs', 'error_log.log')
                try:
                    file = open(logfile, 'a', encoding='utf-8')
                    size = os.path.getsize(logfile)
                    if size >= 32102400:
                        file.seek(0)
                        file.truncate()
                    file.write(exception_data)
                    file.close()
                except PermissionError:
                    return
            else:
                raise err
        else:
            raise err

    async def on_ready(self):
        """
        Bot Event.
        :return: Nothing.
        """
        await self.tree.sync()
        try:
            await self.on_bot_login()
        except Exception as e:
            funcname = 'on_ready'
            tbinfo = str(traceback.format_exc())
            self.on_bot_error(funcname, tbinfo, e)

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
            sys.stdout = open(os.path.join(
                sys.path[0], 'resources', 'Logs', 'console.log'),
                'w')
            sys.stderr = open(os.path.join(
                sys.path[0], 'resources', 'Logs',
                'unhandled_tracebacks.log'), 'w')

    async def on_error(self, event, *args, **kwargs):
        """
        Bot Event.
        :param event: Event.
        :param args: Args.
        :param kwargs: Other Args.
        :return: Nothing.
        """
        str(args)
        str(kwargs)
        funcname = event
        tbinfo = str(traceback.format_exc())
        self.on_bot_error(funcname, tbinfo, None)

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

    def command_traceback_helper(self, tbinfo):
        """
        Helps iterate through a list of every
        line in a command's traceback.
        """
        tracebackdata = ""
        for line in tbinfo:
            tracebackdata = tracebackdata + line
        return tracebackdata

    # def bot_intents(self) -> discord.Intents:
    #     _intents = discord.Intents.default()
    #     _intents.members = True
    #     return _intents


config = BotCredentialsReader()
