"""
Simple Axiom-based lookup index implementation.
"""
from axiom.attributes import AND, compoundIndex, text, bytes
from axiom.item import Item



class LookupEntry(Item):
    """
    An entry in the lookup index.

    Each combination of C{(environment, indexType, key)} identifies a unique
    item in the index.
    """
    environment = text(doc="""
    The environment in which this entry exists.

    Usually something like C{u'production'}.
    """, allowNone=False)

    indexType = text(doc="""
    The index type this entry exists.

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
        return store.findUnique(
            cls,
            AND(cls.environment == environment,
                cls.indexType == indexType,
                cls.key == key)).value


    @classmethod
    def set(cls, store, environment, indexType, key, value):
        item = store.findOrCreate(
            cls,
            environment=environment,
            indexType=indexType,
            key=key)
        item.value = value
