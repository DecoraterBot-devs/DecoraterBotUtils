# coding=utf-8
"""
Readers for DecoraterBot.
"""
import json
import os
import sys
import sqlite3

import aiofiles

__all__ = ['BaseConfigReader', 'BotCredentialsReader',
           'DbLocalizationReader']


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
        self.bot_token: str = self['token']  # string
        self.language: str = self['language']  # string
        self.default_plugins: dict = self['default_plugins']  # dict


class BaseDbReader:
    """
    Reads values from a database.
    """
    def __init__(self):
        self.connection: sqlite3.Connection = sqlite3.connect('localizations.db')

    def __del__(self):
        self.close()

    def get_table_value(self, query: str) -> tuple | None:
        """
        Runs a query and returns a tuple of the results.
        """
        cursor: sqlite3.Cursor = self.connection.cursor()
        cursor.execute(query)
        result: tuple | None = cursor.fetchone()
        cursor.close()
        return result

    def get_table_values(self, query: str) -> list[tuple] | None:
        """
        Runs a query and returns a dictionary of the rows with the results.
        """
        cursor: sqlite3.Cursor = self.connection.cursor()
        cursor.execute(query)
        result: list[tuple] | None = cursor.fetchall()
        cursor.close()
        return result

    def close(self):
        self.connection.close()


class DbLocalizationReader(BaseDbReader):
    """
    Reads localized string values from a database.
    """

    def get_locale_id(self, locale: str) -> int:
        result: int = self.get_table_value(
            f'SELECT BaseLocalizationId FROM Localizations WHERE localization == \'{locale}\'')[0]
        return result

    def get_str(self, str_id: int, locale: str) -> str:
        """
        Gets a localized string from the database using a specific id and a specified locale.
        """
        locale_id = self.get_locale_id(locale)
        results: tuple | None = self.get_table_value(
            f'SELECT string FROM StringTable WHERE id == \'{str_id}\' AND localizationId == {locale_id}')
        # if results is None, fall back to the english version of the string.
        if results is None:
            results = self.get_table_value(
                f'SELECT string FROM StringTable WHERE id == \'{str_id}\' AND localizationId == 0')
        result: str = results[0]
        return result
