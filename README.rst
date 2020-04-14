========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor|
        | |codecov|
    * - package
      - | |version| |supported-versions| |supported-implementations|
.. |docs| image:: https://readthedocs.org/projects/eam-data-tools/badge/?style=flat
    :target: https://readthedocs.org/projects/eam-data-tools
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/dschien/eam-data-tools.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/dschien/eam-data-tools

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/dschien/eam-data-tools?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/dschien/eam-data-tools

.. |codecov| image:: https://codecov.io/gh/dschien/eam-data-tools/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/dschien/eam-data-tools

.. |version| image:: https://img.shields.io/pypi/v/eam-data-tools.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/eam-data-tools/

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/eam-data-tools.svg
    :alt: Supported versions
    :target: https://pypi.org/project/eam-data-tools/

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/eam-data-tools.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/eam-data-tools/

.. end-badges

Tool to define random variables in a table. The main purpose is to support the EAM framework.

* Free software: Apache Software License 2.0

Installation
============

::

    pip install eam-data-tools

You can also install the in-development version with::

    pip install https://github.com/dschien/eam-data-tools/archive/master.zip


Documentation
=============

https://eam-data-tools.readthedocs.io/

Usage
=====

# Example
Given an excel file with rows similar to the below

+----------+----------+--------+-------------------------------------------------------+--------+--------------------------------------+------+-------------+--------------------+------------+------------+---------+--------+
| variable | scenario | type   | ref value                                             | param  | initial_value_proportional_variation | unit | mean growth | variability growth | ref date   | label      | comment | source |
+----------+----------+--------+-------------------------------------------------------+--------+--------------------------------------+------+-------------+--------------------+------------+------------+---------+--------+
| a        |          | exp    | 10                                                    |        | 0.4                                  | kg   | -0.20       | 0.10               | 01/01/2009 | test var 1 |         |        |
+----------+----------+--------+-------------------------------------------------------+--------+--------------------------------------+------+-------------+--------------------+------------+------------+---------+--------+
| b        |          | interp | {"2010-01-01":1, "2010-03-01":100 , "2010-12-01":110} | linear | 0.4                                  | kg   | -0.20       | 0.10               | 01/01/2009 | test var 1 |         |        |
+----------+----------+--------+-------------------------------------------------------+--------+--------------------------------------+------+-------------+--------------------+------------+------------+---------+--------+

Write code that references these variables and generates random distributions in pandas dataframes with `pint-pandas
<https://github.com/hgrecco/pint-pandas>`_ units.::

        repository = ParameterRepository()
        TableParameterLoader(filename='./test_v2.xlsx', excel_handler='xlrd').load_into_repo(sheet_name='Sheet1',
                                                                                             repository=repository)
        p = repository.get_parameter('a')

        settings = {'sample_size': 3, 'times': pd.date_range('2016-01-01', '2017-01-01', freq='MS'),
                    'sample_mean_value': False, 'use_time_series': True}
        val = p(settings)
        series = val.pint.m




