from cgi import parse_header, parse_qs

from twisted.internet.address import IPv4Address
from twisted.internet.defer import Deferred
from twisted.python.failure import Failure
from twisted.python.urlpath import URLPath
from twisted.test.proto_helpers import StringTransport
from twisted.web import http
from twisted.web.client import ResponseDone
from twisted.web.http_headers import Headers
from twisted.web.iweb import IAgent, IClientRequest, IRequest, IResponse
from twisted.web.resource import getChildForRequest
from twisted.web.server import NOT_DONE_YET
from zope.interface import implementer



@implementer(IClientRequest)
class _ResourceObjectClientRequest(object):
    """
    L{IClientRequest} for L{ResourceObjectResponse}.
    """
    def __init__(self, method, absoluteURI, headers):
        self.method = method
        self.absoluteURI = absoluteURI
        self.headers = headers



@implementer(IResponse)
class ResourceObjectResponse(object):
    """
    An L{IResponse} implementation which is generated from an L{IResource}
    provider.
    """
    phrase = b'OK'
    version = (b'HTTP', 1, 0)

    def __init__(self, request, body=None):
        self.request = _ResourceObjectClientRequest(
            method=request.method,
            absoluteURI=request.uri,
            headers=request.requestHeaders)
        self.body = body
        self.code = request.code
        self.headers = request.responseHeaders
        self.previousResponse = None
        if request.method == b'HEAD':
            length = 0
        else:
            length = len(body)
        self.length = length


    def setPreviousResponse(self, response):
        self.previousResponse = response


    def deliverBody(self, protocol):
        protocol.makeConnection(StringTransport())
        if self.body is not None:
            protocol.dataReceived(self.body)
        protocol.connectionLost(Failure(ResponseDone()))



@implementer(IRequest)
class MemoryRequest(object):
    """
    In-memory L{IRequest} for use with L{ResourceTraversalAgent}.
    """
    def __init__(self, method, uri, headers, code=http.OK, content=None,
                 client=None):
        self.method = method
        self.uri = uri
        self.requestHeaders = headers.copy()
        self.responseHeaders = Headers()
        self.code = code
        self._client = client
        self.prepath = []
        location = http.urlparse(self.uri)
        self.postpath = location.path[1:].split(b'/')
        self._finishDeferreds = []
        self.written = []
        self.finished = 0
        self.args = parse_qs(location.query, True)
        self.content = content

        contentType = self.requestHeaders.getRawHeaders(
            b'Content-Type', [None])[0]
        if method == b'POST' and contentType is not None:
            contentType = parse_header(contentType)[0]
            if contentType == b'application/x-www-form-urlencoded':
                self.args.update(parse_qs(self.content.read(), True))


    # IRequest

    def prePathURL(self):
        from twisted.web.client import URI
        location = URI.fromBytes(self.uri)
        location.path = b'/'.join(self.prepath)
        return location.toBytes()


    def URLPath(self):
        return URLPath.fromRequest(self)


    def getClient(self):
        return self._client


    def getHost(self):
        return IPv4Address(b'TCP', b'127.0.0.1', 80)


    def setResponseCode(self, code):
        self.code = code


    def setHeader(self, name, value):
        # TODO: Make this assert on write() if the header is content-length.
        self.responseHeaders.setRawHeaders(name, [value])


    def write(self, data):
        if not isinstance(data, bytes):
            raise TypeError(
                'write() only accepts bytes not {!r}'.format(type(data)))
        self.written.append(data)


    def render(self, resource):
        """
        Render the given resource as a response to this request.
        """
        result = resource.render(self)
        if result is NOT_DONE_YET:
            return
        self.write(result)
        self.finish()


    def notifyFinish(self):
        d = Deferred()
        self._finishDeferreds.append(d)
        return d


    def finish(self):
        self.finished = self.finished + 1
        observers = self._finishDeferreds
        self._finishDeferreds = []
        for obs in observers:
            obs.callback(None)


    def processingFailed(self, reason):
        observers = self._finishDeferreds
        self._finishDeferreds = []
        for obs in observers:
            obs.errback(reason)



@implementer(IAgent)
class ResourceTraversalAgent(object):
    """
    An L{IAgent} implementation that performs requests against an L{IResource}.
    """
    def __init__(self, root):
        self.root = root


    # IAgent

    def request(self, method, uri, headers=None, bodyProducer=None):
        def _finished(ignored):
            return ResourceObjectResponse(
                request=request,
                body=b''.join(request.written))

        if headers is None:
            headers = Headers()
        content = None
        if bodyProducer is not None:
            # XXX: This is seriously cheating...
            content = bodyProducer._inputFile
        request = MemoryRequest(method, uri, headers, content=content)
        d = request.notifyFinish()
        d.addCallback(_finished)
        resource = getChildForRequest(self.root, request)
        request.render(resource)
        return d
