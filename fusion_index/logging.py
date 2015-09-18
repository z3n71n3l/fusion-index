from eliot import ActionType, Field, fields



LOG_START_SERVICE = ActionType(
    u'fusion_index:service:start',
    [Field(
        u'description',
        lambda d: d.asField(),
        u'The service description')],
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
