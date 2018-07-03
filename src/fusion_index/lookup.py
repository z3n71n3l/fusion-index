"""
Simple Axiom-based lookup index implementation.
"""
from axiom.attributes import AND, bytes, compoundIndex, text
from axiom.item import Item

from fusion_index.metrics import (
    METRIC_LOOKUP_INSERT_LATENCY, METRIC_LOOKUP_QUERY_LATENCY)



class LookupEntry(Item):
    """
    An entry in the lookup index.

    Each combination of C{(environment, indexType, key)} identifies a unique
    item in the index.
    """
    environment = text(doc="""
    The environment in which this entry exists.

    Usually something like C{u'prod'}.
    """, allowNone=False)

    indexType = text(doc="""
    The index type for this index entry.

    Usually something like C{u'idNumber'}.
    """, allowNone=False)

    key = text(doc="""
    The key for this index entry.
    """, allowNone=False)

    value = bytes(doc="""
    The value for this index entry.
    """, allowNone=False, default=b'')

    compoundIndex(environment, indexType, key)

    @classmethod
    def get(cls, store, environment, indexType, key):
        """
        Get the value of an index entry.

        @type store: L{axiom.store.Store}
        @param store: The store to use.

        @type environment: L{unicode}
        @param environment: The environment.

        @type indexType: L{unicode}
        @param indexType: The type.

        @type key: L{unicode}
        @param key: The key.

        @raises KeyError: if the entry does not exist.
        """
        with METRIC_LOOKUP_QUERY_LATENCY.labels(environment, indexType).time():
            return store.findUnique(
                cls,
                AND(cls.environment == environment,
                    cls.indexType == indexType,
                    cls.key == key)).value


    @classmethod
    def set(cls, store, environment, indexType, key, value):
        """
        Set the value of an index entry.

        If the entry already exists in the index, the previous value will be
        overwritten.

        @type store: L{axiom.store.Store}
        @param store: The store to use.

        @type environment: L{unicode}
        @param environment: The environment.

        @type indexType: L{unicode}
        @param indexType: The type.

        @type key: L{unicode}
        @param key: The key.

        @type value: L{bytes}
        @param value: The value to set.
        """
        with METRIC_LOOKUP_INSERT_LATENCY.labels(environment, indexType).time():
            item = store.findOrCreate(
                cls,
                environment=environment,
                indexType=indexType,
                key=key)
            item.value = value
