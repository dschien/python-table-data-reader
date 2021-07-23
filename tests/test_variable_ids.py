import unittest
import openpyxl
from table_data_reader import OpenpyxlTableHandler
from deepdiff import DeepDiff
import os
import re


def create_temp_copy(original):
    wb = openpyxl.load_workbook(original, data_only=True)
    wb_copy = openpyxl.Workbook()
    sheet_names = wb.sheetnames
    for sheet_name in sheet_names:
        sheet_a = wb_copy.create_sheet(sheet_name)
        sheet_b = wb[sheet_name]
        m = sheet_b.max_row
        for row in range(len(list(sheet_b.iter_rows()))):
            for col in range(len(list(sheet_b.iter_cols()))):
                c = sheet_a.cell(row=row + 1, column=col + 1)
                val = sheet_b.cell(row=row + 1, column=col + 1).value
                c.value = val
    std = wb_copy['Sheet']
    wb_copy.remove(std)
    name = original.split('.')[0] + "_copy." + original.split('.')[1]
    wb_copy.save(name)


def get_diff(a, b):
    wb_a = openpyxl.load_workbook(a, data_only=True)
    wb_b = openpyxl.load_workbook(b, data_only=True)
    reg1 = re.compile(r".*style.*")
    reg2 = re.compile(r"iterable_item_added")
    diff = DeepDiff(wb_a, wb_b, exclude_regex_paths=[reg1, reg2])
    return diff

def delete_temp_copy(copy):
    os.remove(copy)


def get_static_path(filename):
    """
    Direct copy of the function in eam-core-provenance/tests/directory_test_controller.py
    Get the current script directory- which should point to /tests- and join it with the desired filename, then return
    """
    directory = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(directory, filename)


class TestVariableIDs(unittest.TestCase):

    def test_existing_ids(self):
        handler = OpenpyxlTableHandler()
        create_temp_copy(get_static_path('data/existing_ids.xlsx'))
        handler.load_definitions("params", filename=get_static_path('data/existing_ids_copy.xlsx'), id_flag=True)
        diff = get_diff(get_static_path('data/existing_ids.xlsx'), get_static_path('data/existing_ids_copy.xlsx'))
        delete_temp_copy(get_static_path('data/existing_ids_copy.xlsx'))
        assert handler.id_map == {'power_latop': {'default': 0, "S1": 1},
                                  'energy_intensity_network': {'default': 2}}
        assert 'values_changed' not in diff.keys() and 'type_changes' not in diff.keys()

    def test_existing_ids_group(self):
        handler = OpenpyxlTableHandler()
        create_temp_copy(get_static_path('data/existing_ids_group.xlsx'))

        handler.load_definitions("params",
                                 filename=get_static_path('data/existing_ids_group_copy.xlsx'),
                                 id_flag=True,
                                 with_group=True,
                                 groupings=['UK', 'DE'],
                                 group_vars=['power_laptop', 'energy_intensity_network'])

        diff = get_diff(get_static_path('data/existing_ids_group.xlsx'),
                        get_static_path('data/existing_ids_group_copy.xlsx'))

        delete_temp_copy(get_static_path('data/existing_ids_group_copy.xlsx'))

        assert handler.id_map == {
            'power_laptop': {
                'default': {
                    'overall': 0,
                    'UK': 1,
                    'DE': 2
                }
            },
            'energy_intensity_network': {
                'default': {
                    'overall': 3,
                    'UK': 4,
                    'DE': 5
                }
            }
        }

        assert 'values_changed' not in diff.keys() and 'type_changes' not in diff.keys()

    def test_some_existing_ids(self):
        handler = OpenpyxlTableHandler()
        create_temp_copy(get_static_path('data/some_existing_ids.xlsx'))
        handler.load_definitions("params", filename=get_static_path('data/some_existing_ids_copy.xlsx'), id_flag=True)
        diff = get_diff(get_static_path('data/some_existing_ids.xlsx'),
                        get_static_path('data/some_existing_ids_copy.xlsx'))
        delete_temp_copy(get_static_path('data/some_existing_ids_copy.xlsx'))
        assert handler.id_map == {'power_latop': {'default': 0}, 'time_laptop': {'default': 3},
                                  'energy_intensity_network': {'default': 2}}

        assert diff['type_changes']['root[0][2][18]._value']['new_value'] == 3

    def test_no_existing_ids(self):
        handler = OpenpyxlTableHandler()
        create_temp_copy(get_static_path('data/no_existing_ids.xlsx'))
        handler.load_definitions("params", filename=get_static_path('data/no_existing_ids_copy.xlsx'), id_flag=True)
        diff = get_diff(get_static_path('data/no_existing_ids.xlsx'), get_static_path('data/no_existing_ids_copy.xlsx'))
        delete_temp_copy(get_static_path('data/no_existing_ids_copy.xlsx'))
        assert handler.id_map == {'power_latop': {'default': 0, 'S1': 1}}

        assert diff['type_changes']['root[0][1][18]._value']['new_value'] == 0
        assert diff['type_changes']['root[0][2][18]._value']['new_value'] == 1

    def test_duplicate_ids(self):
        with self.assertRaises(Exception) as context:
            handler = OpenpyxlTableHandler()
            handler.load_definitions("params", filename=get_static_path('data/duplicate_ids.xlsx'), id_flag=True)
        self.assertTrue("Duplicate ID variable " in str(context.exception))

    def test_no_id_flag(self):
        handler = OpenpyxlTableHandler()
        create_temp_copy(get_static_path('data/no_existing_ids.xlsx'))
        handler.load_definitions("params", filename=get_static_path('data/no_existing_ids_copy.xlsx'))
        diff = get_diff(get_static_path('data/no_existing_ids.xlsx'),
                        get_static_path('data/no_existing_ids_copy.xlsx'))
        delete_temp_copy(get_static_path('data/no_existing_ids_copy.xlsx'))
        assert handler.id_map == {}
        assert 'values_changed' not in diff.keys() and 'type_changes' not in diff.keys()
