=====
Usage
=====

**The below refers to table format v1 and needs updating.**

To use table-data-reader in a project::

	import table_data_reader


For example, the following will initialise a variable `c` with a vector of size 2 with random values
 from the distribution defined in the excel file::


    np.random.seed(123)

    data = ParameterLoader.from_excel('test.xlsx', size=2, sheet_index=0)
    c = data['c']
    >>> [ 7.08471918  5.45131111]


Other types of distributions include `choice` and `normal`. However you can specify any distribution from
numpy that takes up to three parameters to init.

You can also specify a .csv file with samples and an empiricial distribution function is generated
and variable values will be sampled from that.

Scenarios
=========
It is possible to define scenarios and have paramter values for  a variable change with each scenario.::


    data = ParameterLoader.from_excel('test.xlsx', size=1, sheet_index=0)
    res = data['a'][0]

    assert res == 1.

    data.select_scenario('s1')
    res = data['a'][0]

    assert res == 2.

use `data.unselect_scenario()` to return to the default value.

Pandas Dataframes
=================

It is possible to define a time frame for distributions and have sample values change over time.::

    # the time axis of our dataset
    times = pd.date_range('2009-01-01', '2009-04-01', freq='MS')
    # the sample axis our dataset
    samples = 2

    dfl = DataSeriesLoader.from_excel('test.xlsx', times, size=samples, sheet_index=0)
    res = dfl['a']

    assert res.loc[[datetime(2009, 1, 1)]][0] == 1
    assert np.abs(res.loc[[datetime(2009, 4, 1)]][0] - pow(1.1, 3. / 12)) < 0.00001


Metadata
========
The contents of the rows is also contained in the metadata::

    # the time axis of our dataset
    times = pd.date_range('2009-01-01', '2009-04-01', freq='MS')
    # the sample axis our dataset
    samples = 3

    dfl = DataSeriesLoader.from_excel('test.xlsx', times, size=samples, sheet_index=0)
    res = dfl['a']

    print(res._metadata)


CAGR
---
It is possible to define compound annual growth to the variables. The growth will be applied relative to the ref date.

