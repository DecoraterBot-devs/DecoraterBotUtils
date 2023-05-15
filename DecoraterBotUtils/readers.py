# coding=utf-8
"""
Readers for DecoraterBot.
"""
from os.path import exists as file_exists
import sqlite3

import asqlite


__all__ = ['BaseDbReader', 'DbCredentialsReader', 'DbLocalizationReader']


class BaseDbReader:
    """
    Reads values from a database.
    """

    async def __aenter__(self):
        self.connection: asqlite.Connection = await asqlite.connect(self.get_db_file())
        return self

    async def __aexit__(self, *exc):
        await self.connection.close()

    def get_db_file(self) -> str:
        return ''

    async def get_table_value_async(self, query: str) -> sqlite3.Row | None:
        """
        Runs a query and returns a tuple of the results.
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute(query)
            result: sqlite3.Row | None = await cursor.fetchone()
        return result

    async def get_table_values_async(self, query: str) -> list[sqlite3.Row] | None:
        """
        Runs a query and returns a dictionary of the rows with the results.
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute(query)
            result: list[sqlite3.Row] | None = await cursor.fetchall()
        return result


class DbCredentialsReader(BaseDbReader):
    """
    Reads the bot's credentials from a database.
    """

    def get_db_file(self) -> str:
        # when the bot's beta db is present, use that one instead (since if it exists we are most likely in testing).
        return 'credentialsbeta.db' if file_exists('credentialsbeta.db') else 'credentials.db'

    @property
    async def bot_token(self) -> str:
        result: sqlite3.Row | None = await self.get_table_value_async('SELECT Token FROM Credentials WHERE id == 1')
        return result['Token'] if result is not None else None

    @property
    async def language(self) -> str:
        result: sqlite3.Row | None = await self.get_table_value_async('SELECT Language FROM Credentials WHERE id == 1')
        return result['Language'] if result is not None else None

    @property
    async def default_cogs(self) -> list[str] | None:
        results: list[sqlite3.Row] | None = await self.get_table_values_async('SELECT Cog FROM DefaultCogs')
        return [item['Cog'] for item in results] if results is not None else None


class DbLocalizationReader(BaseDbReader):
    """
    Reads localized string values from a database.
    """

    def get_db_file(self) -> str:
        return 'localizations.db'

    async def _get_locale_id(self, locale: str) -> int:
        results: sqlite3.Row = await self.get_table_value_async(
            f'SELECT BaseLocalizationId FROM Localizations WHERE localization == \'{locale}\'')
        try:
            result: int = results['BaseLocalizationId']
            return result
        except TypeError:
            print(f'Localization for the \'{locale}\' is missing in the database.')
            # fall back to the english version of the string.
            return 0

    async def get_str_async(self, str_id: int, locale: str) -> str | None:
        """
        Gets a localized string from the database using a specific id and a specified locale.
        """
        locale_id = await self._get_locale_id(locale)
        results: sqlite3.Row | None = await self.get_table_value_async(
            f'SELECT string FROM StringTable WHERE id == \'{str_id}\' AND localizationId == {locale_id}')
        # if results is None, fall back to the english version of the string.
        if results is None:
            results = await self.get_table_value_async(
                f'SELECT string FROM StringTable WHERE id == \'{str_id}\' AND localizationId == 0')
        try:
            result: str = results['string']
            return result
        except TypeError:
            return None
