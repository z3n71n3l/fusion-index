import json
from StringIO import StringIO

from axiom.store import Store
from eliot.testing import assertContainsFields, capture_logging, LoggedAction
from treq.testing import RequestTraversalAgent
from twisted.trial.unittest import SynchronousTestCase
from twisted.web import http
from twisted.web.client import FileBodyProducer, readBody

from fusion_index.logging import (
    LOG_LOOKUP_GET, LOG_LOOKUP_PUT, LOG_SEARCH_DELETE, LOG_SEARCH_GET,
    LOG_SEARCH_PUT)
from fusion_index.resource import IndexRouter
from fusion_index.search import SearchClasses



def GET(self, agent, path):
    """
    Simulate a GET request.
    """
    return self.successResultOf(
        agent.request(b'GET', b'https://example.com' + path))


def PUT(self, agent, path, data):
    """
    Simulate a PUT request.
    """
    return self.successResultOf(
        agent.request(
            b'PUT',
            b'https://example.com' + path,
            bodyProducer=FileBodyProducer(StringIO(data))))


def DELETE(self, agent, path):
    """
    Simulate a DELETE request.
    """
    return self.successResultOf(
        agent.request(b'DELETE', b'https://example.com' + path))


def data(self, response):
    """
    Get the body from a response.
    """
    return self.successResultOf(readBody(response))



class LookupAPITests(SynchronousTestCase):
    """
    Tests for the Lookup HTTP API.
    """
    def _resource(self):
        return IndexRouter(store=Store()).router.resource()


    def assertLookupLogging(self, logger):
        """
        The put action is logged, followed by the get action.
        """
        [put] = LoggedAction.of_type(logger.messages, LOG_LOOKUP_PUT)
        assertContainsFields(
            self, put.start_message,
            {'environment': u'someenv',
             'indexType': u'sometype',
             'key': u'somekey'})
        assertContainsFields(self, put.end_message, {'value': b'data'})
        self.assertTrue(put.succeeded)

        [get] = LoggedAction.of_type(logger.messages, LOG_LOOKUP_GET)
        assertContainsFields(
            self, get.start_message,
            {'environment': u'someenv',
             'indexType': u'sometype',
             'key': u'somekey'})
        assertContainsFields(self, get.end_message, {'value': b'data'})
        self.assertTrue(get.succeeded)


    @capture_logging(assertLookupLogging)
    def test_storeAndRetrieve(self, logger):
        """
        Storing a value in the lookup index and then retrieving it results in
        the same value that was originally stored.
        """
        agent = RequestTraversalAgent(self._resource())
        response = PUT(
            self, agent, b'/lookup/someenv/sometype/somekey', b'data')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = GET(self, agent, b'/lookup/someenv/sometype/somekey')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(data(self, response), b'data')


    def assertMissingGetLogging(self, logger):
        """
        When a I{GET} results in I{Not found}, a successful action is logged
        with a C{None} value.
        """
        [get] = LoggedAction.of_type(logger.messages, LOG_LOOKUP_GET)
        assertContainsFields(
            self, get.start_message,
            {'environment': u'someenv',
             'indexType': u'sometype',
             'key': u'somekey'})
        assertContainsFields(self, get.end_message, {'value': None})
        self.assertTrue(get.succeeded)


    @capture_logging(assertMissingGetLogging)
    def test_retrieveMissing(self, logger):
        """
        Trying to retrieve an item that is not present in the lookup index
        results in a 404 response.
        """
        agent = RequestTraversalAgent(self._resource())
        response = GET(self, agent, b'/lookup/someenv/sometype/somekey')
        self.assertEqual(response.code, http.NOT_FOUND)


    def test_storeTwice(self):
        """
        Storing a value in the lookup index is idempotent.
        """
        agent = RequestTraversalAgent(self._resource())
        response = PUT(
            self, agent, b'/lookup/someenv/sometype/somekey', b'data')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = GET(self, agent, b'/lookup/someenv/sometype/somekey')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(data(self, response), b'data')

        response = PUT(
            self, agent, b'/lookup/someenv/sometype/somekey', b'data')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = GET(self, agent, b'/lookup/someenv/sometype/somekey')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(data(self, response), b'data')


    def test_storeOverwrite(self):
        """
        Storing a value in the lookup index overwrites any existing value.
        """
        agent = RequestTraversalAgent(self._resource())
        response = PUT(
            self, agent, b'/lookup/someenv/sometype/somekey', b'data')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = GET(self, agent, b'/lookup/someenv/sometype/somekey')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(data(self, response), b'data')

        response = PUT(
            self, agent, b'/lookup/someenv/sometype/somekey', b'newdata')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = GET(self, agent, b'/lookup/someenv/sometype/somekey')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(data(self, response), b'newdata')


    def test_storeMultiple(self):
        """
        Storing values under one key does not affect different keys.
        """
        agent = RequestTraversalAgent(self._resource())

        response = PUT(self, agent, b'/lookup/e1/t1/k1', b'data1')
        self.assertEqual(response.code, http.NO_CONTENT)
        response = PUT(self, agent, b'/lookup/e2/t2/k2', b'data2')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = GET(self, agent, b'/lookup/e1/t1/k1')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(data(self, response), b'data1')

        response = GET(self, agent, b'/lookup/e2/t2/k2')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(data(self, response), b'data2')

        self.assertEqual(
            GET(self, agent, b'/lookup/e2/t1/k1').code, http.NOT_FOUND)
        self.assertEqual(
            GET(self, agent, b'/lookup/e1/t2/k1').code, http.NOT_FOUND)
        self.assertEqual(
            GET(self, agent, b'/lookup/e1/t1/k2').code, http.NOT_FOUND)
        self.assertEqual(
            GET(self, agent, b'/lookup/e1/t2/k2').code, http.NOT_FOUND)
        self.assertEqual(
            GET(self, agent, b'/lookup/e2/t1/k2').code, http.NOT_FOUND)
        self.assertEqual(
            GET(self, agent, b'/lookup/e2/t2/k1').code, http.NOT_FOUND)



