from collections import namedtuple

from testtools import TestCase

from fusion_index.resource import authenticateRequest
from twisted.internet.interfaces import ISSLTransport
from twisted.internet.ssl import CertificateOptions, PrivateCertificate
from twisted.python.filepath import FilePath
from zope.interface import implementer



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
        certificate has a matching Common Name.
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
        certificate doesn't have a matching Common Name.
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
