# LiteCache

A Python SQLite-backed key-value cache with data ttl

## Example of Usage

**Import and Setup**
```python
>>> from litecache import LiteCache
>>>
>>> cache = LiteCache('test.db', ttl=600)  # ttl is seconds
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
```

**Setting a Key-Value Pair**
```python
>>> cache.set('test', {'test': 1})
>>> 'test' in cache
True
>>> cache.get('test')
{'test': 1}
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
```
