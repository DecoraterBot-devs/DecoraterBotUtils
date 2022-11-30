# coding=utf-8
"""
Readers for DecoraterBot.
"""
import json
import os
import sys

__all__ = [
    'BaseConfigReader', 'PluginConfigReader',
    'BotCredentialsReader']


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


class PluginConfigReader(BaseConfigReader):
    """
    Class for getting plugin config values.
    """
    def __init__(self, file=None, credits=False):
        self.credits = credits
        super(PluginConfigReader, self).__init__(file=file)

    def getcredits(self, key, key2):
        """
        Gets a JSON Config Value basted on the key provided.
        :param key: String key to the entry in the JSON file.
        :param key2: String key to the entry in the JSON file.
        :return: JSON config Value.
        """
        if not self.credits:
            return None

        return self.config[key][key2]

    def setcredits(self, key, key2, data):
        """
        Sets a JSON Config Value basted on the key and data provided.
        :param key: String key to the entry in the JSON file
        :param key2: String key to the entry in the JSON file.
        :param data: Data to replace old value with.
        """
        if not self.credits:
            return None

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


class BotCredentialsReader(BaseConfigReader):
    """
    Class for getting the Credentials.json config Values.
    """
    def __init__(self):
        super(BotCredentialsReader, self).__init__(file='Credentials.json')

        # defaults.
        self.discord_logger = False  # bool
        self.asyncio_logger = False  # bool
        self.log_error = False  # bool
        self.pm_command_errors = False  # bool
        self.enable_error_handler = False  # bool
        self.bot_prefix = ''  # string
        self.bot_token = ''  # string
        self.language = 'en'  # string
        self.description = ''  # string
        self.twitch_url = ''  # string
        self.default_plugins = []  # list

        # populate the values from Credentials.json.
        self.set_values()

    def set_values(self):
        """
        sets values of the variables.
        """
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
            self.twitch_url = self.getconfig(
                'twitch_url')  # string
        except (KeyError, TypeError):
            pass
        try:
            self.default_plugins = self.getconfig(
                'default_plugins')  # dict
        except (KeyError, TypeError):
            pass
