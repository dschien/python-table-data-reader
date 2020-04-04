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

.. |requires| image:: https://requires.io/github/dschien/python-table-data-reader/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/dschien/python-table-data-reader/requirements/?branch=master

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
