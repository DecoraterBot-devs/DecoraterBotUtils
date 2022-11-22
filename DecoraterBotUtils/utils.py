"""
Utils for DecoraterBot.
"""
import json
import logging
import time
import os
import sys
import traceback

import consolechange
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
from colorama import Fore, Back, Style, init

from .BotErrors import *


# we import asyncpg as I want to use that
# for credentials and other runtime stuff
# instead of json.
__all__ = [
    'get_plugin_full_name', 'GitHubRoute',
    'PluginData', 'construct_reply',
    'BotPMError', 'BotCredentialsVars', 'CreditsReader',
    'PluginTextReader', 'PluginConfigReader', 'make_version',
    'PluginInstaller', 'log_writer', 'CogLogger',
    'config', 'BotClient', 'Checks']


def get_plugin_full_name(plugin_name):
    """
    returns the plugin's full name.
    """
    if plugin_name is not '':
        return 'DecoraterBotCore.plugins.' + plugin_name
    return None


def construct_reply(message, msgdata):
    """
    Constructs a bot reply.
    """
    return msgdata.format(message.server.name, message.channel.name)


class GitHubRoute:
    """gets the route information to the github resource/file(s)."""
    HEAD = "https://raw.githubusercontent.com/"

    def __init__(self, user: str, repo: str,
                 branch: str, filename: str):
        self.url = (self.HEAD + user + "/" +
                    repo + "/" + branch + "/" +
                    filename)


class PluginData:
    """
    Stores the data to plugins.
    """
    def __init__(self, plugincode=None, version=None,
                 textjson=None):
        self.plugincode = plugincode
        self.version = version
        self.textjson = textjson


# TODO: Place the code in this class with a global on_command_error.
class BotPMError:
    """
    Class for PMing bot errors.
    """
    def __init__(self, bot):
        self.bot = bot

    async def resolve_send_message_error(self, interaction: discord.Interaction):
        """
        Resolves errors when sending messages.
        """
        await self.resolve_send_message_error_old(interaction)

    async def resolve_send_message_error_old(self, interaction: discord.Interaction):
        """
        Resolves errors when sending messages.
        """
        try:
            await self.bot.send_message(
                interaction.user,
                content=self.bot.consoletext['error_message'][0].format(
                    interaction.guild.name,
                    interaction.channel.name))
        except discord.errors.Forbidden:
            return


class BaseConfigReader:
    """
    Base config Class.
    """
    def __init__(self, file=None):
        self.config = None
        self.filename = file
        self.file = None
        self.json_file = None
        self.load()

    def load(self):
        """
        Loads the JSON config Data.
        :return: List.
        """
        self.json_file = os.path.join(
            sys.path[0], 'resources', 'ConfigData',
            self.filename)
        try:
            with open(self.json_file) as self.file:
                self.config = json.load(self.file)
        except(OSError, IOError):
            pass

    def getconfig(self, key):
        """
        Gets a JSON Config Value basted on the key provided.
        :param key: String key to the entry in the JSON file
        :return: JSON config Value.
        """
        return self.config[key]

    def setconfig(self, key, data):
        """
        Sets a JSON Config Value basted on the key and data provided.
        :param key: String key to the entry in the JSON file
        :param data: Data to replace old value with.
        """
        self.config[key] = data
        with open(self.json_file) as self.file:
            json.dump(self.config, self.file, indent=4, sort_keys=True)


class BaseCredentialsReader(BaseConfigReader):
    """
    Base config Class.
    """
    def __init__(self, file=None):
        super(BaseCredentialsReader, self).__init__(file=file)


class CreditsReader(BaseConfigReader):
    """
    Obtains Data from credits.json
    """
    def __init__(self, file=None):
        super(CreditsReader, self).__init__(file=file)

    def getcredits(self, key, key2):
        """
        Gets a JSON Config Value basted on the key provided.
        :param key: String key to the entry in the JSON file.
        :param key2: String key to the entry in the JSON file.
        :return: JSON config Value.
        """
        return self.config[key][key2]

    def setcredits(self, key, key2, data):
        """
        Sets a JSON Config Value basted on the key and data provided.
        :param key: String key to the entry in the JSON file
        :param key2: String key to the entry in the JSON file.
        :param data: Data to replace old value with.
        """
        try:
            self.config[key][key2] = data
        except (KeyError, TypeError):
            self.config[key] = {}
            self.config[key][key2] = data
        try:
            with open(self.json_file, mode='w') as file:
                file.write(json.dumps(self.config, indent=4, sort_keys=True))
        except(OSError, IOError):
            pass


