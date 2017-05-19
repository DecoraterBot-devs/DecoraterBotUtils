"""
Utils for DecoraterBot.
"""

__all__ = ['get_plugin_full_name', 'GitHubRoute',
           'PluginData', 'YTDLLogger', 'construct_reply',
           'BotPMError']


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
