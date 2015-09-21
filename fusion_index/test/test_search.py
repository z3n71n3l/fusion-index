from axiom.store import Store
from hypothesis import given
from hypothesis.strategies import text
from testtools import TestCase
from testtools.matchers import Equals

from fusion_index.search import SearchClasses, SearchEntry



def axiom_text():
    return text().map(lambda s: u''.join(c for c in s if c != u'\x00'))


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
