from axiom import attributes as a
from axiom.dependency import installOn
from axiom.item import Item
from axiom.scripts.axiomatic import AxiomaticCommand
from characteristic import attributes
from eliot.twisted import DeferredContext
from fusion_util.cert import chainCerts
from twisted.application.internet import StreamServerEndpointService
from twisted.application.service import IService, Service
from twisted.internet import reactor
from twisted.internet.endpoints import SSL4ServerEndpoint
from twisted.internet.ssl import (
    Certificate, CertificateOptions, PrivateCertificate)
from twisted.python.filepath import FilePath
from twisted.web.server import Site

from fusion_index.logging import LOG_START_SERVICE, LOG_STOP_SERVICE
from fusion_index.resource import IndexRouter



@attributes(['reactor', 'port', 'interface', 'options', 'router'])
class _ServiceDescription(object):
    """
    Description of the underlying service.
    """
    def makeService(self):
        """
        Construct a service from this description.
        """
        factory = Site(self.router.router.resource())
        return StreamServerEndpointService(
            SSL4ServerEndpoint(
                self.reactor, self.port, self.options,
                interface=self.interface),
            factory)


    def asField(self):
        """
        Return a dictionary suitable for serialization as an Eliot field.
        """
        return {
            'reactor': repr(self.reactor),
            'port': self.port,
            'interface': self.interface,
            'options': repr(self.options),
            'router': repr(self.router),
            }



class FusionIndexService(Item, Service):
    """
    Service powerup for exposing the index service over HTTPS.
    """
    powerupInterfaces = [IService]
    interface = a.bytes(default='', allowNone=False)
    port = a.integer(default=8443, allowNone=False)
    caPath = a.text(allowNone=False)
    certPath = a.text(allowNone=False)

    _endpointService = a.inmemory()
    parent = a.inmemory()
    name = a.inmemory()
    running = a.inmemory()

    def activate(self):
        self.parent = None
        self.name = None
        self.running = False


    def _serviceDescription(self):
        """
        Produce a description of the service we should start.
        """
        ca = Certificate.loadPEM(
            FilePath(self.caPath.encode('utf-8')).getContent())
        certBytes = FilePath(self.certPath.encode('utf-8')).getContent()
        cert = PrivateCertificate.loadPEM(certBytes)
        # Can't use PrivateCertificate.options until Twisted #6361 is fixed
        options = CertificateOptions(
            privateKey=cert.privateKey.original,
            certificate=cert.original,
            trustRoot=ca,
            extraCertChain=chainCerts(certBytes))
        router = IndexRouter(store=self.store)
        return _ServiceDescription(
            reactor=reactor, port=self.port, interface=self.interface,
            options=options, router=router)


    # IService

    def startService(self):
        desc = self._serviceDescription()
        with LOG_START_SERVICE(description=desc):
            self.running = True
            self._endpointService = desc.makeService()
            self._endpointService.startService()


    def stopService(self):
        action = LOG_STOP_SERVICE()
        with action.context():
            self.running = False
            d = DeferredContext(self._endpointService.stopService())
            d.addActionFinish()
            return d.result



class FusionIndexConfiguration(AxiomaticCommand):
    """
    Axiomatic subcommand plugin for inspecting and modifying the index service
    configuration.
    """
    name = 'fusion-index'
    description = 'Fusion index service configuration'

    optFlags = [
        ('create', None, 'Allow creating the service if it does not already exist'),
        ]

    optParameters = [
        ('interface', 'i', None, 'Interface to listen on'),
        ('port', 'p', None, 'Port to listen on'),
        ('ca', None, None, 'Path to CA certificate for authentication'),
        ('cert', None, None, 'Path to server certificate/key'),
        ]


    def _opts(self):
        """
        Collect all service options.
        """
        o = {}
        if self['interface'] is not None:
            o['interface'] = self['interface']
        if self['port'] is not None:
            o['port'] = int(self['port'])
        if self['ca'] is not None:
            o['caPath'] = self.decodeCommandLine(self['ca'])
        if self['cert'] is not None:
            o['certPath'] = self.decodeCommandLine(self['cert'])
        return o


    def _configure(self, store):
        service = store.findUnique(FusionIndexService, default=None)
        if service is None:
            if self['create']:
                service = FusionIndexService(store=store, **self._opts())
                installOn(service, store)
            else:
                print 'No existing service; pass --create to allow creation.'
                raise SystemExit(1)
        else:
            for k, v in self._opts().iteritems():
                setattr(service, k, v)
        print service


    def postOptions(self):
        store = self.parent.getStore()
        store.transact(self._configure, store)
        raise SystemExit(0)

__all__ = ['FusionIndexConfiguration']
