"""
Utils for DecoraterBot.
"""
import json
import time
import os
import sys
import traceback

import consolechange
import discord
from discord.ext import commands
import aiohttp


__all__ = [
    'get_plugin_full_name', 'GitHubRoute',
    'PluginData', 'YTDLLogger', 'construct_reply',
    'BotPMError', 'BotCredentialsVars', 'CreditsReader',
    'PluginTextReader', 'PluginConfigReader', 'make_version',
    'PluginInstaller', 'ReconnectionHelper', 'log_writter',
    'CogLogger', 'config', 'BaseClient']


def get_plugin_full_name(plugin_name):
    """
    returns the plugin's full name.
    """
    if plugin_name is not '':
        return 'DecoraterBotCore.plugins.' + plugin_name
    return None


def construct_reply(message, msgdata):
    """
    Constructs an bot reply.
    """
    return msgdata % (message.server.name, message.channel.name)


class GitHubRoute:
    """gets the route information to the an github resource/file."""
    HEAD = "https://raw.githubusercontent.com/"

    def __init__(self, user : str, repo : str,
                 branch : str, filename : str):
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


class YTDLLogger(object):
    """
    Class for Silencing all of the Youtube_DL Logging stuff that defaults to
    console.
    """
    def __init__(self, bot):
        self.bot = bot

    def log_file_code(self, meth, msg):
        """
        Logs data to file (if set).
        :param meth: Method name.
        :param msg: message.
        :return: Nothing.
        """
        if meth is not '':
            if meth == 'ytdl_debug':
                logfile = os.path.join(
                    sys.path[0], 'resources', 'Logs',
                    'ytdl_debug_logs.log')
                try:
                    self.bot.DBLogs.log_writter(logfile, msg + '\n')
                except PermissionError:
                    return
            elif meth == 'ytdl_warning':
                logfile2 = os.path.join(
                    sys.path[0], 'resources', 'Logs',
                    'ytdl_warning_logs.log')
                try:
                    self.bot.DBLogs.log_writter(logfile2, msg + '\n')
                except PermissionError:
                    return
            elif meth == 'ytdl_error':
                logfile3 = os.path.join(
                    sys.path[0], 'resources', 'Logs',
                    'ytdl_error_logs.log')
                try:
                    self.bot.DBLogs.log_writter(logfile3, msg + '\n')
                except PermissionError:
                    return
            elif meth == 'ytdl_info':
                logfile4 = os.path.join(
                    sys.path[0], 'resources', 'Logs',
                    'ytdl_info_logs.log')
                try:
                    self.bot.DBLogs.log_writter(logfile4, msg + '\n')
                except PermissionError:
                    return
        else:
            return

    def log_setting_check(self, meth, msg):
        """
        checks the log youtube_dl setting.
        """
        if self.bot.BotConfig.log_ytdl:
            self.log_file_code(meth, msg)

    def info(self, msg):
        """
        Reroutes the Youtube_DL Messages of this type to teither a file or
        silences them.
        :param msg: Message.
        :return: Nothing.
        """
        self.log_setting_check('ytdl_info', msg)

    def debug(self, msg):
        """
        Reroutes the Youtube_DL Messages of this type to teither a file or
        silences them.
        :param msg: Message.
        :return: Nothing.
        """
        self.log_setting_check('ytdl_debug', msg)

    def warning(self, msg):
        """
        Reroutes the Youtube_DL Messages of this type to teither a file or
        silences them.
        :param msg: Message.
        :return: Nothing.
        """
        self.log_setting_check('ytdl_warning', msg)

    def error(self, msg):
        """
        Reroutes the Youtube_DL Messages of this type to teither a file or
        silences them.
        :param msg: Message.
        :return: Nothing.
        """
        self.log_setting_check('ytdl_error', msg)


class BotPMError:
    """
    Class for PMing bot errors.
    """
    def __init__(self, bot):
        self.bot = bot

    async def resolve_send_message_error(self, ctx):
        """
        Resolves errors when sending messages.
        """
        await self.resolve_send_message_error_old(
            ctx.message)

    async def resolve_send_message_error_old(self, message):
        """
        Resolves errors when sending messages.
        """
        try:
            await self.bot.send_message(
                message.author,
                content=construct_reply(
                    message,
                    self.bot.consoletext['error_message'][0]))
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
        sys.path[0], 'resources', 'ConfigData', 'plugins',
        file)
    try:
        with open(json_file) as fileobj:
            return json.load(fileobj)
    except(OSError, IOError):
        pass
    return None


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
    return None


