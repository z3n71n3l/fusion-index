import json

from characteristic import attributes
from service_identity import CertificateError, VerificationError
from service_identity._common import DNS_ID, verify_service_identity
from service_identity.pyopenssl import extract_ids
from toolz.dicttoolz import merge
from twisted.internet.interfaces import ISSLTransport
from twisted.web import http
from txspinneret.interfaces import ISpinneretResource
from txspinneret.resource import NotFound
from txspinneret.route import Router, Text, routedResource
from zope.interface import implementer

from fusion_index.logging import (
    LOG_LOOKUP_GET, LOG_LOOKUP_PUT, LOG_SEARCH_DELETE, LOG_SEARCH_GET,
    LOG_SEARCH_PUT)
from fusion_index.lookup import LookupEntry
from fusion_index.search import SearchClasses, SearchEntry



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
        b'lookup', Text('environment'), Text('indexType'), Text('key'))
    def lookup(self, request, params):
        return LookupResource(store=self.store, **params)


    @router.subroute(
        b'search', Text('searchClass'), Text('environment'), Text('indexType'))
    def search(self, request, params):
        try:
            params['searchClass'] = SearchClasses.lookupByValue(
                params['searchClass'])
        except ValueError:
            return NotFound()
        return SearchResource(store=self.store, params=params)



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



@routedResource
@implementer(ISpinneretResource)
@attributes(['store', 'params'])
class SearchResource(object):
    router = Router()


    @router.route(b'results', Text('searchValue'))
    def searchNoType(self, request, params):
        return SearchResultResource(
            store=self.store,
            params=merge(self.params, params, {'searchType': None}))


    @router.route(b'results', Text('searchValue'), Text('searchType'))
    def searchWithType(self, request, params):
        return SearchResultResource(
            store=self.store, params=merge(self.params, params))


    @router.route(b'entries', Text('result'), Text('searchType'))
    def searchEntry(self, request, params):
        return SearchEntryResource(
            store=self.store, params=merge(self.params, params))



@implementer(ISpinneretResource)
@attributes(['store', 'params'])
class SearchResultResource(object):
    def render_GET(self, request):
        with LOG_SEARCH_GET(**self.params) as action:
            results = self.store.transact(
                lambda: list(
                    SearchEntry.search(store=self.store, **self.params)))
            action.add_success_fields(results=results)
            request.setHeader('Content-Type', 'application/json')
            return json.dumps(results)



@implementer(ISpinneretResource)
@attributes(['store', 'params'])
class SearchEntryResource(object):
    def render_PUT(self, request):
        with LOG_SEARCH_PUT(**self.params) as action:
            searchValue = request.content.read().decode('utf-8')
            action.add_success_fields(searchValue=searchValue)
            self.store.transact(
                SearchEntry.insert, store=self.store, searchValue=searchValue,
                **self.params)
            request.setResponseCode(http.NO_CONTENT)
            return ''


    def render_DELETE(self, request):
        with LOG_SEARCH_DELETE(**self.params):
            self.store.transact(
                SearchEntry.remove, store=self.store, **self.params)
            request.setResponseCode(http.NO_CONTENT)
            return ''
