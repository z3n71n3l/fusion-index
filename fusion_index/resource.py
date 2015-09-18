from characteristic import attributes
from service_identity import CertificateError, VerificationError
from service_identity._common import DNS_ID, verify_service_identity
from service_identity.pyopenssl import extract_ids
from twisted.internet.interfaces import ISSLTransport
from twisted.web import http
from txspinneret.interfaces import ISpinneretResource
from txspinneret.resource import NotFound
from txspinneret.route import Router, Text
from zope.interface import implementer

from fusion_index.logging import LOG_LOOKUP_GET, LOG_LOOKUP_PUT
from fusion_index.lookup import LookupEntry



def _verify_hostname(certificate, hostname):
    """
    Verify whether *certificate* has a valid certificate chain for *hostname*.
    """
    # Using private APIs here because service_identity doesn't *quite* have the
    # right public API.
    verify_service_identity(
        cert_patterns=extract_ids(certificate),
        obligatory_ids=[DNS_ID(hostname)],
        optional_ids=[],
    )


# XXX: Stolen from Diamond, except this version uses service_identity so it is
# a little more general. This should really go somewhere shared.
def authenticateRequest(request, hostname):
    """
    Check the certificate provided in the C{request} has the correct
    subject name.

    @param request: The request to validate.
    @type  request: L{twisted.web.http.Request}

    @param hostname: The name to match against the client certificate.
    @type  hostname: L{unicode}

    @rtype: L{bool}
    """
    transport = getattr(
        getattr(request, 'channel', None), 'transport', None)
    if ISSLTransport(transport, None) is not None:
        clientCertificate = transport.getPeerCertificate()
        try:
            _verify_hostname(clientCertificate, hostname)
        except (CertificateError, VerificationError):
            return False
        else:
            return True
    return False



@attributes(['store'])
class IndexRouter(object):
    router = Router()

    @router.route(
        'lookup', Text('environment'), Text('indexType'), Text('key'))
    def lookup(self, request, params):
        return LookupResource(store=self.store, **params)



@implementer(ISpinneretResource)
@attributes(['store', 'environment', 'indexType', 'key'])
class LookupResource(object):
    def render_GET(self, request):
        action = LOG_LOOKUP_GET(
            environment=self.environment,
            indexType=self.indexType,
            key=self.key)
        with action as a:
            try:
                result = self.store.transact(
                    LookupEntry.get,
                    store=self.store,
                    environment=self.environment,
                    indexType=self.indexType,
                    key=self.key)
            except KeyError:
                a.add_success_fields(value=None)
                return NotFound()
            else:
                request.setHeader(b'Content-Type', b'application/octet-stream')
                a.add_success_fields(value=result)
                return result


    def render_PUT(self, request):
        action = LOG_LOOKUP_PUT(
            environment=self.environment,
            indexType=self.indexType,
            key=self.key)
        with action as a:
            value = request.content.read()
            a.add_success_fields(value=value)
            self.store.transact(
                LookupEntry.set,
                store=self.store,
                environment=self.environment,
                indexType=self.indexType,
                key=self.key,
                value=value)
            request.setResponseCode(http.NO_CONTENT)
            return ''
