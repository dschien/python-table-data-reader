import unittest
import openpyxl
from table_data_reader import OpenpyxlTableHandler
from deepdiff import DeepDiff
import os
import re


def create_temp_copy(a):
    wb = openpyxl.load_workbook(a, data_only=True)
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
    name = a.split('.')[0] + "_copy." + a.split('.')[1]
    wb_copy.save(name)


def get_diff_then_make_files_equal(a, b):
    wb_a = openpyxl.load_workbook(a, data_only=True)
    wb_b = openpyxl.load_workbook(b, data_only=True)
    reg1 = re.compile(r".*style.*")
    reg2 = re.compile(r"iterable_item_added")
    diff = DeepDiff(wb_b, wb_a, exclude_regex_paths=[reg1, reg2])
    os.remove(b)
    return diff


class TestVariableIDs(unittest.TestCase):

    def test_existing_ids(self):
        handler = OpenpyxlTableHandler()
        create_temp_copy("tests/data/existing_ids.xlsx")
        handler.load_definitions("params", filename="tests/data/existing_ids_copy.xlsx", id_flag=True)
        diff = get_diff_then_make_files_equal("tests/data/existing_ids.xlsx", "tests/data/existing_ids_copy.xlsx")
        assert handler.id_map == {'power_latop': {'default': 0, "S1": 1},
                                  'energy_intensity_network': {'default': 2}}
        assert 'values_changed' not in diff.keys() and 'type_changes' not in diff.keys()

    def test_some_existing_ids(self):
        handler = OpenpyxlTableHandler()
        create_temp_copy("tests/data/some_existing_ids.xlsx")
        handler.load_definitions("params", filename="tests/data/some_existing_ids_copy.xlsx", id_flag=True)
        diff = get_diff_then_make_files_equal("tests/data/some_existing_ids.xlsx",
                                              "tests/data/some_existing_ids_copy.xlsx")
        assert handler.id_map == {'power_latop': {'default': 0}, 'time_laptop': {'default': 3},
                                  'energy_intensity_network': {'default': 2}}
        assert (str(diff[
                        'type_changes']) == "{'root[0][2][18]._value': {'old_type': <class 'int'>, 'new_type': <class 'NoneType'>, 'old_value': 3, 'new_value': None}}")

    def test_no_existing_ids(self):
        handler = OpenpyxlTableHandler()
        create_temp_copy("tests/data/no_existing_ids.xlsx")
        handler.load_definitions("params", filename="tests/data/no_existing_ids_copy.xlsx", id_flag=True)
        diff = get_diff_then_make_files_equal("tests/data/no_existing_ids.xlsx", "tests/data/no_existing_ids_copy.xlsx")
        assert handler.id_map == {'power_latop': {'default': 0, 'S1': 1}}
        assert (str(
            diff[
                'type_changes']) == "{'root[0][1][18]._value': {'old_type': <class 'int'>, 'new_type': <class 'NoneType'>, 'old_value': 0, 'new_value': None}, 'root[0][2][18]._value': {'old_type': <class 'int'>, 'new_type': <class 'NoneType'>, 'old_value': 1, 'new_value': None}}")
    def test_duplicate_ids(self):
        with self.assertRaises(Exception) as context:
            handler = OpenpyxlTableHandler()
            handler.load_definitions("params", filename="tests/data/duplicate_ids.xlsx", id_flag=True)
        self.assertTrue("Duplicate ID variable " in str(context.exception))

    def test_no_id_flag(self):
        handler = OpenpyxlTableHandler()
        create_temp_copy("tests/data/no_existing_ids.xlsx")
        handler.load_definitions("params", filename="tests/data/no_existing_ids_copy.xlsx")
        diff = get_diff_then_make_files_equal("tests/data/no_existing_ids.xlsx",
                                              "tests/data/no_existing_ids_copy.xlsx")
        assert handler.id_map == {}
        assert 'values_changed' not in diff.keys() and 'type_changes' not in diff.keys()
