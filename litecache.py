import time
import pickle
import sqlite3
from typing import Any, Optional


# Limit what gets imported via *
__all__ = (
    '__version__',
    'LiteCache'
)


__version__ = '21.9.21.0'


ONE_DAY_SECONDS = 24 * 60 * 60
DEFAULT_TTL = ONE_DAY_SECONDS * 14


SQL_TABLE_CREATE = 'CREATE TABLE IF NOT EXISTS `litecache` (`key` TEXT UNIQUE, `value` BLOB, `last_seen` INTEGER, PRIMARY KEY(`key`)) WITHOUT ROWID;'
SQL_INDEX_CREATE = 'CREATE INDEX IF NOT EXISTS `last_seen_idx` ON `litecache` (`last_seen`);'
SQL_ADD_UPDATE_KEY = 'INSERT OR REPLACE INTO `litecache` (`key`, `value`, `last_seen`) VALUES (?, ?, ?);'
SQL_GET_KEY_SINCE = 'SELECT `value` FROM `litecache` WHERE `key` = ? AND `last_seen` >= ?;'
SQL_UPDATE_KEY_LAST_SEEN = 'UPDATE `litecache` SET `last_seen` = ? WHERE `key` = ?;'
SQL_DELETE_KEY = 'DELETE FROM `litecache` WHERE `key` = ?;'
SQL_CLEAR = 'DELETE * FROM `litecache`;'


class NotSet:
    __slots__ = ()


class LiteCache:

    # The limited set of attributes used
    __slots__ = (
        '_conn',
        'db',
        'ttl',
        'save_on_exit'
    )

    def __init__(self, cache_db: Optional[str] = None,
                 ttl: Optional[int] = DEFAULT_TTL,
                 save_on_exit: Optional[bool] = True):
        '''
        Setup a new LiteCache object
        '''

        # Get the cache file
        cache_db = cache_db or ':memory:'

        # Save the details
        self._conn = None
        self.db = cache_db
        self.ttl = ttl
        self.save_on_exit = save_on_exit

    def __repr__(self) -> str:
        return (f'LiteCache(db={self.db}, ttl={self.ttl}, '
                f'save_on_exit={self.save_on_exit})')

    def __del__(self):
        '''
        Close the DB connection cleanly, saving if desired
        '''
        if self._conn:
            if self.save_on_exit:
                self.save()
            self._conn.close()

    def __contains__(self, key: str) -> bool:
        '''
        Run the exists check
        '''
        return self.has(key)

    def __getitem__(self, key: str) -> Any:
        '''
        Get the key value from the cache
        '''

        # Attempt to get the key
        res = self.get(key)
        return res

    def __setitem__(self, key: str, value: Any):
        '''
        Set the key value from the cache
        '''

        # Attempt to set the key
        self.set(key, value)

    def _now(self) -> int:
        '''
        Return the current epoch time
        '''
        return int(time.time())

    def _since(self, ttl: Optional[int] = None) -> int:
        '''
        Return the earliest last_seen time for an entry to be returned
        '''

        # Allow ttl to be overridden
        ttl = ttl or self.ttl

        # No ttl?
        if ttl == 0:
            return 0

        # Return calculated earliest time for last_seen
        return self._now() - ttl

    @property
    def _connection(self) -> sqlite3.Connection:
        '''
        Return the SQLite connection
        '''

        # Not yet setup?
        if not self._conn:

            # Open the connection
            self._conn = sqlite3.connect(self.db, timeout=30)

            # Ensure the table and index have been created
            self._conn.execute(SQL_TABLE_CREATE)
            self._conn.execute(SQL_INDEX_CREATE)

            # Save the setup
            self.save()

        # Return the connection
        return self._conn

    def save(self) -> None:
        '''
        Commit the cache change
        '''
        self._connection.commit()

    def rollback(self) -> None:
        '''
        Rollback any changes since the last save/open
        '''
        self._connection.rollback()

    def has(self, key: str, ttl: Optional[int] = None) -> bool:
        '''
        Return True/False if a key exists
        '''

        # Query for the data
        cursor = self._connection.execute(SQL_GET_KEY_SINCE, (key, self._since(ttl)))
        row = cursor.fetchone()

        # Return whether it exists
        return row is not None

    def get(self, key: str, default: Optional[Any] = NotSet,
            ttl: Optional[int] = None) -> Any:
        '''
        Get the key value from the cache
        '''

        # Start with the default
        result = default

        # Query for the data
        cursor = self._connection.execute(SQL_GET_KEY_SINCE, (key, self._since(ttl)))
        row = cursor.fetchone()

        # Do we have a result? Load it
        if row is not None:
            result = pickle.loads(row[0])

        # Ran into our sentinel?
        if result is NotSet:
            raise KeyError(key)

        # Return the result
        return result

    def set(self, key: str, value: Any, last_seen: Optional[int] = None) -> None:
        '''
        Set the key value in the cache
        '''

        # Get the last_seen time
        last_seen = last_seen or self._now()

        # Pickle the data
        data = pickle.dumps(value)

        # Add the data to the DB
        self._connection.execute(SQL_ADD_UPDATE_KEY, (key, memoryview(data), last_seen))

    def expire(self, key: str) -> None:
        '''
        Expire the key in the cache
        '''

        # Get the new last_seen time
        last_seen = self._now() - 1

        # Set the last_seen time to now - 1
        self._connection.execute(SQL_UPDATE_KEY_LAST_SEEN, (last_seen, key))

    def delete(self, key: str) -> None:
        '''
        Delete the key in the cache
        '''

        # Delete the data from the DB
        self._connection.execute(SQL_DELETE_KEY, (key,))

    def clear(self) -> None:
        '''
        Clear the cache (DB)
        '''
        self._connection.execute(SQL_CLEAR)
