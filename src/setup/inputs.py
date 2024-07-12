import logging
import json
from RPA.Robocorp.WorkItems import WorkItems


class InputProvider:

    def __init__(self, logger: logging.Logger) -> None:
        self.search_phrase = 'Nvidia'
        self.topics = '["Business"]'
        self.number_of_months = 3
        self.logger = logger
        self._provide_inputs_from_work_items()

    def _provide_inputs_from_work_items(self):
        self.logger.info('Providing inputs from work items')
        work_items = WorkItems()
        work_items.get_input_work_item()
        self.search_phrase = work_items.get_work_item_variable(
            'SEARCH_PHRASE',
            self.search_phrase
        )
        self.number_of_months = work_items.get_work_item_variable(
            'NUMBER_OF_MONTHS',
            self.number_of_months
        )
        try:
            self.topics = json.loads(
                work_items.get_work_item_variable(
                    'TOPICS',
                    self.topics
                )
            )
        except json.JSONDecodeError:
            self.logger.error('Defined topics are not JSON serializable')
