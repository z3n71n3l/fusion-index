from service_identity import CertificateError, VerificationError
from service_identity._common import DNS_ID, verify_service_identity
from service_identity.pyopenssl import extract_ids
from twisted.internet.interfaces import ISSLTransport
from txspinneret.interfaces import ISpinneretResource
from txspinneret.route import Any, Router, routedResource
from zope.interface import implementer



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



@routedResource
class IndexRouter(object):
    router = Router()

    @router.route('lookup', Any('environment'), Any('type'), Any('key'))
    def lookup(self, request, params):
        print params
        return LookupResource(params)



@implementer(ISpinneretResource)
class LookupResource(object):
    def __init__(self, params):
        self.params = params


    def render_GET(self, request):
        request.setHeader('Content-Type', 'application/octet-stream')
        return 'foo'


    def render_PUT(self, request):
        request.setResponseCode(204)
        return ''
