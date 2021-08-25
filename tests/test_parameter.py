import datetime
import unittest

import numpy as np
import pandas as pd
from scipy import stats

from table_data_reader import Parameter

import pint

class ParameterTestCase(unittest.TestCase):
    def test_distribution_generate_values(self):
        p = Parameter('test', module_name='numpy.random', distribution_name='normal', param_a=0, param_b=.1)
        settings = {'sample_size': 32}
        a = p(settings)

        assert abs(stats.shapiro(a)[0] - 0.9) < 0.1

    @unittest.skip('no assertion')
    def test_ExponentialGrowthTimeSeriesDistributionFunctionParameter_generate_values(self):
        p = Parameter('test', module_name='numpy.random', distribution_name='normal',
                      param_a=0,
                      param_b=.1)

        settings = {
            'use_time_series': True,
            'times': pd.date_range('2009-01-01',
                                   '2009-03-01',
                                   freq='MS'),
            'sample_size': 5,
            'cagr': 0.1}
        a = p(settings)

        print(a)
        # assert abs(stats.shapiro(a)[0] - 0.9) < 0.1

    @unittest.skip('no assertion')
    def test_ExponentialGrowthTimeSeriesDistributionFunctionParameter_generate_values_uniform(self):
        p = Parameter('test', module_name='numpy.random', distribution_name='uniform',
                      param_a=1,
                      param_b=2)

        settings = {
            'use_time_series': True,
            'times': pd.date_range('2009-01-01',
                                   '2009-03-01',
                                   freq='MS'),
            'sample_size': 5,
            'cagr': 1}
        a = p(settings)

        print(a)
        # assert abs(stats.shapiro(a)[0] - 0.9) < 0.1

    def test_ExponentialGrowthTimeSeriesDistributionFunctionParameter_generate_values_uniform_mean(self):
        p = Parameter('test', module_name='numpy.random', distribution_name='uniform',
                      param_a=1, param_b=2, cagr=.1)

        settings = {
            'use_time_series': True,
            'times': pd.date_range('2009-01-01', '2010-01-01', freq='MS'),
            'sample_size': 1,
            'sample_mean_value': True}
        a = p(settings)

        assert a.iloc[0] * 1.1 == a.iloc[-1]

    def test_normal_zero_variance(self):
        p = Parameter('a', module_name='numpy.random', distribution_name='normal', param_a=0,
                      param_b=0, )
        q = Parameter('b', module_name='numpy.random', distribution_name='normal', param_a=0,
                      param_b=0)
        settings = {'sample_size': 64, }
        a = p(settings) * q(settings)
        # print(a)
        assert abs(stats.shapiro(a)[0] - 0.9) < 0.1

    def test_get_mean_uniform(self):
        p = Parameter('a', module_name='numpy.random', distribution_name='uniform', param_a=2,
                      param_b=4, )
        settings = {
            'sample_size': 5,
            'sample_mean_value': True}
        val = p(settings)
        # print(val)
        assert (val == 3).all()

    def test_get_mean_normal_timeseries(self):
        p = Parameter('test', module_name='numpy.random', distribution_name='normal',
                      param_a=3.,
                      param_b=.1, )

        settings = {
            'use_time_series': True,
            'times': pd.date_range('2009-01-01',
                                   '2009-03-01',
                                   freq='MS'),
            'sample_size': 5,
            'cagr': 0,
            'sample_mean_value': True}
        val = p(settings)
        # print(val)
        assert (val == 3).all()

    @unittest.skip('no assertion')
    def test_get_mean_normal(self):
        p = Parameter('a', module_name='numpy.random', distribution_name='normal', param_a=3, param_b=4, )

        val = p()
        # print(val)
        # assert (val == 3).all()

    def test_get_mean_choice(self):
        p = Parameter('a', module_name='numpy.random', distribution_name='choice', param_a=3, param_b=4, )
        settings = {'sample_mean_value': True, 'sample_size': 3}
        val = p(settings)
        # print(val)
        assert (val == 3.5).all()

    def test_get_mean_numerically(self):
        p = Parameter('a', module_name='numpy.random', distribution_name='normal', param_a=3,
                      param_b=4)
        settings = {'sample_mean_value': True, 'sample_size': 3}
        val = p(settings)
        # print(val)
        assert (val == 3).all()

    def test_returned_series_is_correct(self):
        p = Parameter('test',
                      with_pint_units=True,
                      unit='kg',
                      version=2,
                      ref_date=datetime.datetime(2019, 1, 1),
                      type='exp',
                      size=3,
                      growth_factor=0,
                      initial_value_proportional_variation=0,
                      ef_growth_factor=0,
                      **{'ref value': {
                          'A': 1,
                          'B': 2,
                          'C': 4
                      }})

        dates = pd.date_range('2009-01-01', '2009-03-01', freq='MS')
        groups = ['A', 'B', 'C']

        settings = {
            'use_time_series': True,
            'sample_mean_value': True,
            'with_group': True,
            'group_vars': ['test'],
            'groupings': groups,
            'times': dates
        }

        val = p(settings)

        expected_index = pd.MultiIndex.from_product([dates, range(3), groups], names=['time', 'samples', 'group'])

        expected = pd.Series(index=expected_index, data=np.tile([1, 2, 4], 9), dtype='pint[kg]')

        pd.testing.assert_series_equal(val, expected)


if __name__ == '__main__':
    unittest.main()
