========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-table-data-reader/badge/?style=flat
    :target: https://readthedocs.org/projects/python-table-data-reader
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/dschien/python-table-data-reader.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/dschien/python-table-data-reader

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/dschien/python-table-data-reader?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/dschien/python-table-data-reader

.. |codecov| image:: https://codecov.io/gh/dschien/python-table-data-reader/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/dschien/python-table-data-reader

.. |version| image:: https://img.shields.io/pypi/v/table-data-reader.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/table-data-reader

.. |wheel| image:: https://img.shields.io/pypi/wheel/table-data-reader.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/table-data-reader

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/table-data-reader.svg
    :alt: Supported versions
    :target: https://pypi.org/project/table-data-reader

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/table-data-reader.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/table-data-reader

.. |commits-since| image:: https://img.shields.io/github/commits-since/dschien/python-table-data-reader/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/dschien/python-table-data-reader/compare/v0.0.0...master



.. end-badges

Tool to read model data from a table

* Free software: Apache Software License 2.0

Installation
============

::

    pip install table-data-reader

You can also install the in-development version with::

    pip install https://github.com/dschien/python-table-data-reader/archive/master.zip


Documentation
=============


https://python-table-data-reader.readthedocs.io/


Usage
=====

# Example
Given an excel file with rows similar to the below

| variable        | scenario | module                                      | distribution | param 1          | param 2 | param 3 | unit | start date | end date   | CAGR | ref date   | label      | comment | source |
|-----------------|----------|---------------------------------------------|--------------|------------------|---------|---------|------|------------|------------|------|------------|------------|---------|--------|
| a               |          | numpy.random                                | choice       | 1                |         |         | kg   | 01/01/2009 | 01/04/2009 | 0.10 | 01/01/2009 | test var 1 |         |        |
| b               |          | numpy.random                                | uniform      | 2                | 4       |         | -    |            |            |      |            | label      |         |        |
| c               |          | numpy.random                                | triangular   | 3                | 6       | 10      | -    |            |            |      |            | label      |         |        |
| d               |          | bottom_up_comparision.sampling_core_routers | Distribution | core_routers.csv |         |         | J/Gb |            |            |      |            | label      |         |        |
|                 |          |                                             |              |                  |         |         |      |            |            |      |            |            |         |        |
| a               | s1       | numpy.random                                | choice       | 2                |         |         |      |            |            |      |            | test var 1 |         |        |
| multiple choice |          | numpy.random                                | choice       | 1,2,3            |         |         | kg   | 01/01/2007 | 01/01/2009 |      |            | test var 1 |         |        |


You can run python/ numpy code that references these variables and generates random distributions.

For example, the following will initialise a variable `c` with a vector of size 2 with random values
 from a triangular distribution.

```
    np.random.seed(123)

    data = ParameterLoader.from_excel('test.xlsx', size=2, sheet_index=0)
    c = data['c']
>>> [ 7.08471918  5.45131111]
```

Other types of distributions include `choice` and `normal`. However you can specify any distribution from
numpy that takes up to three parameters to init.

You can also specify a .csv file with samples and an empiricial distribution function is generated
and variable values will be sampled from that.

## Scenarios
It is possible to define scenarios and have paramter values for  a variable change with each scenario.

```
    data = ParameterLoader.from_excel('test.xlsx', size=1, sheet_index=0)
    res = data['a'][0]

    assert res == 1.

    data.select_scenario('s1')
    res = data['a'][0]

    assert res == 2.
```

use `data.unselect_scenario()` to return to the default value.

## Pandas Dataframes

It is possible to define a time frame for distributions and have sample values change over time.

```
    # the time axis of our dataset
    times = pd.date_range('2009-01-01', '2009-04-01', freq='MS')
    # the sample axis our dataset
    samples = 2

    dfl = DataSeriesLoader.from_excel('test.xlsx', times, size=samples, sheet_index=0)
    res = dfl['a']

    assert res.loc[[datetime(2009, 1, 1)]][0] == 1
    assert np.abs(res.loc[[datetime(2009, 4, 1)]][0] - pow(1.1, 3. / 12)) < 0.00001
```

## Metadata
The contents of the rows is also contained in the metadata
```
    # the time axis of our dataset
    times = pd.date_range('2009-01-01', '2009-04-01', freq='MS')
    # the sample axis our dataset
    samples = 3

    dfl = DataSeriesLoader.from_excel('test.xlsx', times, size=samples, sheet_index=0)
    res = dfl['a']

    print(res._metadata)
```


## CAGR
It is possible to define compound annual growth to the variables. The growth will be applied relative to the ref date.



Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
