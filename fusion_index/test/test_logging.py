"""
Tests for L{fusion_index.logging}.
"""
from eliot._validation import ValidationError
from twisted.trial.unittest import SynchronousTestCase

from fusion_index.logging import _SERVICE_DESCRIPTION
from fusion_index.service import _ServiceDescription



class ServiceDescriptionSerializationTests(SynchronousTestCase):
    """
    Tests for serialization of L{fusion_index.logging._SERVICE_DESCRIPTION}.
    """
    def test_validate(self):
        """
        Serializing something that is not L{_ServiceDescription} raises a
        validation error.
        """
        self.assertRaises(ValidationError, _SERVICE_DESCRIPTION.validate, 42)
        self.assertRaises(ValidationError, _SERVICE_DESCRIPTION.validate, None)


    def test_serialize(self):
        """
        A service description is serialized to a dict with items for each
        attribute of L{_ServiceDescription}.
        """
        desc = _ServiceDescription(
            reactor=None,
            port=8443,
            interface='localhost',
            options=None,
            router=None)
        self.assertEqual(
            _SERVICE_DESCRIPTION.serialize(desc),
            {'reactor': 'None',
             'port': 8443,
             'interface': 'localhost',
             'options': 'None',
             'router': 'None'})
