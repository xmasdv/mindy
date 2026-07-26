import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "patches" / "0002-mindy-mail-shell.patch"
UPSTREAM = ROOT / "vendor" / "gecko" / "comm"


class MailShellContractTests(unittest.TestCase):
    def test_patch_is_limited_to_documented_about3pane_seams(self):
        changed = [
            line.removeprefix("+++ b/")
            for line in PATCH.read_text().splitlines()
            if line.startswith("+++ b/")
        ]
        self.assertEqual(
            [
                "comm/mail/base/content/about3Pane.xhtml",
                "comm/mail/test/browser/folder-display/browser.toml",
                "comm/mail/test/browser/folder-display/browser_mindyMailShell.js",
                "comm/mail/themes/shared/jar.inc.mn",
                "comm/mail/themes/shared/mail/mindyMail.css",
            ],
            changed,
        )
        patch = PATCH.read_text()
        self.assertIn('getAttribute("data-mindy-shell")', patch)
        self.assertIn('getPropertyValue("--mindy-accent")', patch)
        self.assertIn('getElementById("messagePane")', patch)
        self.assertIn("@@ -0,0 +1,51 @@", patch)
        self.assertNotIn("BrowserTestUtils.isVisible", patch)
        self.assertIn("mindyStyle.sheet.cssRules", patch)

    def test_patch_has_no_unwired_status_or_grid_override(self):
        patch = PATCH.read_text()
        self.assertNotIn("mindyMailStatus", patch)
        self.assertNotIn("grid-template-columns", patch)
        self.assertIn("--folderPaneSplitter-width", patch)
        self.assertIn(":focus-visible", patch)

    def test_pinned_upstream_service_tests_are_receipted(self):
        receipt = json.loads((ROOT / "overlay" / "upstream-test-receipt.json").read_text())
        self.assertEqual("pass", receipt["runtimeStatus"])
        self.assertEqual(
            {
                "command": "./mach test comm/mail/test/browser/folder-display/browser_mindyMailShell.js",
                "checks": 10,
                "expected": 10,
                "unexpected": 0,
                "result": "OK",
                "build": "PASS 2m33s",
            },
            receipt["mindyRuntime"],
        )
        self.assertEqual(
            {
                "unifiedAccountScoping",
                "selectedIdentity",
                "searchEmpty",
                "archiveMove",
                "loadingError",
                "keyboardNarrowPanes",
                "setupFailure",
                "offlineIsolation",
                "calendarContacts",
            },
            set(receipt["cases"]),
        )
        self.assertTrue(all(receipt["cases"].values()))
        self.assertEqual(
            ["mail/test/browser/account/browser_accountHubManualConfig.js"],
            receipt["cases"]["setupFailure"],
        )
        self.assertEqual(
            [
                "mail/test/browser/quick-filter-bar/browser_filterLogic.js",
                "mail/test/browser/account/browser_accountHubManualConfig.js",
            ],
            receipt["cases"]["loadingError"],
        )
        tests = [test for paths in receipt["cases"].values() for test in paths]
        self.assertGreaterEqual(len(tests), 10)
        for test in tests:
            self.assertTrue((UPSTREAM / test).is_file(), test)

    def test_inherited_identity_and_adjacent_service_seams_remain(self):
        compose = (
            UPSTREAM / "mail/components/compose/content/MsgComposeCommands.js"
        ).read_text()
        spaces = (UPSTREAM / "mail/base/content/spacesToolbar.js").read_text()
        self.assertIn("gMsgCompose.identity != gCurrentIdentity", compose)
        self.assertIn('name: "calendar"', spaces)
        self.assertIn('name: "addressbook"', spaces)

    def test_inherited_unified_search_and_offline_seams_remain(self):
        page = (UPSTREAM / "mail/base/content/about3Pane.xhtml").read_text()
        controller = (UPSTREAM / "mail/base/content/about3Pane.js").read_text()
        self.assertIn('value="smart"', page)
        self.assertIn('id="placeholderNoMessages"', page)
        self.assertIn("Services.io.offline", controller)

    @unittest.skipIf(os.environ.get("MINDY_MAIL_VERIFY_CHILD"), "verifier child")
    def test_focused_verifier_reports_runtime_pass(self):
        result = subprocess.run(
            [sys.executable, "tools/verify-mvp.py", "mail"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("mail contract: PASS", result.stdout)
        self.assertIn("upstream runtime: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
