import unittest
import openpyxl
import pytest

import table_data_reader
from deepdiff import DeepDiff
import os
import re

from table_data_reader.table_handlers import OpenpyxlTableHandler, TableValidationError

from contextlib import contextmanager


TEST_DATA_DIRECTORY = 'data/validate_tables'


def get_static_path(filename):
    """
    Direct copy of the function in eam-core-provenance/tests/directory_test_controller.py
    Get the current script directory- which should point to /tests- and join it with the desired filename, then return
    """
    directory = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(directory, TEST_DATA_DIRECTORY, filename)


def assert_exception_message(exception, message):
    assert str(exception) == message, f'Expected exception message to be \'{message}\', but was \'{str(exception)}\''


class TestValidateTables(unittest.TestCase):

    def test_valid(self):
        handler = OpenpyxlTableHandler()
        try:
            handler.load_definitions(None, filename=get_static_path('valid.xlsx'))
        except TableValidationError as e:
            raise AssertionError(f'Expected no errors, but \'{str(e)}\' was raised.')

    def test_valid_empty(self):
        handler = OpenpyxlTableHandler()
        try:
            handler.load_definitions(None, filename=get_static_path('valid_empty.xlsx'))
        except TableValidationError as e:
            raise AssertionError(f'Expected no errors, but \'{str(e)}\' was raised.')

    def test_no_header(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_header.xlsx'))

        assert_exception_message(context.exception, 'Table is missing header row for sheet params')

    def test_no_primary_sheet(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_primary_sheet.xlsx'))

        assert_exception_message(context.exception, 'Table has no primary data sheets')

    def test_no_type(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_type.xlsx'))

        assert_exception_message(context.exception, 'Table is missing type column for sheet params')
