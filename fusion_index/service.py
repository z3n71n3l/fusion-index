from axiom import attributes as a
from axiom.dependency import installOn
from axiom.item import Item
from axiom.scripts.axiomatic import AxiomaticCommand
from twisted.application.service import IService, Service



class FusionIndexService(Item, Service):
    """
    Service powerup for exposing the index service over HTTPS.
    """
    powerupInterfaces = [IService]
    interface = a.bytes(default='', allowNone=False)
    port = a.integer(default=8443, allowNone=False)
    caPath = a.text(allowNone=False)
    certPath = a.text(allowNone=False)

    endpointService = a.inmemory()
    parent = a.inmemory()
    name = a.inmemory()
    running = a.inmemory()



class FusionIndexConfiguration(AxiomaticCommand):
    """
    Axiomatic subcommand plugin for inspecting and modifying the index service
    configuration.
    """
    name = 'fusion_index'
    description = 'Fusion index service configuration'

    optFlags = [
        ('create', None, 'Allow creating the service if it does not already exist'),
        ]

    optParameters = [
        ('interface', 'i', '', 'Interface to listen on'),
        ('port', 'p', 8443, 'Port to listen on'),
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
        s = store.findUnique(FusionIndexService, default=None)
        if s is None:
            if self['create']:
                service = FusionIndexService(store=store, **self._opts())
                installOn(service, store)
                print service
            else:
                print 'No existing service; pass --create to allow creation.'
                raise SystemExit(1)


    def postOptions(self):
        store = self.parent.getStore()
        store.transact(self._configure, store)
        raise SystemExit(0)

__all__ = ['FusionIndexConfiguration']
