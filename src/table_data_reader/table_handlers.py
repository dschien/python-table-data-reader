import csv
from abc import abstractmethod
from collections import defaultdict
import datetime
from typing import Dict, List
from functools import partial
from openpyxl import Workbook
from typing import Callable

import logging
logger = logging.getLogger(__name__)

from table_data_reader import param_name_maps, ParameterRepository, Parameter


class TableHandler(object):
    version: int

    def __init__(self, version=2):
        self.version = version

    @abstractmethod
    def load_definitions(self, sheet_name, filename=None, id_flag=False, **kwargs):
        raise NotImplementedError()


class Xlsx2CsvHandler(TableHandler):
    def load_definitions(self, sheet_name, filename=None, id_flag=False):
        from xlsx2csv import Xlsx2csv
        data = Xlsx2csv(filename, inmemory=True).convert(None, sheetid=0)

        definitions = []

        _sheet_names = [sheet_name] if sheet_name else [data.keys()]

        for _sheet_name in _sheet_names:
            sheet = data[_sheet_name]

            header = sheet.header
            if header[0] != 'variable':
                continue

            for row in sheet.rows:
                values = {}
                for key, cell in zip(header, row):
                    values[key] = cell
                definitions.append(values)
        return definitions


class DictReaderStrip(csv.DictReader):
    @property
    def fieldnames(self):
        if self._fieldnames is None:
            # Initialize self._fieldnames
            # Note: DictReader is an old-style class, so can't use super()
            csv.DictReader.fieldnames.fget(self)
            if self._fieldnames is not None:
                self._fieldnames = [name.strip() for name in self._fieldnames]
        return self._fieldnames


class CSVHandler(TableHandler):
    def load_definitions(self, sheet_name, filename=None, id_flag=False):
        reader = DictReaderStrip(open(filename), delimiter=',')

        definitions = []

        _definition_tracking = defaultdict(dict)

        for i, row in enumerate(reader):

            values = {k: v.strip() for k, v in row.items()}

            if not values['variable']:
                logger.debug(f'ignoring row {i}: {row}')
                continue
            for key in ['ref value', 'initial_value_proportional_variation', 'mean growth', 'variability growth']:
                try:
                    new_val = float(values[key])
                    values[key] = new_val
                except:
                    if values['type'] == 'interp':
                        continue
                    else:
                        raise Exception(
                            f'Could not convert value <{values[key]}> for key {key} to number in row {i} for variable {values["variable"]}')

            if 'ref date' in values and values['ref date']:
                if isinstance(values['ref date'], str):
                    values['ref date'] = datetime.datetime.strptime(values['ref date'], '%d/%m/%Y')
                    if values['ref date'].day != 1:
                        logger.warning(
                            f'ref date truncated to first of month for variable {values["variable"]}')
                        values['ref date'] = values['ref date'].replace(day=1)
                else:
                    raise Exception(
                        f"{values['ref date']} for variable {values['variable']} is not a date - "
                        f"check spreadsheet value is a valid day of a month")
            logger.debug(f'values for {values["variable"]}: {values}')
            definitions.append(values)
            scenario = values['scenario'] if values['scenario'] else "n/a"

            if scenario in _definition_tracking[values['variable']]:

                logger.error(
                    f"Duplicate entry for parameter "
                    f"with name <{values['variable']}> and <{scenario}> scenario in file")
                raise ValueError(
                    f"Duplicate entry for parameter "
                    f"with name <{values['variable']}> and <{scenario}> scenario in file")

            else:
                _definition_tracking[values['variable']][scenario] = 1
        return definitions


class PandasCSVHandler(TableHandler):

    def strip(self, text):
        try:
            return text.strip()
        except AttributeError:
            return text

    def load_definitions(self, sheet_name, filename=None, id_flag=False):
        self.version = 2

        import pandas as pd
        df = pd.read_csv(filename, usecols=range(15), index_col=False, parse_dates=['ref date'],
                         dtype={'initial_value_proportional_variation': 'float64'},
                         dayfirst=True,
                         # date_parser=l0ambda x: pd.datetime.strptime(x, '%d-%m-%Y')
                         )
        df = df.dropna(subset=['variable', 'ref value'])
        df.fillna("", inplace=True)

        return df.to_dict(orient='records')


