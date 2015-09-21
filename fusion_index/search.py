"""
Simple Axiom-based search implementation.

This primarily differs from the "lookup" index in L{fusion_index.lookup} by not
being 1:1; a particular search key can map to multiple values. In addition,
this implementation has both exact matching and prefix matching (in different
indexes).
"""
from axiom.attributes import AND, compoundIndex, text
from axiom.item import Item
from twisted.python.constants import ValueConstant, Values



class SearchClasses(Values):
    EXACT = ValueConstant(u'exact')
    PREFIX = ValueConstant(u'prefix')



class SearchEntry(Item):
    """
    An entry in the search index.

    Each combination of the attributes on this item. The primary querying
    operation supported is matching on the C{(searchClass, environment,
    indexType, searchValue)} portion, with exact or prefix matching on the
    I{searchValue} component depending on the I{searchClass} component.

    "Separate" indexes are keyed by C{(searchClass, environment, indexType)}.
    I{environment} and I{indexType} are separated as a convenience to clients
    as separating them allows for easily differentiating between application
    environments at a global configuration level, as well as between different
    indexes within the application.
    """
    searchClass = text(doc="""
    The search "class" that this entry belongs to; must be a value from
    L{SearchClasses}.
    """, allowNone=False)

    environment = text(doc="""
    The environment in which this entry exists.

    Usually something like C{u'production'}.
    """, allowNone=False)

    indexType = text(doc="""
    The index type for this index entry.

    Usually something like C{u'idNumber'}.
    """, allowNone=False)

    searchValue = text(doc="""
    The search value that this entry should match.
    """, allowNone=False)

    searchType = text(doc="""
    The search type that this entry should match.
    """, allowNone=False)

    result = text(doc="""
    The search result that should be returned when this entry matches.
    """, allowNone=False)

    compoundIndex(
        searchClass, environment, indexType, searchValue, searchType, result)


    @classmethod
    def search(cls, store, searchClass, environment, indexType, searchValue,
               searchType=None):
        """
        Return entries matching the given search.

        @see: L{SearchEntry}
        """
        criteria = [
            SearchEntry.searchClass == searchClass.value,
            SearchEntry.environment == environment,
            SearchEntry.indexType == indexType,
            ]
        if searchClass == SearchClasses.EXACT:
            criteria.append(SearchEntry.searchValue == searchValue)
        elif searchClass == SearchClasses.PREFIX:
            criteria.append(SearchEntry.searchValue.startswith(searchValue))
        else:
            raise RuntimeError(
                'Invalid search class: {!r}'.format(searchClass))
        if searchType is not None:
            criteria.append(SearchEntry.searchType == searchType)
        return store.query(SearchEntry, AND(*criteria)).getColumn('result')


    @classmethod
    def insert(cls, store, searchClass, environment, indexType, searchValue,
               searchType, result):
        """
        Insert an entry into the search index.

        @see: L{SearchEntry}
        """
        store.findOrCreate(
            SearchEntry, searchClass=searchClass.value,
            environment=environment, indexType=indexType,
            searchValue=searchValue, searchType=searchType, result=result)


    @classmethod
    def remove(cls, store, searchClass, environment, indexType, searchValue,
               searchType, result):
        """
        Remove an entry from the search index.

        @see: L{SearchEntry}
        """
        store.query(
            SearchEntry,
            AND(SearchEntry.searchClass == searchClass.value,
                SearchEntry.environment == environment,
                SearchEntry.indexType == indexType,
                SearchEntry.searchValue == searchValue,
                SearchEntry.searchType == searchType,
                SearchEntry.result == result)).deleteFromStore()