PluginConfigReader = pluginconfigreader
PluginTextReader = plugintextreader


class BotCredentialsVars(BaseCredentialsReader):
    """
    Class for getting the Credentials.json config Values.
    """
    def __init__(self):
        super(BotCredentialsVars, self).__init__(file='Credentials.json')

        # defaults.
        self.logging = False  # bool
        self.logbans = False  # bool
        self.logunbans = False  # bool
        self.logkicks = False  # bool
        self.log_games = False  # bool
        self.discord_logger = False  # bool
        self.asyncio_logger = False  # bool
        self.log_available = False  # bool
        self.log_unavailable = False  # bool
        self.log_channel_create = False  # bool
        self.is_official_bot = False  # bool
        self.log_ytdl = False  # bool
        self.pm_commands_list = False  # bool
        self.log_channel_delete = False  # bool
        self.log_channel_update = False  # bool
        self.log_member_update = False  # bool
        self.log_server_join = False  # bool
        self.log_server_remove = False  # bool
        self.log_server_update = False  # bool
        self.log_server_role_create = False  # bool
        self.log_server_role_delete = False  # bool
        self.log_server_role_update = False  # bool
        self.log_group_join = False  # bool
        self.log_group_remove = False  # bool
        self.log_error = False  # bool
        self.log_voice_state_update = False  # bool
        self.log_typing = False  # bool
        self.log_socket_raw_receive = False  # bool
        self.log_socket_raw_send = False  # bool
        self.log_resumed = False  # bool
        self.log_member_join = False  # bool
        self.pm_command_errors = False  # bool
        self.enable_error_handler = False  # bool
        self.bot_prefix = ''  # string
        self.discord_user_id = ''  # string
        self.bot_token = ''  # string
        self.disable_voice_commands = False  # bool
        self.language = 'en'  # string
        self.description = ''  # string
        self.log_server_emojis_update = False  # bool
        self.log_reaction_add = False  # bool
        self.log_reaction_remove = False  # bool
        self.log_reaction_clear = False  # bool
        self.shards = 0  # int
        self.run_on_shard = 0  # int
        self.twitch_url = ''  # string
        self.youtube_url = ''  # string
        self.default_plugins = []  # list
        self.api_token = ''  # string

        # populate the values from Credentials.json.
        self.set_values()

    def set_values(self):
        """
        sets values of the variables.
        """
        try:
            self.logging = self.getconfig(
                'logging')  # bool
        except (KeyError, TypeError):
            pass
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
            self.logkicks = self.getconfig(
                'logkicks')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_games = self.getconfig(
                'loggames')  # bool
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
            self.log_available = self.getconfig(
                'LogServerAvailable')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_unavailable = self.getconfig(
                'LogServerUnavailable')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_channel_create = self.getconfig(
                'log_channel_create')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.is_official_bot = self.getconfig(
                'Is_Official_Bot_Account')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_ytdl = self.getconfig(
                'ytdl_logs')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.pm_commands_list = self.getconfig(
                'PM_Commands')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_channel_delete = self.getconfig(
                'log_channel_delete')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_channel_update = self.getconfig(
                'log_channel_update')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_member_update = self.getconfig(
                'log_member_update')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_server_join = self.getconfig(
                'log_server_join')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_server_remove = self.getconfig(
                'log_server_remove')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_server_update = self.getconfig(
                'log_server_update')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_server_role_create = self.getconfig(
                'log_server_role_create')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_server_role_delete = self.getconfig(
                'log_server_role_delete')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_server_role_update = self.getconfig(
                'log_server_role_update')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_group_join = self.getconfig(
                'log_group_join')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_group_remove = self.getconfig(
                'log_group_remove')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_error = self.getconfig(
                'log_error')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_voice_state_update = self.getconfig(
                'log_voice_state_update')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_typing = self.getconfig(
                'log_typing')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_socket_raw_receive = self.getconfig(
                'log_socket_raw_receive')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_socket_raw_send = self.getconfig(
                'log_socket_raw_send')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_resumed = self.getconfig(
                'log_resumed')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_member_join = self.getconfig(
                'log_member_join')  # bool
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
            self.disable_voice_commands = self.getconfig(
                'disable_voice')  # bool
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
            self.log_server_emojis_update = self.getconfig(
                'log_server_emojis_update')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_reaction_add = self.getconfig(
                'log_reaction_add')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_reaction_remove = self.getconfig(
                'log_reaction_remove')  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.log_reaction_clear = self.getconfig(
                'log_reaction_clear')  # bool
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
        try:
            self.api_token = self.getconfig(
                'api_token')  # string
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
    Class that implements all of the Plugin
    Instalation / updating system for
    DecoraterBot.
    """
    def __init__(self, connector=None, loop=None):
        self.session = aiohttp.ClientSession(
            connector=connector, loop=loop)

    async def request_repo(self, pluginname):
        """
        requests the bot's plugin
        repository for an particualar plugin.
        """
        url = (
            GitHubRoute(
                "DecoraterBot-devs", "DecoraterBot-cogs",
                "master", "cogslist.json")).url
        data = await self.session.get(url)
        resp1 = await data.json(content_type='text/plain')
        version = resp1[pluginname]['version']
        url2 = resp1[pluginname]['downloadurl']
        url3 = resp1[pluginname]['textjson']
        data2 = await self.session.get(url2)
        data3 = await self.session.get(url3)
        plugincode = await data2.text()
        textjson = await data3.text()
        return PluginData(plugincode=plugincode,
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
        Also gets and sets an cached
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
            self.install_plugin(pluginname)


class ReconnectionHelper:
    """
    Helps the bot with Reconnections.
    """
    def __init__(self):
        self.reconnects = 0

    def reconnect_helper(self):
        """
        helps make the bot reconnect.
        """
        self.reconnects += 1
        if self.reconnects != 0:
            print(
                'Bot is currently reconnecting '
                'for %i times.' % self.reconnects)
        return -1


def log_writter(filename, data):
    """
    Log file writter.

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
            self.LogDataFile = open(os.path.join(
                sys.path[0], 'resources', 'ConfigData', 'LogData.json'))
            self.LogData = json.load(self.LogDataFile)
            self.LogData = self.LogData[self.bot.BotConfig.language]
            self.LogDataFile.close()
        except FileNotFoundError:
            print(str(self.bot.consoletext['Missing_JSON_Errors'][2]))
            sys.exit(2)

    def gamelog(self, ctx, desgame):
        """
        Logs Game Names.
        :param ctx: Message Context.
        :param desgame: Game Name.
        :return: Nothing.
        """
        gmelogdata01 = str(self.LogData['Game_Logs'][0]).format(
            ctx.message.author.name, desgame,
            ctx.message.author.id)
        gmelogspm = gmelogdata01
        gmelogsservers = ""
        if ctx.message.channel.is_private is False:
            gmelog001 = str(self.LogData['Game_Logs'][1]).format(
                ctx.message.author.name, desgame,
                ctx.message.author.id)
            gmelogsservers = gmelog001
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'gamelog.log')
        try:
            if ctx.message.channel.is_private is True:
                log_writter(logfile, gmelogspm)
            else:
                log_writter(logfile, gmelogsservers)
        except PermissionError:
            return

    def log_data_reader(self, entry, index, *args):
        """
        log data reader that also
        does the needed formatting.

        method specifically to fix the
        stupid Codacy duplication bug.
        """
        return str(self.LogData[entry][index]).format(
            *args)

    def logs(self, message):
        """
        Logs Sent Messages.
        :param message: Messages.
        :return: Nothing.
        """
        logs001 = str(self.LogData['On_Message_Logs'][0]).format(
            message.author.name, message.author.id, str(
                message.timestamp), message.content)
        if message.channel.is_private is False:
            logs003 = str(self.LogData['On_Message_Logs'][1]).format(
                message.author.name, message.author.id, str(
                    message.timestamp), message.channel.server.name,
                message.channel.name, message.content)
        if message.content is not None:
            logfile = os.path.join(
                sys.path[0], 'resources', 'Logs', 'log.log')
            try:
                if message.channel.is_private is True:
                    log_writter(logfile, logs001)
                else:
                    log_writter(logfile, logs003)
            except PermissionError:
                return

    def edit_logs(self, before, after):
        """
        Logs Edited Messages.
        :param before: Messages.
        :param after: Messages.
        :return: Nothing.
        """
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'edit_log.log')
        editlog001 = str(self.LogData['On_Message_Logs'][0]).format(
            before.author.name, before.author.id,
            str(before.timestamp), str(before.content),
            str(after.content))
        if before.channel.is_private is False:
            editlog003 = str(self.LogData['On_Message_Logs'][1]).format(
                before.author.name, before.author.id,
                str(before.timestamp), before.channel.server.name,
                before.channel.name, str(before.content),
                str(after.content))
        try:
            try:
                if before.content == after.content:
                    self.resolve_embed_logs(before)
                else:
                    try:
                        log_writter(logfile, editlog003)
                    except PermissionError:
                        return
            except Exception as e:
                # Empty string that is not used nor assigned
                # to a variable. (for now)
                str(e)
                if before.channel.is_private is False:
                    print(str(self.LogData['On_Edit_Logs_Error'][0]))
                else:
                    if before.content == after.content:
                        self.resolve_embed_logs(before)
                    else:
                        log_writter(logfile, editlog001)
        except PermissionError:
            return

    def delete_logs(self, message):
        """
        Logs Deleted Messages.
        :param message: Messages.
        :return: Nothing.
        """
        dellogs001 = str(self.LogData['On_Message_Logs'][0]).format(
            message.author.name, message.author.id,
            str(message.timestamp), message.content)
        dellogspm = dellogs001
        dellogsservers = None
        if message.channel.is_private is False:
            dellogs003 = str(self.LogData['On_Message_Logs'][1]).format(
                message.author.name, message.author.id,
                str(message.timestamp),
                message.channel.server.name,
                message.channel.name, message.content)
            dellogsservers = dellogs003
        if message.content is not None:
            try:
                logfile = os.path.join(
                    sys.path[0], 'resources', 'Logs', 'delete_log.log')
                if message.channel.is_private is True:
                    log_writter(logfile, dellogspm)
                else:
                    log_writter(logfile, dellogsservers)
            except PermissionError:
                return

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
            log_writter(logfile, data + "\n")
        except PermissionError:
            return

    async def send_logs(self, message):
        """
        Sends Sent Messages.
        :param message: Messages.
        :return: Nothing.
        """
        logs001 = self.log_data_reader(
            'Send_On_Message_Logs', 0,
            message.author.name, message.author.id,
            str(message.timestamp),
            message.channel.server.name, message.channel.name,
            message.content)
        sndmsglogs = logs001
        try:
            await self.bot.send_message(
                discord.Object(id='153055192873566208'), content=sndmsglogs)
        except discord.errors.NotFound:
            return
        except discord.errors.HTTPException:
            return

    async def send_edit_logs(self, before, after):
        """
        Sends Edited Messages.
        :param before: Messages.
        :param after: Messages.
        :return: Nothing.
        """
        old = str(before.content)
        new = str(after.content)
        editlog001 = str(self.LogData['Send_On_Message_Edit_Logs'][0]).format(
            before.author.name, before.author.id,
            str(before.timestamp),
            before.channel.server.name,
            before.channel.name, old, new)
        sendeditlogs = editlog001
        if before.content != after.content:
            try:
                await self.bot.send_message(
                    discord.Object(id='153055192873566208'),
                    content=sendeditlogs)
            except discord.errors.NotFound:
                return
            except discord.errors.HTTPException:
                return

    async def send_delete_logs(self, message):
        """
        Sends Deleted Messages.
        :param message: Messages.
        :return: Nothing.
        """
        dellogs001 = self.log_data_reader(
            'Send_On_Message_Delete_Logs', 0,
            message.author.name, message.author.id, str(message.timestamp),
            message.channel.server.name, message.channel.name,
            message.content)
        senddeletelogs = dellogs001
        try:
            await self.bot.send_message(
                discord.Object(id='153055192873566208'),
                content=senddeletelogs)
        except discord.errors.NotFound:
            return
        except discord.errors.HTTPException:
            return

    def on_bot_error(self, funcname, tbinfo, err):
        """
            This Function is for Internal Bot use only.
            It is for catching any Errors and writing them to a file.

            Usage
            =====
            :param funcname: Must be a string with the name of the function
            that caused a Error.
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
                    log_writter(logfile, exception_data)
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
        log_writter(logfile, ban_log_data)

    async def send_ban_logs(self, channel, member):
        """
        sends the ban log data to a specific channel.
        """
        ban_log_data = str(self.LogData['Send_Ban_Logs'][0]).format(
            member.name, member.id, member.discriminator)
        try:
            await self.bot.send_message(
                channel, content=ban_log_data)
        except discord.errors.NotFound:
            return
        except discord.errors.HTTPException:
            return

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
        log_writter(logfile, available_log_data)

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
        log_writter(logfile, unavailable_log_data)

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
        log_writter(logfile, unban_log_data)

    async def send_unban_logs(self, channel, user):
        """
        sends the unban log data to a specific channel.
        """
        unban_log_data = str(self.LogData['Send_Unban_Logs'][0]).format(
            user.name, user.id, user.discriminator)
        try:
            await self.bot.send_message(
                channel, content=unban_log_data)
        except discord.errors.NotFound:
            return
        except discord.errors.HTTPException:
            return

    def ongroupjoin(self, channel, user):
        """
        Logs group join.
        :param channel: Channels.
        :param user: Users.
        :return: Nothing.
        """
        mem_name = user.name
        mem_id = user.id
        mem_dis = user.discriminator
        mem_channel_name = channel.name
        group_join_log_data = str(self.LogData['Group_Join_Logs'][0]).format(
            mem_name, mem_id, mem_dis, mem_channel_name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'group_join.log')
        log_writter(logfile, group_join_log_data)

    def ongroupremove(self, channel, user):
        """
        Logs group remove.
        :param channel: Channels.
        :param user: Users.
        :return: Nothing.
        """
        mem_name = user.name
        mem_id = user.id
        mem_dis = user.discriminator
        mem_channel_name = channel.name
        group_remove_log_data = str(self.LogData['Group_Remove_Logs'][0]).format(
            mem_name, mem_id, mem_dis, mem_channel_name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'group_remove.log')
        log_writter(logfile, group_remove_log_data)

    def ontyping(self, channel, user, when):
        """
        Logs when a user is typing.
        :param channel: Channels.
        :param user: Users.
        :param when: Time.
        :return: Nothing.
        """
        typing_log_data = str(self.LogData['On_typing'][0]).format(
            user.name, user.id, user.discriminator, channel.name,
            str(when))
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'typing.log')
        log_writter(logfile, typing_log_data)

    def onvoicestateupdate(self, before, after):
        """
        Logs When someone updates their voice state.
        :param before: State.
        :param after: State.
        :return: Nothing.
        """
        mem_name = before.user.name
        mem_id = before.user.id
        mem_dis = before.user.discriminator
        before_channel_name = before.channel.name
        after_channel_name = after.channel.name
        voice_update_log_data = str(self.LogData['voice_update'][0]).format(
            mem_name, mem_id, mem_dis, before_channel_name,
            after_channel_name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'voice_update.log')
        log_writter(logfile, voice_update_log_data)

    def onchanneldelete(self, channel):
        """
        Logs Channel Deletion.
        :param channel: Channel.
        """
        channel_delete_log_data = str(self.LogData['channel_delete'][0]).format(
            channel.name, channel.id)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'channel_delete.log')
        log_writter(logfile, channel_delete_log_data)

    def onchannelcreate(self, channel):
        """
        Logs Channel Creation.
        :param channel: Channel.
        """
        channel_create_log_data = str(self.LogData['channel_create'][0]).format(
            channel.name, channel.id)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'channel_create.log')
        log_writter(logfile, channel_create_log_data)

    def onchannelupdate(self, before, after):
        """
        Logs Channel Updates.
        :param before: Channel before.
        :param after: Channel after.
        :return: Nothing.
        """
        # change of permittions trigger this???
        channel_update_log_data = str(self.LogData['channel_update'][0]).format(
            before.name, before.id, after.name)
        logfile = os.path.join(
            sys.path[0], '{0}{1}resources{1}Logs{1}channel_update.log')
        log_writter(logfile, channel_update_log_data)

    def onmemberupdate(self, before, after):
        """
        Logs Member Updates.
        :param before: Member before.
        :param after: Member after.
        :return: Nothing.
        """
        # change of permittions trigger this???
        member_update_log_data = str(self.LogData['member_update'][0]).format(
            before.name, before.id, after.name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'member_update.log')
        log_writter(logfile, member_update_log_data)

    def onserverjoin(self, server):
        """
        Logs server Joins.
        :param server: Server.
        :return: Nothing.
        """
        server_join_log_data = str(self.LogData['server_join'][0]).format(
            self.bot.user.name, self.bot.user.id, server.name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'server_join.log')
        log_writter(logfile, server_join_log_data)

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
        log_writter(logfile, server_remove_log_data)

    def onserverupdate(self, before, after):
        """
        Logs Server Updates.
        :param before: Server before.
        :param after: Server after.
        :return: Nothing.
        """
        server_update_log_data = str(self.LogData['server_update'][0]).format(
            before.name, before.id, after.name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'server_update.log')
        log_writter(logfile, server_update_log_data)

    def onserverrolecreate(self, role):
        """
        Logs role Creation.
        :param role: Role.
        :return: Nothing.
        """
        role_create_log_data = str(self.LogData['role_create'][0]).format(
            role.name, role.id)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'role_create.log')
        log_writter(logfile, role_create_log_data)

    def onserverroledelete(self, role):
        """
        Logs role Deletion.
        :param role: Role.
        :return: Nothing.
        """
        role_delete_log_data = str(self.LogData['role_delete'][0]).format(
            role.name, role.id)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'role_delete.log')
        log_writter(logfile, role_delete_log_data)

    def onserverroleupdate(self, before, after):
        """
        Logs Role updates.
        :param before: Role before.
        :param after: Role after.
        :return: Nothing.
        """
        # change of permittions trigger this???
        role_update_log_data = str(self.LogData['role_update'][0]).format(
            before.name, before.id, after.name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'role_update.log')
        log_writter(logfile, role_update_log_data)

    def onsocketrawreceive(self, msg):
        """
        Logs socket Raw recieves.
        :param msg: Message from socket.
        :return: Nothing.
        """
        raw_receive_log_data = str(self.LogData['raw_receive'][0]).format(
            msg)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'raw_receive.log')
        log_writter(logfile, raw_receive_log_data)

    def onsocketrawsend(self, payload):
        """
        Logs socket raw sends.
        :param payload: Payload that was sent.
        :return: Nothing.
        """
        raw_send_log_data = str(self.LogData['raw_send'][0]).format(
            payload)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'raw_send.log')
        log_writter(logfile, raw_send_log_data)

    def onresumed(self):
        """
        Logs when bot resumes.
        :return: Nothing.
        """
        resumed_log_data = str(self.LogData['resumed'][0])
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'resumed.log')
        log_writter(logfile, resumed_log_data)

    def onserveremojisupdate(self, before, after):
        """
        Logs Server emoji updates.
        :param before: Emoji before.
        :param after: Emoji after.
        :return: Nothing.
        """
        server_emojis_update_log_data = str(
            self.LogData['server_emojis_update'][0]).format(
            before.name, before.id, before.server.name,
            after.name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'server_emojis_update.log')
        log_writter(logfile, server_emojis_update_log_data)

    def onreactionadd(self, reaction, user):
        """
        Logs Reactions Added.
        :param reaction: Reaction.
        :param user: User.
        :return: Nothing.
        """
        reaction_add_log_data = str(
            self.LogData['reaction_add'][0]).format(
            user.name, user.id, user.server, reaction.emoji.name,
            reaction.emoji.id, reaction.emoji.server.name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'reaction_add.log')
        log_writter(logfile, reaction_add_log_data)

    def onreactionremove(self, reaction, user):
        """
        Logs Reaction Removals.
        :param reaction: Reaction.
        :param user: User.
        :return: Nothing.
        """
        reaction_remove_log_data = str(
            self.LogData['reaction_remove'][0]).format(
            user.name, user.id, user.server, reaction.emoji.name,
            reaction.emoji.id, reaction.emoji.server.name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'reaction_remove.log')
        log_writter(logfile, reaction_remove_log_data)

    def onreactionclear(self, message, reactions):
        """
        Logs Reaction clears.
        :param message: Message.
        :param reactions: Reactions.
        :return: Nothing.
        """
        reactionnames = [
            reaction.emoji.name for reaction in reactions]
        reactionids = [
            reaction.emoji.id for reaction in reactions]
        reactionservers = [
            reaction.emoji.server.name for reaction in reactions]
        reaction_clear_log_data = str(
            self.LogData['reaction_clear'][0]).format(
            message.author.name, message.author.id, message.author.server,
            reactionnames, reactionids, reactionservers)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'reaction_clear.log')
        log_writter(logfile, reaction_clear_log_data)

    def onmemberjoin(self, member):
        """
        Logs Member Joins.
        :param member: Member.
        :return: Nothing.
        """
        member_join_log_data = str(self.LogData['member_join'][0]).format(
            member.name, member.id, member.discriminator,
            member.server.name)
        logfile = os.path.join(
            sys.path[0], 'resources', 'Logs', 'member_join.log')
        log_writter(logfile, member_join_log_data)

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
        log_writter(logfile, kick_log_data)


config = BotCredentialsVars()


class BaseClient(commands.Bot):
    """
    Contains the stuff that gets
    bound to the Bot's main client class.
    """
    logged_in = False

    def __init__(self, **kwargs):
        self._start = time.time()
        self.BotPMError = BotPMError(self)
        self._rec = ReconnectionHelper()
        self.logged_in_ = BaseClient.logged_in
        self.somebool = False
        self.reload_normal_commands = False
        self.reload_voice_commands = False
        self.reload_reason = None
        self.initial_rejoin_voice_channel = True
        self.desmod = None
        self.desmod_new = None
        self.rejoin_after_reload = False
        self.sent_prune_error_message = False
        self.tinyurlerror = False
        self.link = None
        self.member_list = []
        self.hook_url = None
        self.payload = {}
        self.header = {}
        self.is_bot_logged_in = False
        super(BaseClient, self).__init__(**kwargs)

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
        consoledata = PluginConfigReader(file='ConsoleWindow.json')
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
        retrieves a list of all of the bot's registered commands.
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
    def ignoreslist(self):
        """
        returns the current ignores list.
        """
        try:
            ret = PluginConfigReader(file='IgnoreList.json')
        except FileNotFoundError:
            ret = None
            print(str(self.consoletext['Missing_JSON_Errors'][0]))
            sys.exit(2)
        return ret

    @property
    def credentials_check(self):
        """
        Checks if the Credentials.json
        file exists.
        """
        PATH = os.path.join(
            sys.path[0], 'resources', 'ConfigData', 'Credentials.json')
        return os.path.isfile(PATH) and os.access(PATH, os.R_OK)

    async def send(self, message=None, ctx=None,
                   *args, **kwargs):
        """
        wraps send_message.
        """
        try:
            await self.send_message(
                *args, **kwargs)
        except discord.errors.Forbidden:
            if ctx is not None:
                await self.BotPMError.resolve_send_message_error(
                    ctx)
            else:
                await self.BotPMError.resolve_send_message_error_old(
                    message)

    def load_all_default_plugins(self):
        """
        Handles loading all plugins that __init__
        used to load up.
        """
        self.remove_command("help")
        for plugins_cog in self.BotConfig.default_plugins:
            ret = self.load_plugin(plugins_cog)
            if isinstance(ret, str):
                print(ret)

    def load_bot_extension(self, extension_full_name):
        """
        loads an bot extension module.
        """
        try:
            self.load_extension(extension_full_name)
        except Exception:
            return str(traceback.format_exc())

    def unload_bot_extension(self, extension_full_name):
        """
        unloads an bot extension module.
        """
        self.unload_extension(extension_full_name)

    def load_plugin(self, plugin_name, raiseexec=True):
        """
        Loads up a plugin in the plugins folder in DecoraterBotCore.
        """
        pluginfullname = get_plugin_full_name(plugin_name)
        if pluginfullname is None:
            if raiseexec:
                raise ImportError(
                    "Plugin Name cannot be empty.")
        err = self.load_bot_extension(pluginfullname)
        if err is not None:
            return err

    def unload_plugin(self, plugin_name, raiseexec=True):
        """
        Unloads a plugin in the plugins folder in DecoraterBotCore.
        """
        pluginfullname = get_plugin_full_name(plugin_name)
        if pluginfullname is None:
            if raiseexec:
                raise CogUnloadError(
                    "Plugin Name cannot be empty.")
        self.unload_bot_extension(pluginfullname)

    def reload_plugin(self, plugin_name):
        """
        Reloads a plugin in the plugins folder in DecoraterBotCore.
        """
        self.unload_plugin(plugin_name, raiseexec=False)
        err = self.load_plugin(plugin_name)
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

    def changewindowsize(self):
        """
        Changes the Console's size.
        """
        # not used but avoids issues with this being an classmethod.
        type(self)
        consolechange.consolesize(80, 23)

    def variable(self):
        """
        Function that makes Certain things on the
        on_ready event only happen 1
        time only. (e.g. the logged in printing stuff)
        """
        if not BaseClient.logged_in:
            BaseClient.logged_in = True
            self.logged_in_ = True
