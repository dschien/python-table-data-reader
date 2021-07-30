import os

import unittest

from table_data_reader.table_handlers import OpenpyxlTableHandler


TEST_DATA_DIRECTORY = 'data/group_variables'


def get_static_path(filename):
    """
    Direct copy of the function in eam-core-provenance/tests/directory_test_controller.py
    Get the current script directory- which should point to /tests- and join it with the desired filename, then return
    """
    directory = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(directory, TEST_DATA_DIRECTORY, filename)


class TestGroupVariables(unittest.TestCase):
    def test_group_single_sheet(self):
        handler = OpenpyxlTableHandler()

        definitions = handler.load_definitions(None,
                                               filename=get_static_path('group_single_sheet.xlsx'),
                                               with_group=True,
                                               group_vars=['power_laptop'],
                                               groupings=['UK', 'DE'])

        assert len(definitions) == 2

        assert definitions[0]['variable'] == 'power_laptop'
        assert definitions[0]['mean growth'] == {
            'UK': 0.01,
            'DE': 0.02
        }
        assert definitions[0]['initial_value_proportional_variation'] == {
            'UK': 0.2,
            'DE': 0.3
        }
        assert definitions[0]['variability growth'] == {
            'UK': 0.06,
            'DE': 0.07
        }

    def test_group_multiple_sheets(self):
        handler = OpenpyxlTableHandler()

        definitions = handler.load_definitions(None,
                                               filename=get_static_path('group_multiple_sheets.xlsx'),
                                               with_group=True,
                                               group_vars=['power_laptop'],
                                               groupings=['UK', 'DE'])

        assert len(definitions) == 2

        assert definitions[0]['variable'] == 'power_laptop'
        assert definitions[0]['mean growth'] == {
            'UK': 0.01,
            'DE': 0.02
        }
        assert definitions[0]['initial_value_proportional_variation'] == {
            'UK': 0.2,
            'DE': 0.3
        }
        assert definitions[0]['variability growth'] == {
            'UK': 0.06,
            'DE': 0.07
        }