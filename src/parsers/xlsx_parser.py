import pandas as pd
from typing import Any


class XlsxParser:

    def __init__(self, file_name, logger):
        self.file_name = file_name
        self.logger = logger

    def generate_xlsx_for_obj_list(self, obj_list: list[Any]) -> None:
        try:
            obj_dict_list = [vars(obj) for obj in obj_list]
            df = pd.DataFrame(obj_dict_list)
            df.to_excel(f'output/{self.file_name}.xlsx', index=False)
        except ValueError as err:
            self.logger.error(
                'Value error when generating .xlsx file',
                extra={'error': str(err)}
            )
        except Exception as err:
            self.logger.error(
                'Unexpected error when generating .xlsx file',
                extra={'error': str(err)}
            )
