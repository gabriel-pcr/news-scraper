import logging
from RPA.Robocorp.WorkItems import WorkItems


class InputProvider:

    def __init__(self, logger: logging.Logger) -> None:
        self.search_phrase = 'Nvidia'
        self.topics = ["Business"]
        self.number_of_months = 3
        self.logger = logger
        self._provide_inputs_from_work_items()
        self._log_defined_variables()

    def _log_defined_variables(self):
        defined_variables = {
            "search_phrase": self.search_phrase,
            "topics": self.topics,
            "number_of_months": self.number_of_months,
        }
        for key, value in defined_variables.items():
            self.logger.info(f'Running with {key} value: {value}')

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
        self.topics = work_items.get_work_item_variable(
            'TOPICS',
            self.topics
        )
