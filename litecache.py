import time
import pickle
import sqlite3


__version__ = '21.8.5.0'


ONE_DAY_SECONDS = 24 * 60 * 60
DEFAULT_TTL = ONE_DAY_SECONDS * 14


SQL_TABLE_CREATE = 'CREATE TABLE IF NOT EXISTS `litecache` (`key` TEXT UNIQUE, `value` BLOB, `last_seen` INTEGER, PRIMARY KEY(`key`)) WITHOUT ROWID;'
SQL_INDEX_CREATE = 'CREATE INDEX IF NOT EXISTS `last_seen_idx` ON `litecache` (`last_seen`);'
SQL_ADD_UPDATE_KEY = 'INSERT OR REPLACE INTO `litecache` (`key`, `value`, `last_seen`) VALUES (?, ?, ?);'
SQL_GET_KEY_SINCE = 'SELECT `value` FROM `litecache` WHERE `key` = ? AND `last_seen` >= ?;'
SQL_CLEAR = 'DELETE * FROM `litecache`;'


class NotSet:
    def __repr__(self):
        return 'NotSet'


class LiteCache(object):

    def __init__(self, cache_db=None, ttl=DEFAULT_TTL):

        # Get the cache file
        cache_db = cache_db or ':memory:'

        # Validation
        assert isinstance(cache_db, str)
        assert isinstance(ttl, int)

        # Save the details
        self._db = cache_db
        self._conn = None
        self.ttl = ttl

    def __del__(self):
        '''
        Save the changes and close the DB connection
        '''
        if self._conn:
            self.save()
            self._conn.close()

    def __contains__(self, key):
        '''
        Run the exists check
        '''
        return self.has(key)

    def _now(self):
        '''
        Return the current epoch time
        '''
        return int(time.time())

    def _since(self, ttl=None):
        '''
        Return the earliest last_seen time for an entry to be returned
        '''

        # Allow ttl to be overridden
        ttl = ttl or self.ttl

        assert isinstance(ttl, int)

        # No ttl?
        if ttl == 0:
            return 0

        # Return calculated earliest time for last_seen
        return self._now() - ttl

    @property
    def _connection(self):
        '''
        Return the SQLite connection
        '''

        # Not yet setup?
        if not self._conn:

            # Open the connection
            self._conn = sqlite3.connect(self._db, timeout=30)

            # Ensure the table and index have been created
            self._conn.execute(SQL_TABLE_CREATE)
            self._conn.execute(SQL_INDEX_CREATE)

            # Save the setup
            self.save()

        # Return the connection
        return self._conn

    def save(self):
        '''
        Commit the cache change
        '''
        self._connection.commit()

    def rollback(self):
        '''
        Rollback any changes since the last save/open
        '''
        self._connection.rollback()

    def has(self, key, ttl=None):
        '''
        Return True/False if a key exists
        '''

        # Validation
        assert isinstance(key, str)

        # Query for the data
        cursor = self._connection.execute(SQL_GET_KEY_SINCE, (key, self._since(ttl)))
        row = cursor.fetchone()

        # Return whether it exists
        return row is not None

    def get(self, key, default=NotSet, ttl=None):
        '''
        Get the key value from the cache
        '''

        # Validation
        assert isinstance(key, str)

        # Set default
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

    def set(self, key, value, last_seen=None):
        '''
        Set the key value in the cache
        '''

        # Get the last_seen time
        last_seen = last_seen or self._now()

        # Validation
        assert isinstance(key, str)
        assert isinstance(last_seen, int)

        # Pickle the data
        data = pickle.dumps(value)

        # Add the data to the DB
        self._connection.execute(SQL_ADD_UPDATE_KEY, (key, memoryview(data), last_seen))

    def clear(self):
        '''
        Clear the cache (DB)
        '''
        self._connection.execute(SQL_CLEAR)
