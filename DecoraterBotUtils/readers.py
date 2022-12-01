# coding=utf-8
"""
Readers for DecoraterBot.
"""
import json
import os
import sys

__all__ = ['BaseConfigReader', 'BotCredentialsReader']


class BaseConfigReader:
    """
    Base config Class.
    """
    def __init__(self, file=None):
        self.config = None
        self.filename = file
        self.found = False
        self.json_file = os.path.join(sys.path[0], 'resources', 'ConfigData', self.filename)
        self.load()

    def __getitem__(self, item):
        """
        Gets a JSON Config Value basted on the key provided.
        :param item: String key to the entry in the JSON file
        :return: JSON config Value.
        """
        return self.config[item]

    def __setitem__(self, key, value):
        """
        Sets a JSON Config Value basted on the key and data provided.
        :param key: String key to the entry in the JSON file
        :param value: Value to replace old value with.
        """
        self.config[key] = value

    def load(self):
        """
        Loads the JSON config Data.
        :return: List.
        """
        self.found = os.path.isfile(self.json_file) and os.access(self.json_file, os.R_OK)
        try:
            with open(self.json_file) as file:
                self.config = json.load(file)
        except(OSError, IOError):
            pass

    def save(self):
        with open(self.json_file, mode='w') as file:
            json.dump(self.config, file, indent=4, sort_keys=True)


class BotCredentialsReader(BaseConfigReader):
    """
    Class for getting the Credentials.json config Values.
    """
    def __init__(self):
        super(BotCredentialsReader, self).__init__(file='Credentials.json')

        # defaults.
        self.log_error = False  # bool
        self.pm_command_errors = False  # bool
        self.enable_error_handler = False  # bool

        # populate the values from Credentials.json.
        self.bot_prefix = self['bot_prefix']  # string
        self.bot_token = self['token']  # string
        self.language = self['language']  # string
        self.description = self['description']  # string
        self.twitch_url = self['twitch_url']  # string
        self.default_plugins = self['default_plugins']  # dict
        self.set_values()

    def set_values(self):
        """
        sets values of the variables.
        """
        try:
            self.log_error = self['log_error']  # bool
        except (KeyError, TypeError):
            pass
        try:
            self.pm_command_errors = self['pm_command_errors']  # bool
        except (KeyError, TypeError):
            pass
        self.enable_error_handler = (
            True if not self.pm_command_errors else False)  # bool
