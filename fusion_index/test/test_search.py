from axiom.store import Store
from hypothesis import given
from hypothesis.strategies import lists, sampled_from, text
from testtools import TestCase
from testtools.matchers import Equals

from fusion_index.search import SearchClasses, SearchEntry



def axiom_text():
    return text().map(lambda s: u''.join(c for c in s if c != u'\x00'))


def upper(text):
    return text.upper()


def lower(text):
    return text.lower()


def mixCase(text):
    return u''.join([c.upper(), c.lower()][n % 2] for n, c in enumerate(text))


def spaced(text):
    return u' \t'.join(text)


def punctuated(text):
    return u'.:_'.join(text)


def mutated(value):
    return lists(sampled_from([upper, lower, mixCase])).map(
        lambda mutations: reduce(lambda v, f: f(v), mutations, value))


class SearchTests(TestCase):
    @given(axiom_text(), axiom_text(), axiom_text(), axiom_text(),
           axiom_text())
    def test_exactSearches(self, environment, indexType, searchValue,
                           searchType, result):
        """
        Test inserting, searching, and removing for the exact search class.
        """
        s = Store()
        def _tx():
            SearchEntry.insert(
                s, SearchClasses.EXACT, environment, indexType, searchValue,
                searchType, result)
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
                s, SearchClasses.EXACT, environment, indexType, searchValue,
                searchType, result)
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


    @given(axiom_text(), axiom_text(), axiom_text(), axiom_text(),
           axiom_text())
    def test_prefixSearches(self, environment, indexType, searchValue,
                            searchType, result):
        """
        Test inserting, searching, and removing for the prefix search class.
        """
        s = Store()
        def _tx():
            SearchEntry.insert(
                s, SearchClasses.PREFIX, environment, indexType, searchValue,
                searchType, result)
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
                s, SearchClasses.PREFIX, environment, indexType, searchValue,
                searchType, result)
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
            RuntimeError, SearchEntry.search, Store(), 42, u'', u'', u'')


    @given(axiom_text())
    def test_normalization(self, value):
        """
        Inserting a value and then searching with a search equal to that value
        over normalization returns the inserted entry.
        """
        s = Store()
        def _tx():
            SearchEntry.insert(
                s, SearchClasses.EXACT, u'e', u'i', value, u'type', u'RESULT')
            for mutation in [upper, lower, mixCase, spaced, punctuated]:
                self.assertThat(
                    list(SearchEntry.search(
                        s, SearchClasses.EXACT, u'e', u'i', mutation(value))),
                    Equals([u'RESULT']))
        s.transact(_tx)
