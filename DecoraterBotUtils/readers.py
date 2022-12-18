# coding=utf-8
"""
Readers for DecoraterBot.
"""
from os.path import exists as file_exists
import sqlite3

__all__ = ['BaseDbReader', 'DbCredentialsReader', 'DbLocalizationReader']


class BaseDbReader:
    """
    Reads values from a database.
    """
    def __init__(self, db_file: str):
        self.connection: sqlite3.Connection = sqlite3.connect(db_file)

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


class DbCredentialsReader(BaseDbReader):
    """
    Reads the bot's credentials from a database.
    """
    def __init__(self):
        # when the bot's beta db is present, use that one instead (since if it exists we are most likely in testing).
        super(DbCredentialsReader, self).__init__(
            'credentials.db' if not file_exists('credentialsbeta.db') else 'credentialsbeta.db')

    @property
    def bot_token(self) -> str:
        result: tuple | None = self.get_table_value('SELECT Token FROM Credentials WHERE id == 1')
        return result[0] if result is not None else None

    @property
    def language(self) -> str:
        result: tuple | None = self.get_table_value('SELECT Language FROM Credentials WHERE id == 1')
        return result[0] if result is not None else None

    @property
    def default_cogs(self) -> list[str] | None:
        results: list[tuple] = self.get_table_values('SELECT Cog FROM DefaultCogs')
        return [item[0] for item in results] if results is not None else None


class DbLocalizationReader(BaseDbReader):
    """
    Reads localized string values from a database.
    """
    def __init__(self):
        super(DbLocalizationReader, self).__init__('localizations.db')

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
