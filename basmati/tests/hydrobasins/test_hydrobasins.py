from pathlib import Path
from unittest import TestCase
import random

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
        # Check 0s.
        (43199, 43100, True),
        (43199, 43101, True),
        (43199, 43102, False),
        (43199, 43120, False),
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
        assert hasattr(self.gdf, 'find_next_level_smaller')
        assert hasattr(self.gdf, 'find_next_level_larger')
        assert hasattr(self.gdf, 'area_select')

    def test2_hb_downstream(self):
        id_dist_max = self.gdf['DIST_MAIN'].idxmax()
        furthest = self.gdf.loc[id_dist_max]

        downstream_of_furthest = self.gdf.find_downstream(furthest.PFAF_ID)
        assert furthest.MAIN_BAS == downstream_of_furthest.iloc[0].HYBAS_ID

        downstream_pfaf_ids = downstream_of_furthest.PFAF_ID.values
        for downstream_pfaf_id in downstream_pfaf_ids:
            assert is_downstream(furthest.PFAF_ID, downstream_pfaf_id)

    def test3_hb_upstream(self):
        id_dist_max = self.gdf['DIST_MAIN'].idxmax()
        furthest = self.gdf.loc[id_dist_max]

        coast = self.gdf.find_downstream(furthest.PFAF_ID).iloc[0]
        upstream_of_coast = self.gdf.find_upstream(coast.PFAF_ID)
        upstream_pfaf_ids = upstream_of_coast.PFAF_ID.values
        for upstream_pfaf_id in upstream_pfaf_ids:
            assert is_downstream(upstream_pfaf_id, coast.PFAF_ID)

    def test4_hb_level_larger(self):
        id_dist_max = self.gdf['DIST_MAIN'].idxmax()
        furthest = self.gdf.loc[id_dist_max]
        print(furthest.PFAF_ID)
        curr_row = furthest
        curr_level = furthest.LEVEL
        while curr_level > 1:
            curr_level -= 1
            gdf_larger = self.gdf.find_next_level_larger(curr_row.PFAF_ID)
            assert len(gdf_larger) == 1
            row_larger = gdf_larger.iloc[0]
            assert row_larger.LEVEL == curr_level
            assert row_larger.PFAF_STR == curr_row.PFAF_STR[:-1]
            curr_row = row_larger

    def test5_hb_level_smaller(self):
        curr_row = self.gdf[self.gdf.PFAF_ID == 4].iloc[0]
        curr_level = 1
        while curr_level < 6:
            curr_level += 1
            gdf_smaller = self.gdf.find_next_level_smaller(curr_row.PFAF_ID)
            if not len(gdf_smaller):
                break
            assert (gdf_smaller.LEVEL.values == curr_level).all()
            curr_row = gdf_smaller.iloc[random.randint(0, len(gdf_smaller) - 1)]
