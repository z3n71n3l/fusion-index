from axiom.store import Store
from hypothesis import given
from hypothesis.strategies import binary, lists, text, tuples, characters
from testtools import TestCase
from testtools.matchers import Equals

from fusion_index.lookup import LookupEntry


def axiom_text():
    return text(
        alphabet=characters(
            blacklist_categories={'Cs'},
            blacklist_characters={u'\x00'}),
        average_size=5)


class LookupTests(TestCase):
    @given(lists(tuples(axiom_text(), axiom_text(), axiom_text(), binary())))
    def test_inserts(self, values):
        """
        Test inserting and retrieving arbitrary entries.
        """
        s = Store()
        def _tx():
            d = {}
            for e, t, k, v in values:
                LookupEntry.set(s, e, t, k, v)
                d[(e, t, k)] = v
                self.assertThat(LookupEntry.get(s, e, t, k), Equals(v))
            for (e, t, k), v in d.iteritems():
                self.assertThat(LookupEntry.get(s, e, t, k), Equals(v))
        s.transact(_tx)
