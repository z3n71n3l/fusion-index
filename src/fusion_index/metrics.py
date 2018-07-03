from prometheus_client import Counter, Histogram



METRIC_LOOKUP_QUERY_LATENCY = Histogram(
    'lookup_query_latency_seconds',
    'Lookup query latency in seconds',
    ['environment', 'indexType'])

METRIC_LOOKUP_INSERT_LATENCY = Histogram(
    'lookup_insert_latency_seconds',
    'Lookup insertion latency in seconds',
    ['environment', 'indexType'])

METRIC_SEARCH_QUERY_LATENCY = Histogram(
    'search_query_latency_seconds',
    'Search query latency in seconds',
    ['searchClass', 'environment', 'indexType'])

METRIC_SEARCH_INSERT_LATENCY = Histogram(
    'search_insert_latency_seconds',
    'Search insertion latency in seconds',
    ['searchClass', 'environment', 'indexType'])

METRIC_SEARCH_DELETE_LATENCY = Histogram(
    'search_delete_latency_seconds',
    'Search deletion latency in seconds',
    ['searchClass', 'environment', 'indexType'])

METRIC_SEARCH_REJECTED = Counter(
    'search_rejected_count',
    'Searches rejected due to being too general',
    ['searchClass', 'environment', 'indexType'])
