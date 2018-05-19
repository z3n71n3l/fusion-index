"""
Tests for L{fusion_index.service}.
"""
from toolz import count
from twisted.trial.unittest import TestCase

from fusion_index.service import FusionIndexServiceMaker


class FusionIndexServiceTests(TestCase):
    """
    Tests for L{FusionIndexService}.
    """

    def test_startService(self):
        """
        L{FusionIndexServiceMaker} creates a multiservice with the store and
        web services hooked up.
        """
        maker = FusionIndexServiceMaker()
        service = maker.makeService({"db": self.mktemp(), "port": "tcp:0"})
        self.assertEqual(count(service), 2)