def plugintextreader(file=None):
    """
    Obtains data from plugin json files
    that contains text for commands.
    """
    json_file = os.path.join(
        sys.path[0], 'resources',
        'ConfigData', 'plugins',
        file)
    try:
        with open(json_file) as fileobj:
            return json.load(fileobj)
    except(OSError, IOError):
        pass


def pluginconfigreader(file=None):
    """
    Obtains data from plugin json files
    that contains config for commands.
    """
    jsonfile = os.path.join(
        sys.path[0], 'resources', 'ConfigData',
        file)
    try:
        with open(jsonfile) as fileobje:
            return json.load(fileobje)
    except(OSError, IOError):
        pass


PluginConfigReader = pluginconfigreader
PluginTextReader = plugintextreader


class BotCredentialsVars(BaseCredentialsReader):
    """
    Class for getting the Credentials.json config Values.
    """
    def __init__(self):
        super(BotCredentialsVars, self).__init__(file='Credentials.json')

        # defaults.
        self.logbans = False  # bool
        self.logunbans = False  # bool
        self.discord_logger = False  # bool
        self.asyncio_logger = False  # bool
        self.is_official_bot = False  # bool
        self.pm_commands_list = False  # bool
        self.log_error = False  # bool
        self.pm_command_errors = False  # bool
        self.enable_error_handler = False  # bool
        self.bot_prefix = ''  # string
        self.discord_user_id = ''  # string
        self.bot_token = ''  # string
        self.language = 'en'  # string
        self.description = ''  # string
        self.shards = 0  # int
        self.run_on_shard = 0  # int
        self.twitch_url = ''  # string
        self.youtube_url = ''  # string
        self.default_plugins = []  # list

        # populate the values from Credentials.json.
        self.set_values()

    def set_values(self):
        """
        sets values of the variables.
        """
        try:
            self.logbans = self.getconfig(
                'logbans')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.logunbans = self.getconfig(
                'logunbans')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.discord_logger = self.getconfig(
                'discord_py_logger')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.asyncio_logger = self.getconfig(
                'asyncio_logger')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.is_official_bot = self.getconfig(
                'Is_Official_Bot_Account')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.pm_commands_list = self.getconfig(
                'PM_Commands')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_error = self.getconfig(
                'log_error')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.pm_command_errors = self.getconfig(
                'pm_command_errors')  # bool
        except (KeyError, TypeError):
            pass
        self.enable_error_handler = (
            True if not self.pm_command_errors else False)  # bool
        try:
            self.bot_prefix = self.getconfig(
                'bot_prefix')  # string
        except (KeyError, TypeError):
            pass
        try:
            self.discord_user_id = self.getconfig(
                'ownerid')  # string
        except (KeyError, TypeError):
            pass
        try:
            self.bot_token = self.getconfig(
                'token')  # string
        except (KeyError, TypeError):
            pass
        try:
            self.language = self.getconfig(
                'language')  # string
        except (KeyError, TypeError):
            pass
        try:
            self.description = self.getconfig(
                'description')  # string
        except (KeyError, TypeError):
            pass
        try:
            self.shards = self.getconfig(
                'shards')  # int
        except (KeyError, TypeError):
            pass
        try:
            self.run_on_shard = self.getconfig(
                'run_on_shard')  # int
        except (KeyError, TypeError):
            pass
        try:
            self.twitch_url = self.getconfig(
                'twitch_url')  # string
        except (KeyError, TypeError):
            pass
        try:
            self.youtube_url = self.getconfig(
                'youtube_url')  # string
        except (KeyError, TypeError):
            pass
        try:
            self.default_plugins = self.getconfig(
                'default_plugins')  # dict
        except (KeyError, TypeError):
            pass


def make_version(pluginname, pluginversion,
                 version=None):
    """
    Makes or remakes the contents to the plugin list
    json that stores the installed versions.

    Used for installing / updating plugins.
    """
    if version is None:
        version = {}
    version[pluginname] = {}
    version[pluginname]['version'] = pluginversion
    return version


