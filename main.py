import logging

from src.parsers.xlsx_parser import XlsxParser
from src.scrapers.la_times_scraper import LATimesScraper
from src.setup.inputs import InputProvider
from src.setup.logger import LoggerSetup


def main():
    logger_setup = LoggerSetup(__name__, 'output/app.log', logging.INFO)
    logger = logger_setup.get_logger()

    input_provider = InputProvider(logger)
    scraper = LATimesScraper(input_provider, logger)
    news = scraper.scrape_news()
    xlsx_parser = XlsxParser("news", logger)
    xlsx_parser.generate_xlsx_for_obj_list(news)


if __name__ == '__main__':
    main()