class OpenpyxlTableHandler(TableHandler):
    version: int

    def __init__(self, version=2):
        super().__init__(version=version)

    def groupings_handler(self, values: Dict = None, inline_groupings=None, sheet_name=None, **kwargs):
        """
        Mutates the inline_groupings dictionary to store group-level variable values
        Dictionary is organised as dict[variable][scenario][group]
        :param values:
        :param inline_groupings:
        :param sheet_name:
        :param kwargs:
        :return:
        """

        var = values["variable"]
        group = values["group"]
        scenario = values["scenario"] if values["scenario"] else "default"
        if group is not None:
            if var not in inline_groupings.keys():
                inline_groupings[var] = {}
            if scenario not in inline_groupings[var].keys():
                inline_groupings[var][scenario] = {}
            if group in inline_groupings[var][scenario].keys():
                logger.error(
                    f"Duplicate entry for parameter "
                    f"with name <{var}>,<{group}> scenario, and <{scenario}> group in sheet {sheet_name}")
                raise ValueError(
                    f"Duplicate entry for parameter "
                    f"with name <{var}>,<{group}> scenario, and <{scenario}> group in sheet {sheet_name}")
            inline_groupings[var][scenario][group] = values

    def truncate_ref_date(self, values: Dict = None):
        """
        Truncates ref dates to the beginning of the month
        """

        if values.get('ref date') is not None:
            if isinstance(values['ref date'], datetime.datetime):
                if values['ref date'].day != 1:
                    logger.warning(f'ref date truncated to first of month for variable {values["variable"]}')
                    values['ref date'] = values['ref date'].replace(day=1)
            else:
                raise Exception(
                    f"{values['ref date']} for variable {values['variable']} is not a date - "
                    f"check spreadsheet value is a valid day of a month")
        return values

    def build_definitions(self, values: Dict = None, definitions=None, sheet_name=None,
                          group_flag=False, inline_groupings=None, wb=None, **kwargs):
        """
        Assigns group-level dictionaries to parameter values in definitions with weird dictionary stuff
        :param values:
        :param definitions:
        :param sheet_name:
        :param group_flag:
        :param inline_groupings:
        :param wb:
        :param kwargs:
        :return:
        """

        values = self.truncate_ref_date(values)

        logger.debug(f'values for {values["variable"]}: {values}')
        name = values['variable']
        scenario = values['scenario'] if values['scenario'] else "default"

        if scenario in definitions[name].keys():
            # if this is an inline group row the error doesn't need to be raised as it's normal
            if values['group'] is not None:
                return None
            logger.error(
                f"Duplicate entry for parameter "
                f"with name <{values['variable']}> and <{scenario}> scenario in sheet {sheet_name}")
            raise ValueError(
                f"Duplicate entry for parameter "
                f"with name <{values['variable']}> and <{scenario}> scenario in sheet {sheet_name}")
        else:
            # if the group flag is not on or there is no sheet by this parameter name just read from params
            if not group_flag or (name not in wb.sheetnames and name not in inline_groupings.keys()):
                definitions[name][scenario] = values
            else:
                keys = list(values.keys())
                group_values = {}
                set_values = ["variable", "scenario", "type", "param", "unit", "group"]
                for s in set_values:
                    keys.remove(s)
                    group_values[s] = values[s]
                for k in keys:
                    group_values[k] = {}
                if name in inline_groupings.keys():
                    # we have already parsed this group variable in inline_groupings
                    # so just set group_values here
                    # todo: give variables more descriptive names
                    if scenario in inline_groupings[name].keys():
                        for c in inline_groupings[name][scenario].keys():
                            for k in keys:
                                if inline_groupings[name][scenario][c][k] is not None:
                                    group_values[k][c] = inline_groupings[name][scenario][c][k]  # do 10005 here
                                else:
                                    group_values[k][c] = values[k]
                else:
                    # the variable is a group variable but has not been parsed inline as part of the main page
                    # so, find its sheet and read from it.
                    # todo: move this into groupings_handler?
                    rows = list(wb[name].iter_rows())
                    header = [cell.value for cell in rows[0]]
                    for i, row in enumerate(rows[1:]):
                        temp_values = {}
                        for key, cell in zip(header, row):
                            temp_values[key] = cell.value  # reads values from the variable's sheet
                        temp_scenario = temp_values['scenario'] if temp_values['scenario'] else "default"
                        if temp_scenario == scenario:
                            for k in keys:
                                if k in header and temp_values[k] is not None:
                                    group_values[k][temp_values["group"]] = temp_values[k]
                                else:
                                    group_values[k][temp_values["group"]] = values[k]

                ref_dates = list(group_values['ref date'].values())
                # Ensures that every element in ref_dates is the same
                # todo: see if we can remove this restriction
                assert ref_dates.count(ref_dates[0]) == len(ref_dates),\
                    f"Different groups have different ref dates for {values['variable']}"
                group_values['ref date'] = ref_dates[0]

                definitions[name][scenario] = group_values

    def table_visitor(self, wb: Workbook = None, sheet_names: List[str] = None, visitor_function: Callable = None,
                      definitions=None, **kwargs):
        """
        stub for id management

        todo: try and remove checks for specific kwargs to allow for more generic visitor functionality

        todo: make this work for other tables? might not be worth the effort

        :param definitions:
        :param wb:
        :type wb:
        :param sheet_names:
        :type sheet_names:
        :param visitor_function:
        :type visitor_function:
        :return:
        :rtype:
        """
        if not sheet_names:
            sheet_names = wb.sheetnames
        for _sheet_name in sheet_names:
            if _sheet_name == 'metadata':
                continue
            sheet = wb[_sheet_name]
            rows = list(sheet.iter_rows())
            header = [cell.value for cell in rows[0]]
            if header[0] != 'variable':
                continue
            for i, row in enumerate(rows[1:]):
                values = {}
                for key, cell in zip(header, row):
                    values[key] = cell.value
                if not values['variable']:
                    logger.debug(f'ignoring row {i}: {row}')
                    continue

                group_flag = kwargs.get('with_group') and (values['variable'] in kwargs['group_vars'])

                visitor_function(ws=sheet, values=values, definitions=definitions,
                                 row_idx=i, sheet_name=_sheet_name, row=row,
                                 header=header, wb=wb, group_flag=group_flag, **kwargs)
        return definitions

    def get_version(self, wb):
        # todo: test versioning?
        version = 1
        try:
            sheet = wb['metadata']
            rows = list(sheet.iter_rows())
            for row in rows:
                if row[0].value == 'version':
                    version = row[1].value
            self.version = version
        except:
            logger.info(f'could not find a sheet with name "metadata" in workbook. defaulting to v2')
        return version

    def check_all_groups_always_present(self, definitions_list, **kwargs):
        """
        check all variables have the same set of groupings and that it is the same set as the yaml file dictates
        todo: this might not work for countries not listed in the yaml, write a test or more experimenting?
        :param definitions_list: The definitions dictionary generated by ref_date_handling
        :param kwargs: Contains list of groupings from the yaml model
        :return:
        """

        for variable in definitions_list:
            for value in variable.values():
                if isinstance(value, dict):
                    assert list(value.keys()) == kwargs.get('groupings')

    def load_definitions(self, sheet_name=None, filename: str = None, **kwargs):
        """
        Loads definitions from the excel workbook
        If sheet_name is given only that sheet will be parsed; if left as None, all sheets will be used.

        :param sheet_name: The name of the sheet to be used; if left blank, all sheets used instead.
        :param filename: The workbook to be parsed
        :param id_flag: Whether missing ids in the excel book should be assigned
        :return: A list of dictionaries containing all the variable value data
        """
        from openpyxl import load_workbook
        wb = load_workbook(filename, data_only=True)

        # Handles id logic and generates an id_map dictionary
        # todo: move invocation to separate program
        from table_data_reader import id_handler
        id_map, highest_id = id_handler.build_id_dict(filename)
        if id_handler.check_for_duplicate_ids(id_map):
            raise Exception("Duplicate ID variable found")
        if kwargs.get('id_flag'):
            id_handler.fill_missing_ids(filename, id_map, highest_id)

        # maps variables to their scenario and group-specific values.
        inline_groupings = {}
        # maps variables to their values, but has dictionaries for each value with different group values
        definitions = defaultdict(lambda: defaultdict(dict))

        _sheet_names = [sheet_name] if sheet_name else wb.sheetnames
        version = self.get_version(wb)

        table_visitor_partial = partial(self.table_visitor, wb=wb, sheet_names=_sheet_names,
                                        definitions=definitions, inline_groupings=inline_groupings, **kwargs)

        # the first visitor pass is for groups, to build the inline_groupings object,
        # the second visitor pass builds the definitions object.
        if kwargs.get('with_group'):
            table_visitor_partial(visitor_function=self.groupings_handler)
        table_visitor_partial(visitor_function=self.build_definitions)

        definitions_list = []
        for var_set in definitions.values():
            for scenario_var in var_set.values():
                definitions_list.append(scenario_var)

        self.check_all_groups_always_present(definitions_list, **kwargs)
        return definitions_list