class SearchAPITests(SynchronousTestCase):
    """
    Tests for the Search HTTP API.
    """
    def _resource(self):
        return IndexRouter(store=Store()).router.resource()


    def assertSearchLogging(self, logger):
        """
        The put action is logged, followed by the get action, followed by the
        delete, followed by the second get.
        """
        [put] = LoggedAction.of_type(logger.messages, LOG_SEARCH_PUT)
        assertContainsFields(
            self, put.start_message,
            {'searchClass': SearchClasses.EXACT,
             'environment': u'someenv',
             'indexType': u'someindex',
             'result': u'result',
             'searchType': u'type'})
        assertContainsFields(
            self, put.end_message,
            {'searchValue': u'somevalue'})
        self.assertTrue(put.succeeded)

        [delete] = LoggedAction.of_type(logger.messages, LOG_SEARCH_DELETE)
        assertContainsFields(
            self, delete.start_message,
            {'searchClass': SearchClasses.EXACT,
             'environment': u'someenv',
             'indexType': u'someindex',
             'result': u'result',
             'searchType': u'type'})
        self.assertTrue(delete.succeeded)

        [get1, get2] = LoggedAction.of_type(logger.messages, LOG_SEARCH_GET)
        assertContainsFields(
            self, get1.start_message,
            {'searchClass': SearchClasses.EXACT,
             'environment': u'someenv',
             'indexType': u'someindex',
             'searchValue': u'somevalue',
             'searchType': None})
        assertContainsFields(self, get1.end_message, {'results': [u'result']})
        self.assertTrue(get1.succeeded)
        assertContainsFields(
            self, get2.start_message,
            {'searchClass': SearchClasses.EXACT,
             'environment': u'someenv',
             'indexType': u'someindex',
             'searchValue': u'somevalue',
             'searchType': None})
        assertContainsFields(self, get2.end_message, {'results': []})
        self.assertTrue(get2.succeeded)


    @capture_logging(assertSearchLogging)
    def test_storeRetrieveDelete(self, logger):
        """
        Storing a value in the search index and then retrieving it results in
        the same value that was originally stored. After deleting it, the entry
        is no longer returned by a search.
        """
        agent = RequestTraversalAgent(self._resource())
        response = PUT(
            self,
            agent,
            b'/search/exact/someenv/someindex/entries/result/type',
            b'somevalue')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = GET(
            self, agent, b'/search/exact/someenv/someindex/results/somevalue')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(
            response.headers.getRawHeaders('Content-Type'),
            ['application/json'])
        self.assertEqual(
            json.loads(data(self, response)),
            [u'result'])

        response = DELETE(
            self,
            agent,
            b'/search/exact/someenv/someindex/entries/result/type')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = GET(
            self, agent, b'/search/exact/someenv/someindex/results/somevalue')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(
            response.headers.getRawHeaders('Content-Type'),
            ['application/json'])
        self.assertEqual(
            json.loads(data(self, response)),
            [])


    def test_storeDeleteMissing(self):
        """
        Deleting a value that does not exist in the search index succeeds
        without doing anything.
        """
        agent = RequestTraversalAgent(self._resource())
        response = DELETE(
            self,
            agent,
            b'/search/exact/someenv/someindex/entries/result/type')
        self.assertEqual(response.code, http.NO_CONTENT)


    def test_storeMultiple(self):
        """
        Inserting two entries with the same value but different search types
        results in both being returned for a search without search type, but
        only the respective entry for a search with search type.
        """
        agent = RequestTraversalAgent(self._resource())
        response = PUT(
            self, agent, b'/search/exact/e/i/entries/result1/type1', b'value')
        self.assertEqual(response.code, http.NO_CONTENT)
        response = PUT(
            self, agent, b'/search/exact/e/i/entries/result2/type2', b'value')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = GET(
            self, agent, b'/search/exact/e/i/results/value')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(
            response.headers.getRawHeaders('Content-Type'),
            ['application/json'])
        self.assertEqual(
            set(json.loads(data(self, response))),
            {'result1', 'result2'})

        response = GET(
            self, agent, b'/search/exact/e/i/results/value/type2')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(
            response.headers.getRawHeaders('Content-Type'),
            ['application/json'])
        self.assertEqual(
            json.loads(data(self, response)),
            ['result2'])


    def test_insertTwice(self):
        """
        Inserting the same entry twice has no effect on the second insert.
        """
        agent = RequestTraversalAgent(self._resource())
        response = PUT(
            self, agent, b'/search/exact/e/i/entries/result/type', b'value')
        self.assertEqual(response.code, http.NO_CONTENT)
        response = PUT(
            self, agent, b'/search/exact/e/i/entries/result/type', b'value')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = GET(
            self, agent, b'/search/exact/e/i/results/value')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(
            response.headers.getRawHeaders('Content-Type'),
            ['application/json'])
        self.assertEqual(
            set(json.loads(data(self, response))),
            {'result'})


    def assertSearchLogging2(self, logger):
        """
        The two put actions are logged, followed by the two get actions.
        """
        [put1, put2] = LoggedAction.of_type(logger.messages, LOG_SEARCH_PUT)
        assertContainsFields(
            self, put1.start_message,
            {'searchClass': SearchClasses.EXACT,
             'environment': u'e',
             'indexType': u'i',
             'searchType': u'type1',
             'result': u'result1'})
        assertContainsFields(
            self, put1.end_message,
            {'searchValue': u'value'})
        self.assertTrue(put1.succeeded)
        assertContainsFields(
            self, put2.start_message,
            {'searchClass': SearchClasses.PREFIX,
             'environment': u'e',
             'indexType': u'i',
             'searchType': u'type2',
             'result': u'result2'})
        assertContainsFields(
            self, put2.end_message,
            {'searchValue': u'value'})
        self.assertTrue(put2.succeeded)

        [get1, get2] = LoggedAction.of_type(logger.messages, LOG_SEARCH_GET)
        assertContainsFields(
            self, get1.start_message,
            {'searchClass': SearchClasses.EXACT,
             'environment': u'e',
             'indexType': u'i',
             'searchValue': u'value',
             'searchType': None})
        assertContainsFields(self, get1.end_message, {'results': [u'result1']})
        self.assertTrue(get1.succeeded)
        assertContainsFields(
            self, get2.start_message,
            {'searchClass': SearchClasses.PREFIX,
             'environment': u'e',
             'indexType': u'i',
             'searchValue': u'va',
             'searchType': None})
        assertContainsFields(self, get2.end_message, {'results': [u'result2']})
        self.assertTrue(get2.succeeded)


    @capture_logging(assertSearchLogging2)
    def test_exactAndPrefix(self, logger):
        """
        Searching the exact index only finds entries inserted into the exact
        index, and likewise for the prefix index.
        """
        agent = RequestTraversalAgent(self._resource())
        response = PUT(
            self, agent, b'/search/exact/e/i/entries/result1/type1', b'value')
        self.assertEqual(response.code, http.NO_CONTENT)
        response = PUT(
            self, agent, b'/search/prefix/e/i/entries/result2/type2', b'value')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = GET(
            self, agent, b'/search/exact/e/i/results/value')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(
            response.headers.getRawHeaders('Content-Type'),
            ['application/json'])
        self.assertEqual(
            json.loads(data(self, response)),
            ['result1'])

        response = GET(
            self, agent, b'/search/prefix/e/i/results/va')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(
            response.headers.getRawHeaders('Content-Type'),
            ['application/json'])
        self.assertEqual(
            json.loads(data(self, response)),
            ['result2'])


    def test_invalidSearchClass(self):
        """
        Paths with an invalid search class result in a Not Found response.
        """
        agent = RequestTraversalAgent(self._resource())
        response = GET(
            self, agent, b'/search/invalid/e/i/value/')
        self.assertEqual(response.code, http.NOT_FOUND)
