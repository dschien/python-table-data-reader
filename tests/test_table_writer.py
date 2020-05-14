import logging
import shutil
import tempfile
import unittest
from pathlib import Path

import pytest

from table_data_reader import ParameterRepository, TableParameterLoader
from table_data_reader.table_data_writer import TableWriter


class MyTestCase(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def test_basic_writing(self):
        with self._caplog.at_level(logging.INFO):
            with tempfile.TemporaryDirectory() as tmpdirname:
                shutil.copy(Path(__file__).parent / 'test_v2.xlsx', tmpdirname)
                file_path = Path(tmpdirname) / 'test_v2.xlsx'

                writer = TableWriter(workbook_input_path=file_path, worksheets=['Sheet1'])
                data = [{'value': 20, 'id': 1, }]
                writer.update_table(data)

                repository = ParameterRepository()
                TableParameterLoader(filename=file_path,
                                     table_handler='openpyxl').load_into_repo(sheet_name='Sheet1',
                                                                              repository=repository)
                p = repository.get_parameter('a')

        assert p.kwargs['ref value'] == 20


if __name__ == '__main__':
    unittest.main()
