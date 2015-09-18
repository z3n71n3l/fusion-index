"""
Tests for L{fusion_index.service}.
"""
import os
import sys
from StringIO import StringIO

from axiom.dependency import installedOn
from axiom.scripts.axiomatic import Options as AxiomaticOptions
from axiom.store import Store
from axiom.test.util import CommandStub
from twisted.application.service import IService
from twisted.internet.defer import inlineCallbacks
from twisted.python.filepath import FilePath
from twisted.trial.unittest import SynchronousTestCase, TestCase

from fusion_index.service import FusionIndexConfiguration, FusionIndexService
from fusion_index.resource import IndexRouter



class FusionIndexServiceTests(TestCase):
    """
    Tests for L{FusionIndexService}.
    """
    @inlineCallbacks
    def test_startService(self):
        """
        L{FusionIndexService.startService} creates and starts a web server
        hooked up to a TLS endpoint.
        """
        certPath = FilePath(__file__).sibling('data').child('test.cert')
        certPath = certPath.path.decode('utf-8')
        s = FusionIndexService(
            caPath=certPath,
            certPath=certPath)
        s.startService()
        self.assertNotIdentical(s._endpointService, None)
        self.assertTrue(s.running)
        self.assertTrue(s._endpointService.running)
        yield s.stopService()
        self.assertFalse(s.running)
        self.assertFalse(s._endpointService.running)


    def test_serviceDescription(self):
        """
        The service description has the data from the service configuration.
        """
        certPath = FilePath(__file__).sibling('data').child('test.cert')
        certPath = certPath.path.decode('utf-8')
        s = FusionIndexService(
            caPath=certPath,
            certPath=certPath)
        desc = s._serviceDescription()

        self.assertEqual(desc.port, s.port)
        self.assertEqual(desc.interface, s.interface)
        self.assertIsInstance(desc.router, IndexRouter)



class ConfigurationCommandTests(SynchronousTestCase):
    """
    Tests for the I{axiomatic fusion_index} command.
    """
    def setUp(self):
        """
        Override C{sys.stdout} to capture anything written by the port
        subcommand.
        """
        self.oldColumns = os.environ.get('COLUMNS')
        os.environ['COLUMNS'] = '80'
        self.stdout = sys.stdout
        sys.stdout = StringIO()


    def tearDown(self):
        """
        Restore the original value of C{sys.stdout}.
        """
        sys.stdout = self.stdout
        if self.oldColumns is not None:
            os.environ['COLUMNS'] = self.oldColumns


    def _makeConfig(self, store):
        """
        Create a L{FusionIndexConfiguration} instance hooked directly up to the
        given store.
        """
        config = FusionIndexConfiguration()
        config.parent = CommandStub(store, 'port')
        return config


    def assertSuccessStatus(self, options, arguments):
        """
        Parse the given arguments with the given options object and assert that
        L{SystemExit} is raised with an exit code of C{0}.
        """
        self.assertFailStatus(0, options, arguments)


    def assertFailStatus(self, code, options, arguments):
        """
        Parse the given arguments with the given options object and assert that
        L{SystemExit} is raised with the specified exit code.
        """
        exc = self.assertRaises(SystemExit, options.parseOptions, arguments)
        self.assertEqual(exc.args, (code,))


    def test_axiomaticSubcommand(self):
        """
        L{FusionIndexConfiguration} is available as a subcommand of
        I{axiomatic}.
        """
        subCommands = AxiomaticOptions().subCommands
        [options] = [cmd[2] for cmd in subCommands if cmd[0] == 'fusion_index']
        self.assertIdentical(options, FusionIndexConfiguration)


    def test_noServiceOutput(self):
        """
        If no service exists in the store, and creating one is not enabled, an
        error message is printed.
        """
        store = Store()
        config = self._makeConfig(store)
        self.assertFailStatus(1, config, [])
        self.assertEqual(
            'No existing service; pass --create to allow creation.\n',
            sys.stdout.getvalue())
        self.assertEqual(store.query(FusionIndexService).count(), 0)


    def test_serviceCreation(self):
        """
        If no service exists in the store, and creation is requested, the item
        is created and installed.
        """
        store = Store()
        config = self._makeConfig(store)
        self.assertSuccessStatus(
            config,
            ['--create',
             '--ca', 'ca.crt',
             '--cert', 'cert.crt'])

        output = sys.stdout.getvalue()
        self.assertIn('FusionIndexService', output)
        self.assertIn('ca.crt', output)
        self.assertIn('cert.crt', output)

        self.assertEqual(store.query(FusionIndexService).count(), 1)
        s = store.findUnique(FusionIndexService)
        self.assertIn(s, list(store.powerupsFor(IService)))
        self.assertIdentical(installedOn(s), store)

        self.assertEqual(s.interface, '')
        self.assertEqual(s.port, 8443)
        self.assertEqual(s.caPath, u'ca.crt')
        self.assertEqual(s.certPath, u'cert.crt')