class PluginInstaller:
    """
    Class that implements all the Plugin
    Installation / updating system for
    DecoraterBot.
    """
    def __init__(self, connector=None, loop=None):
        self.connector = connector
        self.loop = loop

    async def request_repo(self, pluginname):
        """
        requests the bot's plugin
        repository for a particular plugin.
        """
        url = (
            GitHubRoute(
                "DecoraterBot-devs", "DecoraterBot-cogs",
                "master", "cogslist.json")).url
        async with aiohttp.ClientSession(
                connector=self.connector, loop=self.loop) as session:
            data = await session.get(url)
            resp1 = await data.json(content_type='text/plain')
            version = resp1[pluginname]['version']
            url2 = resp1[pluginname]['downloadurl']
            url3 = resp1[pluginname]['textjson']
            data2 = await session.get(url2)
            data3 = await session.get(url3)
            plugincode = await data2.text()
            textjson = await data3.text()
            return PluginData(
                plugincode=plugincode,
                version=version,
                textjson=textjson)

    async def checkupdate(self, pluginname):
        """
        checks a plugin provided for updates.
        :returns: string considing of plugin's name
        and plugin's current version.
        """
        pluginversion = None  # for now until this is complete.
        requestrepo = await self.request_repo(pluginname)
        if requestrepo.version != pluginversion:
            # return every instance of 'PluginData'.
            return requestrepo

    async def checkupdates(self, pluginlist):
        """
        Checks for updates for plugins
        in the plugin list.
        """
        update_list = []
        for plugin in pluginlist:
            update_list.append(await self.checkupdate(plugin))
        # so bot can know which plugins have updates.
        return update_list

    async def install_plugin(self, pluginname):
        """
        installs a plugin provided.
        Also gets and sets a cached
        version of them too.
        """
        # TODO: Finish this.
        pass

    async def install_plugins(self, pluginlist):
        """
        installs all the plugins listed.
        """
        for pluginname in pluginlist:
            # install each plugin individually.
            await self.install_plugin(pluginname)


def log_writer(filename, data):
    """
    Log file writer.

    This is where all the common
    log file writes go to.
    """
    file = open(filename, 'a', encoding='utf-8')
    size = os.path.getsize(filename)
    if size >= 32102400:
        file.seek(0)
        file.truncate()
    file.write(data)
    file.close()


# Some loggers lack the ability to get the server
# the event fired on.


class CogLogger:
    """
    Main cog logging Class.
    """
    def __init__(self, bot):
        self.bot = bot
        try:
            self.LogData = BaseConfigReader(file='LogData.json').config
            self.LogData = self.LogData[self.bot.BotConfig.language]
        except FileNotFoundError:
            print(str(self.bot.consoletext['Missing_JSON_Errors'][2]))
            sys.exit(2)

    def log_data_reader(self, entry, index, *args):
        """
        log data reader that also
        does the needed formatting.

        method specifically to fix the
        stupid Codacy duplication bug.
        """
        return str(self.LogData[entry][index]).format(
            *args)

    def resolve_embed_logs(self, before):
        """
        Resolves if the message was edited or not.
        :param before: Messages.
        :return: Nothing.
        """
        if before.channel.is_private is True:
            data = str(self.LogData['Embed_Logs'][0])
        else:
            data = str(self.LogData['Embed_Logs'][1])
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'embeds.log')
        try:
            log_writer(logfile, data + "\n")
        except PermissionError:
            return

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
        if bool(funcname):
            if bool(tbinfo):
                exception_data = 'Ignoring exception caused at {0}:\n' \
                                 '{1}'.format(funcname, tbinfo)
                logfile = os.path.join(
                    sys.path[0], 'resources', 'Logs', 'error_log.log')
                try:
                    log_writer(logfile, exception_data)
                except PermissionError:
                    return
            else:
                raise err
        else:
            raise err

    def onban(self, member):
        """
        Logs Bans.
        :param member: Members.
        :return: Nothing.
        """
        mem_name = member.name
        mem_id = member.id
        mem_dis = member.discriminator
        mem_svr_name = member.server.name
        ban_log_data = str(self.LogData['Ban_Logs'][0]).format(mem_name,
                                                               mem_id, mem_dis,
                                                               mem_svr_name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'bans.log')
        log_writer(logfile, ban_log_data)

    def onavailable(self, server):
        """
        Logs Available Servers.
        :param server:
        :return: Nothing.
        """
        available_log_data = str(
            self.LogData['On_Server_Available'][0]).format(server)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'available_servers.log')
        log_writer(logfile, available_log_data)

    def onunavailable(self, server):
        """
        Logs Unavailable Servers
        :param server: Servers.
        :return: Nothing.
        """
        unavailable_log_data = str(
            self.LogData['On_Server_Unavailable'][0]).format(server)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'unavailable_servers.log')
        log_writer(logfile, unavailable_log_data)

    def onunban(self, server, user):
        """
        Logs Unbans.
        :param server: Server.
        :param user: Users.
        :return: Nothing.
        """
        unban_log_data = str(self.LogData['Unban_Logs'][0]
                             ).format(user.name, user.id, user.discriminator,
                                      server.name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'unbans.log')
        log_writer(logfile, unban_log_data)

    def onserverremove(self, server):
        """
        Logs server Removes.
        :param server: Server.
        :return: Nothing.
        """
        server_remove_log_data = str(self.LogData['server_remove'][0]).format(
            self.bot.user.name, self.bot.user.id, server.name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'server_remove.log')
        log_writer(logfile, server_remove_log_data)

    def onresumed(self):
        """
        Logs when bot resumes.
        :return: Nothing.
        """
        resumed_log_data = str(self.LogData['resumed'][0])
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'resumed.log')
        log_writer(logfile, resumed_log_data)

    def onkick(self, member):
        """
        Logs Kicks.
        :param member: Members.
        :return: Nothing.
        """
        mem_name = member.name
        mem_id = member.id
        mem_dis = member.discriminator
        mem_svr_name = member.server.name
        kick_log_data = str(self.LogData['Kick_Logs'][0]).format(mem_name,
                                                                 mem_id,
                                                                 mem_dis,
                                                                 mem_svr_name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'kicks.log')
        log_writer(logfile, kick_log_data)


