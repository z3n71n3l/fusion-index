from axiom.attributes import ConstraintError
from axiom.store import Store
from hypothesis import given
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule
from hypothesis.strategies import binary, lists, text, tuples
from testtools import TestCase
from testtools.matchers import Equals, raises

from fusion_index.lookup import LookupEntry


def axiom_text():
    return text().map(lambda s: u''.join(c for c in s if c != u'\x00'))


class LookupTests(TestCase):
    @given(lists(tuples(axiom_text(), axiom_text(), axiom_text(), binary())))
    def test_inserts(self, values):
        """
        Test inserting and retrieving arbitrary entries.
        """
        s = Store()
        def _tx():
            for e, t, k, v in values:
                LookupEntry.set(s, e, t, k, v)
                self.assertThat(LookupEntry.get(s, e, t, k), Equals(v))
        s.transact(_tx)



class LookupStateMachine(RuleBasedStateMachine):
    stores = Bundle('stores')

    @rule(target=stores)
    def newStore(self):
        return Store(), {}


    @rule(s=stores, e=axiom_text(), t=axiom_text(), k=axiom_text(), v=binary())
    def insert(self, s, e, t, k, v):
        s, d = s
        s.transact(LookupEntry.set, s, e, t, k, v)
        d[(e, t, k)] = v


    @rule(s=stores)
    def compare(self, s):
        s, d = s
        def _tx():
            for (e, t, k), v in d.iteritems():
                assert LookupEntry.get(e, t, k) == v
        s.transact(_tx)
