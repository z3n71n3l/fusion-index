"""
Tests for the Axiomatic plugin.
"""
import os
import sys
from StringIO import StringIO

from axiom.scripts.axiomatic import Options as AxiomaticOptions
from axiom.store import Store
from axiom.test.util import CommandStub
from twisted.application.service import IService
from twisted.trial.unittest import SynchronousTestCase

from fusion_index.service import FusionIndexConfiguration, FusionIndexService



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
        self.assertSuccessStatus(config, ['--create'])
        output = sys.stdout.getvalue()
        self.assertIn('FusionIndexService', output)
        self.assertEqual(store.query(FusionIndexService).count(), 1)
        s = store.findUnique(FusionIndexService)
        self.assertIn(s, list(store.powerupsFor(IService)))