config = BotCredentialsVars()


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
            intents=discord.Intents.default(),
            **kwargs)
        self.tree.on_error = self.on_app_command_error
        self.BotPMError = BotPMError(self)
        self.logger = CogLogger(self)
        # Deprecated.
        self.resolve_send_message_error = (
            self.BotPMError.resolve_send_message_error)
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
    def banlist(self):
        """
        returns the list of users banned
        from using the bot.
        """
        type(self)
        return PluginConfigReader(
            file='BotBanned.json')

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
        returns the begin time.
        """
        return self._start

    @property
    def credits(self):
        """
        returns the stuff that the Credits reader returns.
        """
        type(self)
        return CreditsReader(file="credits.json")

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

    async def load_bot_extension(self, extension_full_name):
        """
        loads an bot extension module.
        """
        try:
            await self.load_extension(extension_full_name)
        except Exception:
            return str(traceback.format_exc())

    async def unload_bot_extension(self, extension_full_name):
        """
        unloads an bot extension module.
        """
        await self.unload_extension(extension_full_name)

    async def load_plugin(self, plugin_name, raiseexec=True):
        """
        Loads up a plugin in the plugins folder in DecoraterBotCore.
        """
        pluginfullname = get_plugin_full_name(plugin_name)
        if pluginfullname is None:
            if raiseexec:
                raise ImportError(
                    "Plugin Name cannot be empty.")
        err = await self.load_bot_extension(pluginfullname)
        if err is not None:
            return err

    async def unload_plugin(self, plugin_name, raiseexec=True):
        """
        Unloads a plugin in the plugins folder in DecoraterBotCore.
        """
        pluginfullname = get_plugin_full_name(plugin_name)
        if pluginfullname is None:
            if raiseexec:
                raise CogUnloadError(
                    "Plugin Name cannot be empty.")
        await self.unload_bot_extension(pluginfullname)

    async def reload_plugin(self, plugin_name):
        """
        Reloads a plugin in the plugins folder in DecoraterBotCore.
        """
        await self.unload_plugin(plugin_name, raiseexec=False)
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
        try:
            await self.on_bot_login()
        except Exception as e:
            funcname = 'on_ready'
            tbinfo = str(traceback.format_exc())
            self.logger.on_bot_error(funcname, tbinfo, e)

    async def on_bot_login(self):
        """
        Function that does the on_ready event stuff after logging in.
        :return: Nothing.
        """
        if self.logged_in_ is False:
            self.logged_in_ = True
            bot_name = self.user.name
            init()
            print(Fore.GREEN + Back.BLACK + Style.BRIGHT + str(
                self.consoletext['Window_Login_Text'][0]).format(
                bot_name, self.user.id, discord.__version__))
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
        self.logger.on_bot_error(funcname, tbinfo, None)

    # Helpers.
    def command_traceback_helper(self, tbinfo):
        """
        Helps iterate through a list of every
        line in a command's traceback.
        """
        tracebackdata = ""
        for line in tbinfo:
            tracebackdata = tracebackdata + line
        return tracebackdata


class Checks:
    @staticmethod
    def is_bot_owner():
        def predicate(interaction: discord.Interaction) -> bool:
            return interaction.user.id == int(interaction.client.BotConfig.discord_user_id)
        return app_commands.check(predicate)

    @staticmethod
    def is_user_bot_banned():
        def predicate(interaction: discord.Interaction) -> bool:
            return interaction.user.id not in interaction.client.banlist['Users']
        return app_commands.check(predicate)
