from eliot import ActionType, Field, fields
from eliot._validation import ValidationError



def _serviceDescriptionAsField(desc):
    """
    Return a dictionary suitable for serialization as an Eliot field.

    @type desc: L{fusion_index.service._ServiceDescription}
    @param desc: The service description.
    """
    from fusion_index.service import _ServiceDescription
    if not isinstance(desc, _ServiceDescription):
        raise ValidationError(type(desc))
    return {
        'reactor': repr(desc.reactor),
        'port': desc.port,
        'interface': desc.interface,
        'options': repr(desc.options),
        'router': repr(desc.router),
        }


_SEARCH_CLASS = Field(
    u'searchClass',
    lambda c: c.value,
    u'The search class')


LOG_LOOKUP_GET = ActionType(
    u'fusion_index:lookup:get',
    fields(environment=unicode, indexType=unicode, key=unicode),
    [Field.for_types('value', [bytes, None], u'Value in the index, if any')],
    u'Retrieving a value from the lookup index')


LOG_LOOKUP_PUT = ActionType(
    u'fusion_index:lookup:put',
    fields(environment=unicode, indexType=unicode, key=unicode),
    fields(value=bytes),
    u'Storing a value in the lookup index')


_SEARCH_TYPE = Field.for_types(
    'searchType', [unicode, None], u'The search type')
LOG_SEARCH_GET = ActionType(
    u'fusion_index:search:get',
    fields(
        _SEARCH_CLASS, _SEARCH_TYPE, environment=unicode, indexType=unicode,
        searchValue=unicode),
    fields(results=list),
    u'Searching the search index')


LOG_SEARCH_PUT = ActionType(
    u'fusion_index:search:put',
    fields(
        _SEARCH_CLASS, environment=unicode, indexType=unicode,
        result=unicode, searchType=unicode),
    fields(searchValue=unicode),
    u'Inserting an entry into the search index')


LOG_SEARCH_DELETE = ActionType(
    u'fusion_index:search:delete',
    fields(
        _SEARCH_CLASS, environment=unicode, indexType=unicode,
        result=unicode, searchType=unicode),
    [],
    u'Deleting an entry from the search index')


__all__ = [
    'LOG_LOOKUP_GET', 'LOG_LOOKUP_PUT', 'LOG_SEARCH_GET', 'LOG_SEARCH_PUT',
    'LOG_SEARCH_DELETE']