class XLWingsTableHandler(TableHandler):
    @staticmethod
    def get_sheet_range_bounds(filename, sheet_name):
        from openpyxl import load_workbook
        wb = load_workbook(filename)
        sheet = wb[sheet_name]
        rows = list(sheet.iter_rows())
        return len(rows)

    def load_definitions(self, sheet_name, filename=None, id_flag=False):
        import xlwings as xw
        definitions = []
        wb = xw.Book(fullname=filename)
        _sheet_names = [sheet_name] if sheet_name else wb.sheets
        for _sheet_name in _sheet_names:
            sheet = wb.sheets[_sheet_name]
            range = sheet.range('A1').expand()
            rows = range.rows
            header = [cell.value for cell in rows[0]]

            # check if this sheet contains parameters or if it documentation
            if header[0] != 'variable':
                continue

            total_rows = self.get_sheet_range_bounds(filename, _sheet_name)
            range = sheet.range((1, 1), (total_rows, len(header)))
            rows = range.rows
            for row in rows[1:]:
                values = {}
                for key, cell in zip(header, row):
                    values[key] = cell.value
                definitions.append(values)
        return definitions


class TableParameterLoader(object):
    definition_version: int
    """Utility to populate ParameterRepository from spreadsheets.

        The structure of the spreadsheets is:

        | variable | ... |
        |----------|-----|
        |   ...    | ... |

        If the first row in a spreadsheet does not contain they keyword 'variable' the sheet is ignored.

       """

    def __init__(self, filename, table_handler='openpyxl', version=2, **kwargs):
        self.filename = filename
        self.definition_version = 2  # default - will be overwritten by handler

        logger.info(f'Using {table_handler} excel handler')
        table_handler_instance = None
        if table_handler == 'csv':
            table_handler_instance = CSVHandler(version)
        if table_handler == 'pandas':
            table_handler_instance = PandasCSVHandler(version)
        if table_handler == 'openpyxl':
            table_handler_instance = OpenpyxlTableHandler()
        if table_handler == 'xlsx2csv':
            table_handler_instance = Xlsx2CsvHandler()
        if table_handler == 'xlwings':
            table_handler_instance = XLWingsTableHandler()
        self.table_handler: TableHandler = table_handler_instance

    def load_parameter_definitions(self, sheet_name: str = None, **kwargs):
        """
        Load variable text from rows in excel file.
        If no spreadsheet arg is given, all spreadsheets are loaded.
        The first cell in the first row in a spreadsheet must contain the keyword 'variable' or the sheet is ignored.

        Any cells used as titles (with no associated value) are also added to the returned dictionary. However, the
        values associated with each header will be None. For example, given the spreadsheet:

        | variable | A | B |
        |----------|---|---|
        | Title    |   |   |
        | Entry    | 1 | 2 |

        The following list of definitions would be returned:

        [ { variable: 'Title', A: None, B: None }
        , { variable: 'Entry', A: 1   , B: 2    }
        ]

        :param sheet_name:
        :return: list of dicts with {header col name : cell value} pairs
        """
        definitions = self.table_handler.load_definitions(sheet_name, filename=self.filename, **kwargs)
        self.definition_version = self.table_handler.version
        return definitions

    def load_into_repo(self, repository: ParameterRepository = None, sheet_name: str = None, **kwargs):
        """
        Create a Repo from an excel file.
        :param repository: the repository to load into
        :param sheet_name:
        :return:
        """
        repository.add_all(self.load_parameters(sheet_name, **kwargs))

    def load_parameters(self, sheet_name, **kwargs):
        # todo: work out what is going on here and comment it

        parameter_definitions = self.load_parameter_definitions(sheet_name=sheet_name, **kwargs)
        params = []

        param_name_map = param_name_maps[int(self.definition_version)]
        for _def in parameter_definitions:
            # substitute names from the headers with the kwargs names in the Parameter and Distributions classes
            # e.g. 'variable' -> 'name', 'module' -> 'module_name', etc
            parameter_kwargs_def = {}
            for k, v in _def.items():
                if k in param_name_map:
                    if param_name_map[k]:
                        parameter_kwargs_def[param_name_map[k]] = v
                    else:
                        parameter_kwargs_def[k] = v
                elif kwargs.get('with_group') and k in kwargs['groupings']:
                    parameter_kwargs_def[k] = {}
                    for l, w in _def[k].items():
                        if l in param_name_map:
                            if param_name_map[l]:
                                parameter_kwargs_def[k][param_name_map[l]] = w
                            else:
                                parameter_kwargs_def[k][l] = w
            name_ = parameter_kwargs_def['name']
            del parameter_kwargs_def['name']
            p = Parameter(name_, version=self.definition_version, **parameter_kwargs_def)
            params.append(p)
        return params
