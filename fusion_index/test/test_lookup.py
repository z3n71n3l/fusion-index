import string

from axiom.store import Store
from hypothesis import given
from hypothesis.strategies import binary, characters, lists, text, tuples
from testtools import TestCase
from testtools.matchers import Equals

from fusion_index.lookup import LookupEntry


def axiom_text():
    return text(
        alphabet=characters(
            blacklist_categories={'Cs'},
            blacklist_characters={u'\x00'}),
        average_size=5)


_lower_table = dict(
    zip(map(ord, string.uppercase.decode('ascii')),
        map(ord, string.lowercase.decode('ascii'))))


def _lower(s):
    """
    Lowercase only ASCII characters, like SQLite NOCASE.
    """
    return s.translate(_lower_table)


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
                d[(_lower(e), _lower(t), _lower(k))] = v
                self.assertThat(LookupEntry.get(s, e, t, k), Equals(v))
            for (e, t, k), v in d.iteritems():
                self.assertThat(LookupEntry.get(s, e, t, k), Equals(v))
        s.transact(_tx)
