#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
# from setuptools import setup
from distutils.core import setup


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()


install_requirements = [
    'openpyxl',
    'scipy',
    'xlrd',
    'pandas==0.24.2',
    'pint',
    'pint-pandas-fork',
    'numpy',
    'python-dateutil',
]

extra_requirements = {
    "test": ["pytest", "pytest-cov", "codecov", "coveralls", "nbval"],
    # @todo - remove xlrd dependency
    'excel': ['openpyxl', 'xlrd'],
    "units": [
        # below non-pypi references break pypi package
        # waiting for pint 0.12 release...
        # 'pint @        git+https://github.com/hgrecco/pint.git@f356379c15c1cb5d211c795872ac9e9284d2358f#egg=pint',
        # 'pint-pandas @ git+https://github.com/hgrecco/pint-pandas.git#egg=pint-pandas'
    ]
}

setup(
    setup_requires=['pbr'],
    pbr=True,
    name='eam-data-tools',
    version='1.4.4',
    license='Apache-2.0',
    description='Tool to read model data from a table',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='Dan Schien',
    author_email='daniel.schien@bristol.ac.uk',
    url='https://github.com/dschien/eam-data-tools',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Utilities',
    ],
    project_urls={
        'Documentation': 'https://eam-data-tools.readthedocs.io/',
        'Changelog': 'https://eam-data-tools.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/dschien/eam-data-tools/issues',
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires='>=3.6',
    install_requires=install_requirements,
    extras_require=extra_requirements,
    entry_points={
        'console_scripts': [
            'table-data-reader = table_data_reader.cli:main',
        ]
    },
)
