from pathlib import Path
from typing import List, Dict
from collections import namedtuple
from openpyxl import load_workbook
from table_data_reader import OpenpyxlTableHandler

import logging

logger = logging.getLogger(__name__)

Cell_value = namedtuple('Cell_value', ['cell_ref', 'value'])


class TableWriter(OpenpyxlTableHandler):

    def __init__(self, workbook_input_path: Path = None, worksheets: List = None, workbook_output_path: Path = None):
        """

        :type workbook_input_path: Path object
        """
        super().__init__()
        self.worksheets = worksheets
        self.workbook_path = workbook_input_path
        self.workbook_output_path = workbook_output_path if workbook_output_path else workbook_input_path
        self.workbook = load_workbook(workbook_input_path)

    def update_table(self, data: List[Dict[str, float]]) -> None:
        """
        Iterate over all cells, if the id is identical, then overwrite the ref value provided.
        Overwrites the table

        :param data:
        :return:
        """
        _data = {item['id']: item['value'] for item in data}

        def update_row_visitor(row=None, header=None, **kwargs):
            cell_map = {}
            for key, cell in zip(header, row):
                cell_map[key] = Cell_value(cell_ref=cell, value=cell.value)
            var_id = cell_map['id'].value
            if var_id in _data.keys():
                # write the updated value into cell
                logger.info(
                    f'Overwriting template value for variable {cell_map["variable"]} (id {var_id}) with new value {_data[var_id]} (was {cell_map["ref value"].value})')
                cell_map['ref value'].cell_ref.value = _data[var_id]

        self.table_visitor(wb=self.workbook, sheet_names=self.worksheets, visitor_function=update_row_visitor)
        logger.info(f'Writing updated workbook to file {self.workbook_output_path}')
        self.workbook.save(self.workbook_output_path)
        self.workbook.close()
