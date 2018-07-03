from axiom.store import Store
from hypothesis import HealthCheck, assume, given, settings
from py2casefold import casefold
from testtools import TestCase
from testtools.matchers import AllMatch, Annotate, Equals, HasLength

from fusion_index.search import SearchClasses, SearchEntry
from fusion_index.test.test_lookup import axiom_text



def spaced(text):
    return u' \t'.join(text)


def punctuated(text):
    return u'.:\''.join(text)


class SearchTests(TestCase):
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    @given(axiom_text(), axiom_text(), axiom_text(), axiom_text(),
           axiom_text())
    def test_exactSearches(self, environment, indexType, searchValue,
                           searchType, result):
        """
        Test inserting, searching, and removing for the exact search class.
        """
        assume(SearchEntry._normalize(searchValue) != u'')
        s = Store()

        def _tx():
            SearchEntry.insert(
                s, SearchClasses.EXACT, environment, indexType, result,
                searchType, searchValue)
            self.assertThat(
                list(SearchEntry.search(
                    s, SearchClasses.EXACT, environment, indexType,
                    searchValue)),
                Equals([result]))
            self.assertThat(
                list(SearchEntry.search(
                    s, SearchClasses.EXACT, environment, indexType,
                    searchValue, searchType)),
                Equals([result]))

            SearchEntry.remove(
                s, SearchClasses.EXACT, environment, indexType, result,
                searchType)
            self.assertThat(
                list(SearchEntry.search(
                    s, SearchClasses.EXACT, environment, indexType,
                    searchValue)),
                Equals([]))
            self.assertThat(
                list(SearchEntry.search(
                    s, SearchClasses.EXACT, environment, indexType,
                    searchValue, searchType)),
                Equals([]))
        s.transact(_tx)


    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    @given(axiom_text(), axiom_text(), axiom_text(), axiom_text(),
           axiom_text())
    def test_prefixSearches(self, environment, indexType, searchValue,
                            searchType, result):
        """
        Test inserting, searching, and removing for the prefix search class.
        """
        assume(SearchEntry._normalize(searchValue[:3]) != u'')
        s = Store()

        def _tx():
            SearchEntry.insert(
                s, SearchClasses.PREFIX, environment, indexType, result,
                searchType, searchValue)
            self.assertThat(
                list(SearchEntry.search(
                    s, SearchClasses.PREFIX, environment, indexType,
                    searchValue[:3])),
                Equals([result]))
            self.assertThat(
                list(SearchEntry.search(
                    s, SearchClasses.PREFIX, environment, indexType,
                    'a' + searchValue)),
                Equals([]))
            self.assertThat(
                list(SearchEntry.search(
                    s, SearchClasses.PREFIX, environment, indexType,
                    searchValue)),
                Equals([result]))
            self.assertThat(
                list(SearchEntry.search(
                    s, SearchClasses.PREFIX, environment, indexType,
                    searchValue, searchType)),
                Equals([result]))

            SearchEntry.remove(
                s, SearchClasses.PREFIX, environment, indexType, result,
                searchType)
            self.assertThat(
                list(SearchEntry.search(
                    s, SearchClasses.PREFIX, environment, indexType,
                    searchValue)),
                Equals([]))
            self.assertThat(
                list(SearchEntry.search(
                    s, SearchClasses.PREFIX, environment, indexType,
                    searchValue, searchType)),
                Equals([]))
        s.transact(_tx)


    def test_invalidSearchClass(self):
        """
        Searching with an invalid search class raises L{RuntimeError}.
        """
        self.assertRaises(
            Exception, SearchEntry.search, Store(), 42, u'', u'', u'')


    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    @given(axiom_text().map(SearchEntry._normalize))
    def test_normalization(self, value):
        """
        Inserting a value and then searching with a search equal to that value
        over normalization returns the inserted entry.
        """
        assume(value != u'')
        s = Store()

        def _tx():
            SearchEntry.insert(
                s, SearchClasses.EXACT, u'e', u'i', u'RESULT', u'type', value)
            for mutation in [casefold, spaced, punctuated]:
                self.assertThat(
                    list(SearchEntry.search(
                        s, SearchClasses.EXACT, u'e', u'i', mutation(value))),
                    Annotate(
                        'Not found for {!r}({!r}) == {!r}'.format(
                            mutation, value, mutation(value)),
                        Equals([u'RESULT'])))
        s.transact(_tx)


    def test_insertEmpty(self):
        """
        Inserting a value that is empty after normalization instead deletes
        the entry.
        """
        s = Store()

        def _tx():
            SearchEntry.insert(
                s, SearchClasses.EXACT, u'e', u'i', u'RESULT', u'type', u'. /')
            self.assertThat(s.query(SearchEntry).count(), Equals(0))
            SearchEntry.insert(
                s, SearchClasses.EXACT, u'e', u'i', u'RESULT', u'type', u'yo')
            self.assertThat(s.query(SearchEntry).count(), Equals(1))
            SearchEntry.insert(
                s, SearchClasses.EXACT, u'e', u'i', u'RESULT', u'type', u'. /')
            self.assertThat(s.query(SearchEntry).count(), Equals(0))
        s.transact(_tx)


    def test_searchEmpty(self):
        """
        Searching for a value that is empty after normalization returns nothing.
        """
        s = Store()

        def _tx():
            SearchEntry.insert(
                s, SearchClasses.PREFIX, u'e', u'i', u'RESULT', u'type', u'yo')
            self.assertThat(s.query(SearchEntry).count(), Equals(1))
            self.assertThat([
                list(SearchEntry.search(
                    s, SearchClasses.PREFIX, u'e', u'i', u'')),
                list(SearchEntry.search(
                    s, SearchClasses.PREFIX, u'e', u'i', u'. .'))],
                AllMatch(Equals([])))
        s.transact(_tx)


    def test_searchLimit(self):
        """
        Searching does not return more results than the limit.
        """
        s = Store()

        def _tx():
            for x in xrange(50):
                SearchEntry.insert(
                    s, SearchClasses.EXACT, u'e', u'i', u'RESULT',
                    u'type{}'.format(x), u'yo')
            self.assertThat(s.query(SearchEntry).count(), Equals(50))
            self.assertThat(
                list(SearchEntry.search(
                    s, SearchClasses.EXACT, u'e', u'i', u'yo', limit=20)),
                HasLength(20))
        s.transact(_tx)
