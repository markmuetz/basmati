import os
os.environ['HYDROSHEDS_DIR'] = 'dummy_hydrosheds_dir'
import contextlib
import io
from unittest import TestCase

from mock import patch

from basmati.basmati_cmd import basmati_cmd


class TestVersionCmd(TestCase):
    def test1_version(self):
        basmati_cmd('basmati version'.split())

    def test2_version_debug(self):
        basmati_cmd('basmati -D version'.split())

    def test3_version_bw(self):
        basmati_cmd('basmati -B version'.split())


class TestDownloadCmd(TestCase):
    def test1_download(self):
        # Gobble up stderr.
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            basmati_cmd('basmati download'.split())

    @patch('basmati.downloader.unzip_file')
    @patch('subprocess.run')
    def test2_download(self, mock_sprun, mock_unzip):
        basmati_cmd('basmati download -d ALL -r as'.split())
        mock_sprun.assert_called()
        mock_unzip.assert_called()

    @patch('basmati.downloader.download_main')
    def test3_download(self, mock_download_main):
        raise Exception('mock not working')
        basmati_cmd('basmati download -d ALL -r as'.split())
        mock_download_main.assert_called()


class TestDemoCmd(TestCase):
    # Why is this not working??
    @patch('basmati.basmati_demo.demo_main')
    def test1_demo(self, mock_demo_main):
        raise Exception('mock not working')
        basmati_cmd('basmati demo'.split())
        mock_demo_main.assert_called()
