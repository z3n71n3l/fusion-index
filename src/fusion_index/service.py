from axiom import attributes as a
from axiom.item import Item
from axiom.store import Store
from axiom.upgrade import registerDeletionUpgrader
from twisted.application import strports
from twisted.application.service import IService, IServiceMaker, MultiService, Service
from twisted.internet import reactor
from twisted.plugin import IPlugin
from twisted.python import usage
from twisted.web.server import Site
from zope.interface import implementer

from fusion_index.resource import IndexRouter


class Options(usage.Options):
    optParameters = [
        ["port", "p", "tcp:80", "Port to listen on"],
        ["db", "d", "fusion-index.axiom", "Path to database"],
    ]


@implementer(IServiceMaker, IPlugin)
class FusionIndexServiceMaker(object):
    tapname = "fusion-index"
    description = "Fusion indexing service"
    options = Options

    def makeService(self, options):
        service = MultiService()

        store = Store(options["db"])
        store.querySQL("PRAGMA journal_mode=WAL;")
        store.querySQL("PRAGMA synchronous=NORMAL;")
        IService(store).setServiceParent(service)

        site = Site(IndexRouter(store=store).router.resource())
        webService = strports.service(options["port"], site, reactor=reactor)
        webService.setServiceParent(service)
        return service


class FusionIndexService(Item, Service):
    """
    REMOVED: Old service powerup.
    """
    schemaVersion = 2
    powerupInterfaces = [IService]

    interface = a.bytes(default="", allowNone=False)
    port = a.integer(default=8443, allowNone=False)
    caPath = a.text(allowNone=False)
    certPath = a.text(allowNone=False)


registerDeletionUpgrader(FusionIndexService, 1, 2)


__all__ = ["FusionIndexServiceMaker"]
