"""
Tests for the Axiomatic plugin.
"""
import os
import sys
from StringIO import StringIO

from axiom.scripts.axiomatic import Options as AxiomaticOptions
from twisted.trial.unittest import SynchronousTestCase

from fusion_index.service import FusionIndexConfiguration



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


    def assertSpacelessEqual(self, first, second):
        """
        Assert the equality of two strings without respect to their whitespace.
        """
        self.assertEqual(' '.join(first.split()), ' '.join(second.split()))


    def test_axiomaticSubcommand(self):
        """
        L{FusionIndexConfiguration} is available as a subcommand of
        I{axiomatic}.
        """
        subCommands = AxiomaticOptions().subCommands
        [options] = [cmd[2] for cmd in subCommands if cmd[0] == 'fusion_index']
        self.assertIdentical(options, FusionIndexConfiguration)
