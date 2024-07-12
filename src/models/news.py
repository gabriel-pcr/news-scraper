from datetime import datetime
import re
from typing import Union


class News:

    def __init__(
            self,
            title: str,
            description: Union[str | None],
            date: datetime,
            image_file_name: Union[str | None],
            search_phrase: str
    ) -> None:
        self.title = title
        self.description = description
        self.date = date
        self.image_file_name = image_file_name
        self.search_phrase_count = (
            self._count_search_phrase_in_title_and_description(search_phrase)
        )
        self.contains_money = self._contains_money_in_title_or_description()

    def _count_search_phrase_in_title_and_description(
            self,
            search_phrase: str
    ) -> int:
        title_phrase_count = self.title.lower().count(search_phrase.lower())
        description_phrase_count = (
            self.description.lower().count(search_phrase.lower())
            if self.description
            else 0
        )
        return title_phrase_count + description_phrase_count

    def _contains_money_in_title_or_description(self) -> bool:
        money_pattern = (
            r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d{2})?\s?'
            r'(?:dollars?|USD)\b'
        )
        title_contains_money = bool(re.search(money_pattern, self.title))
        description_contains_money = (
            bool(re.search(money_pattern, self.description))
            if self.description
            else False
        )
        return title_contains_money or description_contains_money

    @property
    def __dict__(self):
        return {
            'title': self.title,
            'description': self.description,
            'date': self.date.strftime('%Y-%m-%d'),
            'image_file_name': self.image_file_name,
            'search_phrase_count': self.search_phrase_count,
            'contains_money': self._contains_money_in_title_or_description()
        }
