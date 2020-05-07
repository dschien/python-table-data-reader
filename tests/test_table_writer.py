import unittest
from pathlib import Path

from table_data_reader import ParameterRepository, TableParameterLoader
from table_data_reader.table_data_writer import TableWriter


class MyTestCase(unittest.TestCase):

    def test_basic_writing(self):
        writer = TableWriter(workbook_path=Path(__file__).parent / 'test_v2.xlsx', worksheet='Sheet1')
        data = {'ref value': '20',
                'id': 1, }
        writer.update_table(data)

        repository = ParameterRepository()
        TableParameterLoader(filename=Path(__file__).parent / 'test_v2.xlsx', table_handler='openpyxl').load_into_repo(
            sheet_name='Sheet1',
            repository=repository)
        p = repository.get_parameter('a')

        assert p.kwargs['ref value'] == 20


if __name__ == '__main__':
    unittest.main()
