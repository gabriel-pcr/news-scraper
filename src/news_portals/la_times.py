class LATimes:
    TIMEZONE: str = 'America/Los_Angeles'
    URL: str = 'https://www.latimes.com/'

    SEARCH_BUTTON: str = '//button[@data-element="search-button"]'
    SEARCH_INPUT: str = '//input[@data-element="search-form-input"]'
    SEARCH_SUBMIT_BUTTON: str = (
        '//button[@data-element="search-submit-button"]'
    )

    TOPIC_CHECKBOX: str = (
        '//ul[@data-name="Topics"]//span[text()="{topic}"]/preceding::input[1]'
    )
    TOPIC_CHECKED_CHECKBOX: str = (
        '//ul[@data-name="Topics"]//span[text()="{topic}"]/'
        'preceding::input[@type="checkbox" and @checked][1]'
    )

    RESULT_SEARCH_INPUT: str = '//input[@class="search-results-module-input"]'
    RESULT_NEXT_PAGE_ANCHOR: str = (
        '//div[@class="search-results-module-next-page"]//a'
    )
    RESULT_NEXT_PAGE_ANCHOR_WITH_URL: str = (
        f'{RESULT_NEXT_PAGE_ANCHOR}[contains(@href, "{{url}}")]'
    )
    RESULTS_LIST: str = '//ul[@class="search-results-module-results-menu"]'

    RESULT_SORTING_SELECT: str = '//select[@class="select-input"]'
    RESULT_SORTING_NEWEST_VALUE: str = '1'

    NEWS_TITLE: str = 'promo-title'
    NEWS_DESCRIPTION: str = 'promo-description'
    NEWS_TIMESTAMP_TEXT: str = 'promo-timestamp'
    NEWS_TIMESTAMP_ATTRIBUTE: str = 'data-timestamp'
    NEWS_IMAGE: str = 'image'

    RESULTS_PER_PAGE: int = 10
