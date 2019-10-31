import os
import tempfile
from pathlib import Path
from unittest import TestCase

from mock import patch, call

from basmati.hydrosheds import load_hydrobasins_geodataframe

HYDROSHEDS_DIR = Path('~/HydroSHEDS').expanduser()


class TestHydrobasinsLoad(TestCase):
    def test0_load_bad_dir(self):
        with self.assertRaises(OSError):
            gdf = load_hydrobasins_geodataframe('bad_dir', 'as', [1])

    def test0_load_bad_region(self):
        with self.assertRaises(OSError):
            gdf = load_hydrobasins_geodataframe(HYDROSHEDS_DIR, 'minmus', [1])

    def test1_load_level1(self):
        gdf = load_hydrobasins_geodataframe(HYDROSHEDS_DIR, 'as', [1])
        assert len(gdf) == 1

    def test2_load_default(self):
        gdf = load_hydrobasins_geodataframe(HYDROSHEDS_DIR, 'as')
        assert len(gdf.LEVEL.unique()) == 6

    def test3_load_all(self):
        gdf = load_hydrobasins_geodataframe(HYDROSHEDS_DIR, 'as', range(1, 13))
        assert len(gdf.LEVEL.unique()) == 12


class TestHydrobasinsOperations(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gdf = load_hydrobasins_geodataframe(HYDROSHEDS_DIR, 'as')

    @classmethod
    def tearDownClass(cls):
        cls.gdf = None

    def test1_check_load_methods(self):
        """Methods added to geodataframe by load"""
        assert hasattr(self.gdf, 'find_downstream')
        assert hasattr(self.gdf, 'find_upstream')
        assert hasattr(self.gdf, 'find_next_smaller')
        assert hasattr(self.gdf, 'find_next_larger')
        assert hasattr(self.gdf, 'area_select')

