from pathlib import Path
from unittest import TestCase

from basmati.hydrosheds import load_hydrobasins_geodataframe, is_downstream

HYDROSHEDS_DIR = Path('~/HydroSHEDS').expanduser()


def test_is_downstream():
    for pfaf_id_a, pfaf_id_b, expected_res in [
        # https://en.wikipedia.org/wiki/Pfafstetter_Coding_System#Properties
        (8835, 8833, True),
        (8835, 8811, True),
        (8835, 8832, False),
        (8835, 8821, False),
        (8835, 9135, False),
        # Other.
        (99, 77, True),
        (89, 81, True),
        (9, 7, True),
        (9, 8, False),
        # More digits upstream.
        (99, 7, True),
        (99, 8, False),
        # More digits downstream.
        (9, 77, True),
        (9, 69, False),
        # Check str OK.
        ('89', 81, True),
        (89, '81', True),
        ('89', '81', True),
    ]:
        yield check_is_downstream, pfaf_id_a, pfaf_id_b, expected_res


def check_is_downstream(pfaf_id_a, pfaf_id_b, expected_res):
    print(f'{pfaf_id_b} is downstream of {pfaf_id_a}: {expected_res}')
    assert is_downstream(pfaf_id_a, pfaf_id_b) == expected_res


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

