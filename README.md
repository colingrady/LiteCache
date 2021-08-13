# LiteCache

A Python SQLite-backed key-value cache with data TTL

## Example of Usage

**Import and Setup**
```python
>>> from litecache import LiteCache
>>>
>>> cache = LiteCache()
>>> cache
LiteCache(db=:memory:, ttl=1209600, save_on_exit:True)
>>>
>>> cache = LiteCache('test.db', ttl=600)  # ttl is seconds
>>> cache
LiteCache(db=test.db, ttl=600, save_on_exit:True)
```

**Checking for Key**
```python
>>> cache.has('test')
False
>>> 'test' in cache
False
```

**Getting a Key**
```python
>>> cache.get('test')
KeyError: 'test'
>>> cache.get('test', 'default')
'default'
>>> cache['test']
KeyError: 'test'
```

**Setting a Key-Value Pair**
```python
>>> cache.set('test', {'test': 1})
>>> 'test' in cache
True
>>> cache.get('test')
{'test': 1}
>>> cache['another'] = 100
>>> cache['another']
100
```

**Rolling Back Key Sets**
```python
>>> cache.rollback()
>>> 'test' in cache
False
```

**Saving Changes**
```python
>>> cache.set('test', {'test': 1})
>>> cache.save()
>>> cache.rollback()
>>> 'test' in cache
True
```
