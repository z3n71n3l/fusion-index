from axiom.attributes import text
from axiom.item import Item
from axiom.scripts.axiomatic import AxiomaticCommand
from twisted.application.service import IService, Service



class FusionIndexService(Item, Service):
    """
    Service powerup for exposing the index service over HTTPS.
    """
    powerupInterfaces = [IService]
    dummy = text()



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

    def _configure(self, store):
        s = store.findUnique(FusionIndexService, default=None)
        if s is None:
            if self['create']:
                service = FusionIndexService(store=store)
                store.powerUp(service)
                print service
            else:
                print 'No existing service; pass --create to allow creation.'
                raise SystemExit(1)


    def postOptions(self):
        store = self.parent.getStore()
        store.transact(self._configure, store)
        raise SystemExit(0)

__all__ = ['FusionIndexConfiguration']
