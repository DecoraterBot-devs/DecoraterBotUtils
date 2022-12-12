# coding=utf-8
"""
Readers for DecoraterBot.
"""
import json
import os
import sys

import aiofiles

__all__ = ['BaseConfigReader', 'BotCredentialsReader']


class BaseConfigReader:
    """
    Base config Class.
    """
    def __init__(self, file=None):
        self.config = None
        self.filename = file
        self.json_file = os.path.join(sys.path[0], 'resources', 'ConfigData', self.filename)
        self.found = os.path.isfile(self.json_file) and os.access(self.json_file, os.R_OK)

    async def __aenter__(self):
        await self.load_async()
        return self

    async def __aexit__(self, *exc):
        await self.save_async()
        return

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, *exc):
        self.save()
        return

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

    def __del__(self):
        self.config = None
        self.filename = None
        self.json_file = None
        self.found = None

    def load(self):
        """
        Loads the JSON config Data.
        :return: List.
        """
        try:
            with open(self.json_file) as file:
                self.config = json.load(file)
        except(OSError, IOError):
            pass

    async def load_async(self):
        """
        Loads the JSON config Data.
        :return: List.
        """
        try:
            async with aiofiles.open(self.json_file) as file:
                self.config = json.loads(await file.read())
        except(OSError, IOError):
            pass

    def save(self):
        with open(self.json_file, mode='w') as file:
            json.dump(self.config, file, indent=4, sort_keys=True)

    async def save_async(self):
        async with aiofiles.open(self.json_file, mode='w') as file:
            await file.write(json.dumps(self.config, indent=4, sort_keys=True))


class BotCredentialsReader(BaseConfigReader):
    """
    Class for getting the Credentials.json config Values.
    """
    def __init__(self):
        super(BotCredentialsReader, self).__init__(file='Credentials.json')

        # manually run the load function so that way the json file
        # gets loaded properly for the credential values to be properly set through this.
        self.load()

        # populate the values from Credentials.json.
        self.bot_prefix = self['bot_prefix']  # string
        self.bot_token = self['token']  # string
        self.language = self['language']  # string
        self.default_plugins = self['default_plugins']  # dict
