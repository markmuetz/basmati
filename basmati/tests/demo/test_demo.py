import os
import tempfile
from pathlib import Path
from unittest import TestCase

from mock import patch

from basmati.basmati_errors import BasmatiError
from basmati.basmati_demo import demo_main

HYDROSHEDS_DIR = Path('~/HydroSHEDS').expanduser()


class TestDemo(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.origdir = os.getcwd()
        cls.tempdir = tempfile.TemporaryDirectory()
        os.chdir(cls.tempdir.name)

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()
        os.chdir(cls.origdir)

    def test0_check_HYDROSHEDS_DIR_env(self):
        """Check all as (Asia) HydroSHEDS files present in ~/HydroSHEDS"""
        assert HYDROSHEDS_DIR.exists()
        assert (HYDROSHEDS_DIR / 'as_dem_30s.bil').exists()
        for level in range(1, 13):
            assert (HYDROSHEDS_DIR / f'hybas_as_lev{level:02}_v1c.dbf').exists()
            assert (HYDROSHEDS_DIR / f'hybas_as_lev{level:02}_v1c.prj').exists()
            assert (HYDROSHEDS_DIR / f'hybas_as_lev{level:02}_v1c.shp').exists()

    @patch.dict('os.environ', {'HYDROSHEDS_DIR': ''})
    def test1_demo_main_no_HYDROSHEDS_DIR_env(self):
        with self.assertRaises(BasmatiError):
            demo_main()

    @patch.dict('os.environ', {'HYDROSHEDS_DIR': str(HYDROSHEDS_DIR)})
    def test2_demo_main(self):
        demo_main()
        assert Path('basmati_demo_figs').exists()
        assert len(list(Path('basmati_demo_figs').glob('*.png'))) == 13
