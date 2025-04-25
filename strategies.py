class SortStrategy:
    def sort_query(self):
        raise NotImplementedError("You must implement sort_query() method")

class TitleSortStrategy(SortStrategy):
    def sort_query(self):
        return "ORDER BY title ASC"

class PriceSortStrategy(SortStrategy):
    def sort_query(self):
        return "ORDER BY price ASC"

class AuthorSortStrategy(SortStrategy):
    def sort_query(self):
        return "ORDER BY author ASC"

class PublisherSortStrategy(SortStrategy):
    def sort_query(self):
        return "ORDER BY publisher ASC"
