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

    def test3_version_warn(self):
        basmati_cmd('basmati -W version'.split())


class TestDownloadCmd(TestCase):
    def test1_download_no_args(self):
        # Gobble up stderr.
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            basmati_cmd('basmati download'.split())

    @patch('basmati.basmati_cmd.download_main')
    def test2_download(self, mock_download_main):
        basmati_cmd('basmati download -d ALL -r as'.split())
        mock_download_main.assert_called_with('ALL', 'as', False)

    @patch('basmati.basmati_cmd.download_main')
    def test3_download(self, mock_download_main):
        basmati_cmd('basmati download -d ALL -r as --delete-zip'.split())
        mock_download_main.assert_called_with('ALL', 'as', True)


class TestDemoCmd(TestCase):
    @patch('basmati.basmati_cmd.demo_main')
    def test1_demo(self, mock_demo_main):
        # raise Exception('mock not working')
        basmati_cmd('basmati demo'.split())
        mock_demo_main.assert_called()
