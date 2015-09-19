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


_SERVICE_DESCRIPTION = Field(
    u'description',
    _serviceDescriptionAsField,
    u'The service description')


LOG_START_SERVICE = ActionType(
    u'fusion_index:service:start',
    [_SERVICE_DESCRIPTION],
    [],
    u'Indexing service is starting')


LOG_STOP_SERVICE = ActionType(
    u'fusion_index:service:stop', [], [], u'Indexing service is stopping')


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


__all__ = [
    'LOG_START_SERVICE', 'LOG_STOP_SERVICE', 'LOG_LOOKUP_GET',
    'LOG_LOOKUP_PUT']
