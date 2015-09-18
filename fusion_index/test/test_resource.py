from collections import namedtuple
from StringIO import StringIO

from axiom.store import Store
from testtools import TestCase
from twisted.internet.interfaces import ISSLTransport
from twisted.internet.ssl import CertificateOptions, PrivateCertificate
from twisted.python.filepath import FilePath
from twisted.trial.unittest import SynchronousTestCase
from twisted.web import http
from twisted.web.client import FileBodyProducer, readBody
from zope.interface import implementer

from fusion_index.resource import IndexRouter, authenticateRequest
from fusion_index.test.util import ResourceTraversalAgent



class authenticateRequestTests(TestCase):
    """
    Tests for L{fusion_index.resource.authenticateRequest}.
    """
    def createRequest(self, certificateOptions):
        """
        Create a L{twisted.web.iweb.IRequest} with a transport that can be
        adapted to L{twisted.internet.interfaces.ISSLTransport}.

        @params certificateOptions: The SSL certificate options.
        @type   certificateOptions: L{CertificateOptions}

        @rtype: L{twisted.web.iweb.IRequest}
        """
        @implementer(ISSLTransport)
        class FakeTransport(object):
            def getPeerCertificate(self):
                return certificateOptions.certificate

        FakeRequest = namedtuple('Request', 'channel')
        FakeChannel = namedtuple('Channel', 'transport')
        channel = FakeChannel(FakeTransport())
        return FakeRequest(channel)


    def test_authenticateSucceed(self):
        """
        L{authenticateRequest} returns C{True} if the provided client
        certificate has a matching hostname.
        """
        privateCert = PrivateCertificate.loadPEM(
            FilePath(__file__).sibling(b'data').child(b'test.cert').getContent())
        self.assertEqual(
            privateCert.original.get_subject().commonName, b'localhost')

        options = CertificateOptions(
            privateKey=privateCert.privateKey.original,
            certificate=privateCert.original)
        request = self.createRequest(options)
        self.assertEqual(True, authenticateRequest(request, u'localhost'))


    def test_authenticateFailed(self):
        """
        L{authenticateRequest} returns C{False} if the provided client
        certificate doesn't have a matching hostname.
        """
        privateCert = PrivateCertificate.loadPEM(
            FilePath(__file__).sibling(b'data').child(b'test.cert').getContent())
        self.assertEqual(
            privateCert.original.get_subject().commonName, b'localhost')

        options = CertificateOptions(
            privateKey=privateCert.privateKey.original,
            certificate=privateCert.original)
        request = self.createRequest(options)
        self.assertEqual(
            False, authenticateRequest(request, u'not_localhost'))



class LookupAPITests(SynchronousTestCase):
    """
    Tests for the Lookup HTTP API.
    """
    def _resource(self):
        return IndexRouter(store=Store()).router.resource()


    def get(self, agent, path):
        """
        Simulate a GET request.
        """
        return self.successResultOf(agent.request(b'GET', path))


    def put(self, agent, path, data):
        """
        Simulate a PUT request.
        """
        return self.successResultOf(
            agent.request(
                b'PUT', path, bodyProducer=FileBodyProducer(StringIO(data))))


    def data(self, response):
        """
        Get the body from a response.
        """
        return self.successResultOf(readBody(response))


    def test_storeAndRetrieve(self):
        """
        Storing a value in the lookup index and then retrieving it results in
        the same value that was originally stored.
        """
        agent = ResourceTraversalAgent(self._resource())
        response = self.put(
            agent, b'/lookup/someenv/sometype/somekey', b'data')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = self.get(agent, b'/lookup/someenv/sometype/somekey')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(self.data(response), b'data')


    def test_retrieveMissing(self):
        """
        Trying to retrieve an item that is not present in the lookup index
        results in a 404 response.
        """
        agent = ResourceTraversalAgent(self._resource())
        response = self.get(agent, b'/lookup/someenv/sometype/somekey')
        self.assertEqual(response.code, http.NOT_FOUND)


    def test_storeTwice(self):
        """
        Storing a value in the lookup index is idempotent.
        """
        agent = ResourceTraversalAgent(self._resource())
        response = self.put(
            agent, b'/lookup/someenv/sometype/somekey', b'data')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = self.get(agent, b'/lookup/someenv/sometype/somekey')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(self.data(response), b'data')

        response = self.put(
            agent, b'/lookup/someenv/sometype/somekey', b'data')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = self.get(agent, b'/lookup/someenv/sometype/somekey')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(self.data(response), b'data')


    def test_storeOverwrite(self):
        """
        Storing a value in the lookup index overwrites any existing value.
        """
        agent = ResourceTraversalAgent(self._resource())
        response = self.put(
            agent, b'/lookup/someenv/sometype/somekey', b'data')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = self.get(agent, b'/lookup/someenv/sometype/somekey')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(self.data(response), b'data')

        response = self.put(
            agent, b'/lookup/someenv/sometype/somekey', b'newdata')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = self.get(agent, b'/lookup/someenv/sometype/somekey')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(self.data(response), b'newdata')


    def test_storeMultiple(self):
        """
        Storing values under one key does not affect different keys.
        """
        agent = ResourceTraversalAgent(self._resource())

        response = self.put(agent, b'/lookup/e1/t1/k1', b'data1')
        self.assertEqual(response.code, http.NO_CONTENT)
        response = self.put(agent, b'/lookup/e2/t2/k2', b'data2')
        self.assertEqual(response.code, http.NO_CONTENT)

        response = self.get(agent, b'/lookup/e1/t1/k1')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(self.data(response), b'data1')

        response = self.get(agent, b'/lookup/e2/t2/k2')
        self.assertEqual(response.code, http.OK)
        self.assertEqual(self.data(response), b'data2')

        self.assertEqual(
            self.get(agent, b'/lookup/e2/t1/k1').code, http.NOT_FOUND)
        self.assertEqual(
            self.get(agent, b'/lookup/e1/t2/k1').code, http.NOT_FOUND)
        self.assertEqual(
            self.get(agent, b'/lookup/e1/t1/k2').code, http.NOT_FOUND)
        self.assertEqual(
            self.get(agent, b'/lookup/e1/t2/k2').code, http.NOT_FOUND)
        self.assertEqual(
            self.get(agent, b'/lookup/e2/t1/k2').code, http.NOT_FOUND)
        self.assertEqual(
            self.get(agent, b'/lookup/e2/t2/k1').code, http.NOT_FOUND)
