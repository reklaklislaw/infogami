import config
import web

from core import *
from utils import *

# Primitive types and corresponding python types
primitive_types = {
    '/type/key': str,
    '/type/int': int,
    '/type/float': float,
    '/type/boolean': parse_boolean,
    '/type/string': str,
    '/type/text': Text,
    '/type/datetime': parse_datetime,
}

# properties present for every type of object.
COMMON_PROPERTIES = ['key', 'type', 'created', 'last_modified', 'permission', 'child_permission']

def find_type(value):
    if isinstance(value, Thing):
        return thing.type.key
    elif isinstance(value, Reference):
        return '/type/object'
    elif isinstance(value, Text):
        return '/type/text'
    elif isinstance(value, datetime.datetime):
        return '/type/datetime'
    elif isinstance(value, bool):
        return '/type/boolean'
    elif isinstance(value, int):
        return '/type/int'
    elif isinstance(value, float):
        return '/type/float'
    elif isinstance(value, dict):
        return '/type/dict'
    else:
        return '/type/string'

def parse_query(d):
    d = dict(d)
    key = d.pop('key', None)
    
    data = parse_data(d)
    if key:
        data['key'] = key
    return data

def parse_data(d):
    """
        >>> parse_data(1)
        1
        >>> text = {'type': '/type/text', 'value': 'foo'}
        >>> date= {'type': '/type/datetime', 'value': '2009-01-02T03:04:05'}
        >>> true = {'type': '/type/boolean', 'value': 'true'}
        
        >>> parse_data(text)
        <text: u'foo'>
        >>> parse_data(date)
        datetime.datetime(2009, 1, 2, 3, 4, 5)
        >>> parse_data(true)
        True
        >>> parse_data({'key': '/type/type'})
        <ref: u'/type/type'>
        
        >>> parse_data([text, date, true])
        [<text: u'foo'>, datetime.datetime(2009, 1, 2, 3, 4, 5), True]
        >>> parse_data({'a': text, 'b': date})
        {'a': <text: u'foo'>, 'b': datetime.datetime(2009, 1, 2, 3, 4, 5)}
    """
    if isinstance(d, dict):
        if 'value' in d:
            type = d.get('type', '/type/string')
            return primitive_types[type](d['value'])
        elif 'key' in d:
            return Reference(d['key'])
        else:
            return dict((k, parse_data(v)) for k, v in d.iteritems())
    elif isinstance(d, list):
        return [parse_data(v) for v in d]
    else:
        return d

def format_data(d):
    """Convert a data to a representation that can be saved.
    
        >>> format_data(1)
        1
        >>> format_data('hello')
        'hello'
        >>> format_data(Text('hello'))
        {'type': '/type/text', 'value': 'hello'}
        >>> format_data(datetime.datetime(2009, 1, 2, 3, 4, 5))
        {'type': '/type/datetime', 'value': '2009-01-02T03:04:05'}
        >>> format_data(Reference('/type/type'))
        {'key': '/type/type'}
    """
    if isinstance(d, dict):
        return dict((k, format_data(v)) for k, v in d.iteritems())
    elif isinstance(d, list):
        return [format_data(v) for v in d]
    elif isinstance(d, Text):
        return {'type': '/type/text', 'value': str(d)}
    elif isinstance(d, Reference):
        return {'key': str(d)}
    elif isinstance(d, datetime.datetime):
        return {'type': '/type/datetime', 'value': d.isoformat()}
    else:
        return d

def record_exception():
    """This function is called whenever there is any exception in Infobase.
    
    Overwrite this function if some action (like logging the exception) needs to be taken on exceptions.
    """
    import traceback
    traceback.print_exc()

def create_test_store():
    """Creates a test implementation for using in doctests.
    
    >>> store = create_test_store()
    >>> t = store.get('/type/type')
    >>> t
    <thing: '/type/type'>
    >>> t.properties[0]
    <Storage {'expected_type': <thing: '/type/string'>, 'unique': True, 'name': 'name'}>
    >>> t.properties[0].expected_type.key
    '/type/string'
    """
    store = web.storage()
    
    def add_primitive_type(key):
        add_object({
            'key': key,
            'type': {'key': '/type/type'},
            'king': 'primitive'
        })
        
    def add_object(data):
        key = data.pop('key')
        store[key] = Thing(store, key, parse_data(data))
        return store[key]
    
    add_object({
        'key': '/type/type',
        'type': {'key': '/type/type'},
        'kind': 'regular',
        'properties': [{
            'name': 'name',
            'expected_type': {'key': '/type/string'},
            'unique': True
        }, {
            'name': 'kind',
            'expected_type': {'key': '/type/string'},
            'options': ['primitive', 'regular', 'embeddable'],
            'unique': True
        }, {
            'name': 'properties',
            'expected_type': {'key': '/type/property'},
            'unique': False
        }]
    })
    
    add_object({
        'key': '/type/property',
        'type': '/type/type',
        'kind': 'embeddable',
        'properties': [{
            'name': 'name',
            'expected_type': {'key': '/type/string'},
            'unique': True
        }, {
            'name': 'expected_type',
            'expected_type': {'key': '/type/type'},
            'unique': True
        }, {
            'name': 'unique',
            'expected_type': {'key': '/type/boolean'},
            'unique': True
        }]    
    })
    
    add_primitive_type('/type/string')
    add_primitive_type('/type/int')
    add_primitive_type('/type/float')
    add_primitive_type('/type/boolean')
    add_primitive_type('/type/text')
    add_primitive_type('/type/datetime')
    return store

class LazyThing:
    def __init__(self, store, key, json):
        self.__dict__['_key'] = key
        self.__dict__['_store'] = store
        self.__dict__['_json'] = json
        self.__dict__['_thing'] = None
        
    def _get(self):
        if self._thing is None:
            self._thing = Thing.from_json(self._store, self._key, self._json)
        return self._thing
        
    def __getattr__(self, key):
        return getattr(self._get(), key)
        
    def __json__(self):
        return self._json
        
    def __repr__(self):
        return "<LazyThing: %s>" % repr(self._key)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
