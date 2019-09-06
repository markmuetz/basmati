#!/usr/bin/env python
import os

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

from basmati.version import get_version


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except:
        return ''

setup(
    name='basmati',
    version=get_version(),
    description='BAsin-Scale Model Assessment Tool',
    long_description=read('README.md'),
    author='Mark Muetzelfeldt',
    author_email='mark.muetzelfeldt@reading.ac.uk',
    maintainer='Mark Muetzelfeldt',
    maintainer_email='mark.muetzelfeldt@reading.ac.uk',
    packages=[
        'basmati',
        'basmati.cmds',
        ],
    scripts=[
        'bin/basmati',
        ],
    python_requires='>=3.6',
    install_requires=[
        # 'numpy',
        # 'scipy',
        # 'pandas',
        # 'geopandas',
        # 'rasterio',
        # 'matplotlib',
        # 'configparser',
        # 'iris',
        ],
    extras_require={
        # 'display': ['matplotlib'],
    },
    # package_data={'basmati.data': ['files/vn10.5/STASHmaster*'],
    #     },
    url='https://github.com/markmuetz/basmati',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        ],
    keywords=[''],
    )
