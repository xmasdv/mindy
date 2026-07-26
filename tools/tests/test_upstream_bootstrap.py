import importlib.util
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = ROOT / "tools" / "bootstrap-upstream.py"

def load_bootstrap():
    spec = importlib.util.spec_from_file_location("bootstrap_upstream", BOOTSTRAP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class BootstrapContractTests(unittest.TestCase):
    def setUp(self):
        self.module = load_bootstrap()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.vendor = self.root / "vendor"
        self.destination = self.vendor / "gecko"
        self.repository = "https://hg.mozilla.org/example"

    def test_repository_contract_is_root_resolved_and_immutable(self):
        lock = self.module.load_lock(ROOT / "sources.lock")
        self.assertEqual(lock["layout"]["gecko"], "vendor/gecko")
        self.assertRegex(lock["gecko"]["revision"], r"^[0-9a-f]{40}$")
        self.assertRegex(lock["comm"]["revision"], r"^[0-9a-f]{40}$")
        self.assertEqual(lock["compatibility"]["gecko_revision"], lock["gecko"]["revision"])

    def test_gecko_revision_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "GECKO_HEAD_REV"):
            self.module.verify_gecko_rev(
                "GECKO_HEAD_REPOSITORY: https://example.invalid/gecko\n"
                "GECKO_HEAD_REV: 0000000000000000000000000000000000000000\n",
                {"repository": "https://example.invalid/gecko", "revision": "1" * 40},
            )

    def test_patch_series_rejects_traversal_and_duplicates(self):
        (self.root / "one.patch").write_text("", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unsafe"):
            self.module.read_series("../outside.patch\n", self.root)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.module.read_series("one.patch\none.patch\n", self.root)

    def test_mozconfig_selects_mail_and_an_in_tree_object_directory(self):
        text = (ROOT / "config" / "mozconfig-pilot").read_text(encoding="utf-8")
        self.assertIn("ac_add_options --enable-project=comm/mail", text)
        self.assertIn("MOZ_OBJDIR=@TOPSRCDIR@/obj-mindy-pilot", text)

    def test_verify_mvp_bootstrap_runs_the_focused_contract(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "verify-mvp.py"), "bootstrap"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("bootstrap contract: PASS", result.stdout)

    def test_failed_clone_cleans_partial_destination_then_disables_bundles(self):
        commands = []

        def fail_once(command, **_kwargs):
            commands.append(command)
            if len(commands) == 1:
                self.destination.mkdir(parents=True)
                (self.destination / "partial").write_text("incomplete", encoding="utf-8")
                raise subprocess.CalledProcessError(255, command)
            self.assertFalse(self.destination.exists())

        with mock.patch.object(self.module, "run", side_effect=fail_once):
            self.module.clone_with_fallback(
                "hg", self.repository, self.destination, self.vendor
            )
        self.assertEqual(
            commands[0], ["hg", "clone", "-U", self.repository, self.destination]
        )
        self.assertEqual(commands[1][:3], ["hg", "--config", "ui.clonebundles=false"])
        self.assertEqual(commands[1][3:], commands[0][1:])

    def test_failed_retry_also_removes_its_partial_destination(self):
        def fail(command, **_kwargs):
            self.destination.mkdir(parents=True)
            raise subprocess.CalledProcessError(255, command)

        with mock.patch.object(self.module, "run", side_effect=fail):
            with self.assertRaises(subprocess.CalledProcessError):
                self.module.clone_with_fallback(
                    "hg", self.repository, self.destination, self.vendor
                )
        self.assertFalse(self.destination.exists())

    def test_cleanup_refuses_vendor_root_and_outside_paths(self):
        outside = self.root / "outside"
        self.vendor.mkdir()
        outside.mkdir()
        for unsafe in (self.vendor, outside):
            with self.subTest(unsafe=unsafe):
                with self.assertRaisesRegex(RuntimeError, "unsafe clone cleanup"):
                    self.module.cleanup_created_clone(unsafe, self.vendor)
                self.assertTrue(unsafe.is_dir())

    def test_cleanup_removes_read_only_clone_files(self):
        self.destination.mkdir(parents=True)
        read_only = self.destination / "store-data"
        read_only.write_text("partial", encoding="utf-8")
        os.chmod(read_only, stat.S_IREAD)
        self.module.cleanup_created_clone(self.destination, self.vendor)
        self.assertFalse(self.destination.exists())

if __name__ == "__main__":
    unittest.main()
