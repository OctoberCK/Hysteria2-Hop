import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


spec = importlib.util.spec_from_file_location(
    'hy2hop_platform', Path(__file__).resolve().parent.parent / 'hy2hop.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PlatformTests(unittest.TestCase):
    def check_release(self, text, missing=None):
        with patch.object(m.os, 'geteuid', return_value=0, create=True), \
                patch.object(m.Path, 'exists', return_value=True), \
                patch.object(m.Path, 'read_text', return_value=text), \
                patch.object(m.shutil, 'which', side_effect=lambda cmd: None if cmd == missing else '/usr/bin/' + cmd):
            m.prerequisites()

    def test_supported_releases(self):
        for text in (
            'ID=debian\nVERSION_ID="12"\nVERSION_CODENAME=bookworm\n',
            'ID="debian"\nVERSION_ID=12\n',
            "ID='debian'\nVERSION_ID='12'\n",
            'ID=ubuntu\nVERSION_ID="24.04"\n',
            'ID="ubuntu"\nVERSION_ID=24.04\n',
        ):
            with self.subTest(text=text):
                self.check_release(text)

    def test_unsupported_or_incomplete_releases(self):
        for text in (
            'ID=debian\nVERSION_ID="11"\n',
            'ID=debian\nVERSION_ID="13"\n',
            'ID=ubuntu\nVERSION_ID="22.04"\n',
            'ID=ubuntu\nVERSION_ID="12"\n',
            'ID=debian\nVERSION_ID="24.04"\n',
            'ID=kali\nID_LIKE=debian\nVERSION_ID="12"\n',
            'ID=debian\n',
            'VERSION_ID="12"\n',
            '',
        ):
            with self.subTest(text=text), self.assertRaisesRegex(RuntimeError, '仅支持'):
                self.check_release(text)

    def test_missing_system_commands(self):
        for cmd in ('systemctl', 'ss', 'ip', 'apt-get'):
            with self.subTest(cmd=cmd), self.assertRaisesRegex(RuntimeError, '缺少系统命令 ' + cmd):
                self.check_release('ID=debian\nVERSION_ID="12"\n', missing=cmd)

    def test_requires_root(self):
        with patch.object(m.os, 'geteuid', return_value=1000, create=True):
            with self.assertRaisesRegex(RuntimeError, 'root'):
                m.prerequisites()

    def test_requires_running_systemd(self):
        with patch.object(m.os, 'geteuid', return_value=0, create=True), \
                patch.object(m.Path, 'exists', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'systemd'):
                m.prerequisites()

    def test_command_locale_is_stable(self):
        result = Mock(returncode=0, stdout='Status: active\n')
        with patch.dict(os.environ, {'LC_ALL': 'zh_CN.UTF-8', 'LANG': 'zh_CN.UTF-8'}), \
                patch.object(m.subprocess, 'run', return_value=result) as run:
            self.assertIs(m.run(['ufw', 'status']), result)
            kwargs = run.call_args.kwargs
            self.assertEqual(kwargs['env']['LC_ALL'], 'C')
            self.assertEqual(kwargs['encoding'], 'utf-8')
            self.assertEqual(os.environ['LC_ALL'], 'zh_CN.UTF-8')

    def test_nftables_starts_before_hop_rules(self):
        unit = m.unit_content()
        after = next(line for line in unit.splitlines() if line.startswith('After='))
        self.assertIn('nftables.service', after.split('=', 1)[1].split())
        self.assertNotIn('Wants=nftables.service', unit)


if __name__ == '__main__':
    unittest.main()
