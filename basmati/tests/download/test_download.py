import os
import tempfile
from pathlib import Path
from unittest import TestCase

from mock import patch, call

from basmati.basmati_errors import BasmatiError
from basmati.downloader import (download_main, HydroshedsDownloader, UnrecognizedRegionError,
                                HYDROBASINS_REGIONS)


class TestDownloadMainUnit(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.origdir = os.getcwd()
        cls.tempdir = tempfile.TemporaryDirectory()
        os.chdir(cls.tempdir.name)

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()
        os.chdir(cls.origdir)

    @patch.dict('os.environ', {'HYDROSHEDS_DIR': ''})
    def test1_download_main_no_HYDROSHEDS_DIR_env(self):
        with self.assertRaises(BasmatiError):
            download_main('hydrobasins_all_levels', 'as', False)

    @patch.dict('os.environ', {'HYDROSHEDS_DIR': 'dummy_dir'})
    def test2_download_main_bad_dataset(self):
        with self.assertRaises(BasmatiError):
            download_main('hydrobasins_', 'as', False)

    @patch.dict('os.environ', {'HYDROSHEDS_DIR': 'dummy_dir'})
    def test3_download_main_bad_region(self):
        with self.assertRaises(BasmatiError):
            download_main('hydrobasins_all_levels', 'moon', False)

    @patch.dict('os.environ', {'HYDROSHEDS_DIR': 'dummy_dir'})
    @patch.object(HydroshedsDownloader, 'download_hydrosheds_dem_30s')
    def test4_download_main(self, mock_dl):
        download_main('hydrosheds_dem_30s', 'as', False)
        mock_dl.assert_called_once_with('as')

    @patch.dict('os.environ', {'HYDROSHEDS_DIR': 'dummy_dir'})
    @patch.object(HydroshedsDownloader, 'download_hydrosheds_dem_30s')
    def test5_download_main(self, mock_dl):
        download_main('hydrosheds_dem_30s', 'ALL', False)
        mock_dl.mock_calls = [call(r) for r in HYDROBASINS_REGIONS]

    @patch.dict('os.environ', {'HYDROSHEDS_DIR': 'dummy_dir'})
    @patch.object(HydroshedsDownloader, 'download_hydrobasins_all_levels')
    def test6_download_main(self, mock_dl):
        download_main('hydrobasins_all_levels', 'eu', False)
        mock_dl.assert_called_once_with('eu')

    @patch.dict('os.environ', {'HYDROSHEDS_DIR': 'dummy_dir'})
    @patch.object(HydroshedsDownloader, 'download_hydrobasins_all_levels')
    def test7_download_main(self, mock_dl):
        download_main('hydrobasins_all_levels', 'ALL', False)
        mock_dl.mock_calls = [call(r) for r in HYDROBASINS_REGIONS]


class TestHydroshedsDownloaderUnit(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.origdir = os.getcwd()
        cls.tempdir = tempfile.TemporaryDirectory()
        os.chdir(cls.tempdir.name)

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()
        os.chdir(cls.origdir)

    def test1_hs_dl_no_HYDROSHEDS_DIR(self):
        with self.assertRaises(BasmatiError):
            dl = HydroshedsDownloader('not_there', False)

    def test2_hs_dl(self):
        dl = HydroshedsDownloader(self.tempdir.name, False)

    def test3_hs_dl(self):
        dl = HydroshedsDownloader(self.tempdir.name, False)
        with self.assertRaises(UnrecognizedRegionError):
            dl.download_hydrobasins_all_levels('mordor')

    @patch('basmati.downloader.download_file_wget')
    def test4_hs_dl(self, mock_dl):
        dl = HydroshedsDownloader(self.tempdir.name, False)
        dl.download_hydrobasins_all_levels('as')
        mock_dl.assert_called()

    def test5_hs_dl(self):
        dl = HydroshedsDownloader(self.tempdir.name, False)
        with self.assertRaises(UnrecognizedRegionError):
            dl.download_hydrosheds_dem_30s('mordor')

    @patch('basmati.downloader.download_file_wget')
    def test6_hs_dl(self, mock_dl):
        dl = HydroshedsDownloader(self.tempdir.name, False)
        dl.download_hydrosheds_dem_30s('as')
        mock_dl.assert_called()


class TestHydroshedsDownloader(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.origdir = os.getcwd()
        cls.tempdir = tempfile.TemporaryDirectory()
        os.chdir(cls.tempdir.name)
        cls.hydrosheds_dir = Path(cls.tempdir.name)

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()
        os.chdir(cls.origdir)

    def test1_hs_dl(self):
        # Don't delete zipfile
        dl = HydroshedsDownloader(self.tempdir.name, False)
        dl.download_hydrobasins_all_levels('as')

    def test2_check_dir_state(self):
        # Check all Asia hydrobasins files exist, including zipfile (not deleted).
        assert (self.hydrosheds_dir / f'hybas_as_lev01-12_v1c.zip').exists()
        for level in range(1, 13):
            assert (self.hydrosheds_dir / f'hybas_as_lev{level:02}_v1c.dbf').exists()
            assert (self.hydrosheds_dir / f'hybas_as_lev{level:02}_v1c.prj').exists()
            assert (self.hydrosheds_dir / f'hybas_as_lev{level:02}_v1c.shp').exists()

    def test3_hs_dl(self):
        # Delete zipfile
        dl = HydroshedsDownloader(self.tempdir.name, True)
        dl.download_hydrosheds_dem_30s('eu')

    def test4_check_dir_state(self):
        # Check Europe hydrosheds DEM file exists, and zipfile deleted.
        assert (self.hydrosheds_dir / 'eu_dem_30s.bil').exists()
        assert not (self.hydrosheds_dir / 'eu_dem_30s.zip').exists()
