import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Tuple, List, Union

import pytz
from dateutil.relativedelta import relativedelta
import requests
from requests import RequestException

from RPA.Browser.Selenium import Selenium, WebElement, By, ElementNotFound
from selenium.common.exceptions import NoSuchElementException

from src.models.news import News
from src.news_portals.la_times import LATimes
from src.setup.inputs import InputProvider
from src.utils.image_utils import ImageUtils


class LATimesScraper:

    def __init__(
            self,
            input_provider: InputProvider,
            logger: logging.Logger
    ) -> None:
        self.browser = Selenium()
        self.input_provider = input_provider
        self.timezone = pytz.timezone(LATimes.TIMEZONE)
        self.logger = logger

    def scrape_news(self):
        self.logger.info('Starting to scrape news')
        self.open_browser()
        self.search_for_phrase()
        self.select_topics()
        self.sort_by_newest()
        news = self.get_news()
        self.close_browser()
        return news

    def open_browser(self) -> None:
        self.logger.info(f'Opening browser in URL: {LATimes.URL}')
        self.browser.open_available_browser(LATimes.URL, maximized=True)

    def search_for_phrase(self) -> None:
        self.logger.info(
            f'Searching for search phrase: {self.input_provider.search_phrase}'
        )
        self.browser.click_button_when_visible(LATimes.SEARCH_BUTTON)
        self.browser.input_text_when_element_is_visible(
            LATimes.SEARCH_INPUT,
            self.input_provider.search_phrase
        )
        self.browser.click_button_when_visible(
            LATimes.SEARCH_SUBMIT_BUTTON
        )
        self.browser.wait_until_element_is_visible(
            LATimes.RESULT_SEARCH_INPUT
        )

    def select_topics(self) -> None:
        self.logger.info(f'Selecting topics: {self.input_provider.topics}')
        for topic in self.input_provider.topics:
            try:
                self.browser.select_checkbox(
                    LATimes.TOPIC_CHECKBOX.format(topic=topic)
                )
                self.browser.wait_until_element_is_visible(
                    LATimes.TOPIC_CHECKED_CHECKBOX.format(topic=topic)
                )
            except ElementNotFound:
                self.logger.warning(f'Topic not found: {topic}')
                continue

    def sort_by_newest(self) -> None:
        self.logger.info('Sorting by newest')
        self.wait_for_results_load()
        self.browser.select_from_list_by_value(
            LATimes.RESULT_SORTING_SELECT,
            LATimes.RESULT_SORTING_NEWEST_VALUE
        )

    def wait_for_results_load(self) -> None:
        self.logger.info('Waiting for results to load')
        current_url = self.browser.get_location()
        next_page_anchor = (
            LATimes.RESULT_NEXT_PAGE_ANCHOR_WITH_URL.format(
                url=current_url
            )
        )
        self.browser.wait_until_element_is_visible(next_page_anchor)

    def get_news(self) -> List[News]:
        self.logger.info('Iterating through pages to get news')
        self.wait_for_results_load()
        start_date, end_date = self._get_date_range()
        news = []
        while True:
            page_news = self._get_page_news(start_date, end_date)
            news.extend(page_news)
            has_next = self.browser.is_element_visible(
                LATimes.RESULT_NEXT_PAGE_ANCHOR
            )

            reached_max_date = (
                    len(page_news) < LATimes.RESULTS_PER_PAGE
            )
            if reached_max_date or not has_next:
                break
            elif has_next:
                self._go_to_next_page()
        return news

    def close_browser(self) -> None:
        self.logger.info('Closing browser')
        self.browser.close_browser()

    def _get_date_range(self) -> Tuple[datetime, datetime]:
        self.logger.info('Getting date range')
        end_date = datetime.now(tz=self.timezone)
        months_delta = relativedelta(
            months=self.input_provider.number_of_months - 1
        )
        start_date = (end_date - months_delta).replace(day=1)
        return start_date, end_date

    def _get_page_news(
            self,
            start_date: datetime,
            end_date: datetime
    ) -> List[News]:
        self.logger.info('Getting current page news')
        news_ul = self.browser.find_element(LATimes.RESULTS_LIST)
        news_li = news_ul.find_elements(By.TAG_NAME, 'li')
        page_news = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_news = {
                executor.submit(
                    self._process_page_news,
                    start_date,
                    end_date,
                    news
                ): news
                for news in news_li
            }
            for future in future_to_news:
                result = future.result()
                if result:
                    page_news.append(result)
        return page_news

    def _process_page_news(
            self,
            start_date: datetime,
            end_date: datetime,
            news: WebElement
    ) -> Union[News | None]:
        self.logger.info('Collecting news data')
        news_datetime = self._get_news_datetime(news)
        if start_date <= news_datetime <= end_date:
            title = news.find_element(
                By.CLASS_NAME,
                LATimes.NEWS_TITLE
            ).text

            try:
                description = news.find_element(
                    By.CLASS_NAME,
                    LATimes.NEWS_DESCRIPTION
                ).text
            except NoSuchElementException:
                self.logger.info(f'Description not found for news: {title}')
                description = None

            image_file_name = self._download_news_image(news, title)
            return News(
                title=title,
                description=description,
                date=news_datetime,
                image_file_name=image_file_name,
                search_phrase=self.input_provider.search_phrase,
            )
        return None

    def _get_news_datetime(self, news_element: WebElement) -> datetime:
        self.logger.info('Getting news datetime')
        timestamp_element = news_element.find_element(
            By.CLASS_NAME,
            LATimes.NEWS_TIMESTAMP_TEXT
        )
        timestamp = int(
            timestamp_element.get_attribute(
                LATimes.NEWS_TIMESTAMP_ATTRIBUTE
            )
        )
        date_obj = datetime.fromtimestamp(timestamp / 1000)
        return date_obj.astimezone(self.timezone)

    def _download_news_image(
            self,
            news: WebElement,
            title: str
    ) -> Union[str | None]:
        self.logger.info(f'Downloading news image: {title}')
        try:
            unparsed_image_url = news.find_element(
                By.CLASS_NAME,
                LATimes.NEWS_IMAGE
            ).get_attribute('src')
            image_url = ImageUtils.extract_image_url_from_url(
                unparsed_image_url
            )
            if image_url is None:
                self.logger.info(f'Image not found for news: {title}')
                return None
            file_name = image_url.split('/')[-1]
            file_name = ImageUtils.add_extension_if_none(
                file_name,
                'jpeg'
            )
            response = requests.get(image_url)
            response.raise_for_status()
            ImageUtils.save_file_to_path(
                'output',
                response.content,
                file_name
            )
            return file_name
        except RequestException as err:
            self.logger.error(
                f'Request error for news image: {title}',
                extra={'error': str(err)}
            )
        except NoSuchElementException:
            self.logger.info(f'No such image element for news: {title}')
        except IOError as err:
            self.logger.error(
                f'Error when trying to save image news: {title}',
                extra={'error': str(err)}
            )
        return None

    def _go_to_next_page(self) -> None:
        self.logger.info('Going to next page')
        next_page_element = self.browser.find_element(
            LATimes.RESULT_NEXT_PAGE_ANCHOR
        )
        next_page_url = self.browser.get_element_attribute(
            next_page_element,
            'href'
        )
        self.browser.click_element_when_visible(next_page_element)
        self.browser.wait_until_location_is(next_page_url)
