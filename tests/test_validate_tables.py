import unittest

import os

from table_data_reader.table_handlers import OpenpyxlTableHandler, TableValidationError


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

    def test_no_param(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_param.xlsx'))

        assert_exception_message(context.exception, 'Table is missing param column for sheet params')

    def test_no_ref_value(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_ref_value.xlsx'))

        assert_exception_message(context.exception, 'Table is missing ref value column for sheet params')

    def test_no_ref_date(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_ref_date.xlsx'))

        assert_exception_message(context.exception, 'Table is missing ref date column for sheet params')

    def test_no_mean_growth(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_mean_growth.xlsx'))

        assert_exception_message(context.exception, 'Table is missing mean growth column for sheet params')

    def test_no_initial_value_proportional_variation(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_initial_value_proportional_variation.xlsx'))

        assert_exception_message(context.exception, 'Table is missing initial_value_proportional_variation column for '
                                                    'sheet params')

    def test_no_variability_growth(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_variability_growth.xlsx'))

        assert_exception_message(context.exception, 'Table is missing variability growth column for sheet params')

    def test_no_unit(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_unit.xlsx'))

        assert_exception_message(context.exception, 'Table is missing unit column for sheet params')

    def test_no_user_name(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_user_name.xlsx'))

        assert_exception_message(context.exception, 'Table is missing user name column for sheet params')

    def test_no_id(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_id.xlsx'))

        assert_exception_message(context.exception, 'Table is missing id column for sheet params')

    def test_no_order(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_order.xlsx'))

        assert_exception_message(context.exception, 'Table is missing order column for sheet params')

    def test_no_ui_variable(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('no_ui_variable.xlsx'))

        assert_exception_message(context.exception, 'Table is missing ui variable column for sheet params')

    def test_no_description(self):
        handler = OpenpyxlTableHandler()
        with self.assertLogs(level='WARNING') as log:
            handler.load_definitions(None, filename=get_static_path('no_description.xlsx'))

        assert len(log.records) == 1
        assert log.records[0].message == 'Table is missing description column for sheet params',\
            f'Expected exception message to be \'Table is missing description column for sheet params\', but was '\
            f'\'{log.records[0].message}\''

    def test_has_group_primary(self):
        handler = OpenpyxlTableHandler()
        with self.assertRaises(TableValidationError) as context:
            handler.load_definitions(None, filename=get_static_path('has_group_primary.xlsx'))

        assert_exception_message(context.exception, 'params is a primary sheet. It cannot have a \'group\' column.')
