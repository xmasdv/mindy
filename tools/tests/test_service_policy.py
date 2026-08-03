import hashlib
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "patches" / "0007-mindy-service-policy-baseline.patch"
MOZ_FIXTURE = ROOT / "tools/tests/fixtures/0004-moz.configure-preimage"
APPROVED_TARGETS = (
    "comm/mail/moz.configure",
    "comm/mail/app/profile/all-thunderbird.js",
    "comm/mailnews/mailnews.js",
    "toolkit/content/aboutTelemetry.js",
    "comm/mail/base/content/aboutDialog.xhtml",
    "comm/mail/base/content/aboutRights.xhtml",
    "comm/mail/base/content/buildconfig.html",
    "comm/mail/base/content/overrides/app-license.html",
    "comm/mail/base/content/messenger.xhtml",
    "comm/mailnews/base/content/msgAccountCentral.xhtml",
    "comm/mail/components/preferences/compose.inc.xhtml",
    "comm/mail/components/preferences/qrExport.inc.xhtml",
    "comm/mail/components/preferences/privacy.inc.xhtml",
    "comm/mail/base/content/utilityOverlay.js",
    "devtools/server/actors/inspector/event-collector.js",
    "devtools/server/actors/utils/inactive-property-helper.js",
    "devtools/client/shared/stylesheet-utils.js",
)
ACCOUNT_PREFS = (
    "identity.fxaccounts.autoconfig.uri",
    "identity.fxaccounts.remote.root",
    "identity.fxaccounts.oauth.enabled",
    "identity.fxaccounts.remote.profile.uri",
    "identity.fxaccounts.remote.oauth.uri",
    "identity.sync.tokenserver.uri",
    "mail.accounthub.enabled",
)
DENIED_SERVICE_HOSTS = (
    "mozilla.com",
    "mozilla.net",
    "mozilla.org/thunderbird/legal/privacy",
    "mozilla.org/en-us/privacy/thunderbird",
    "thunderbird.net",
)


def added_lines(text):
    return "\n".join(line[1:] for line in text.splitlines() if line.startswith("+") and not line.startswith("+++"))


def changed_pref_names(text):
    names = set()
    for line in text.splitlines():
        if line.startswith(("+pref(", "-pref(", "+ pref(", "- pref(")):
            match = re.search(r'pref\("([^"]+)"', line)
            if match:
                names.add(match.group(1))
    return names


class ServicePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bytes = PATCH.read_bytes()
        cls.patch = cls.bytes.decode("utf-8")
        cls.added = added_lines(cls.patch)

    def test_patch_is_canonical_and_targets_only_service_policy_sources(self):
        self.assertNotIn(b"\r", self.bytes)
        targets = tuple(line[6:] for line in self.patch.splitlines() if line.startswith("+++ b/"))
        self.assertEqual(APPROVED_TARGETS, targets)

    def test_patch_adds_no_product_service_endpoints(self):
        self.assertNotRegex(self.added, r"https?://")
        lowered = self.added.lower()
        for host in DENIED_SERVICE_HOSTS:
            with self.subTest(host=host):
                self.assertNotIn(host, lowered)

    def test_patch_disables_crashreporter_and_datareporting_policy(self):
        for value in (
            'imply_option("--enable-crashreporter", False)',
            'imply_option("MOZ_SERVICES_HEALTHREPORT", False)',
            'imply_option("MOZ_TELEMETRY_REPORTING", False)',
            'pref("datareporting.healthreport.uploadEnabled", false);',
            'pref("datareporting.policy.dataSubmissionEnabled", false);',
            'pref("datareporting.policy.dataSubmissionPolicyBypassNotification", true);',
            'pref("toolkit.telemetry.server", "");',
            'pref("breakpad.reportURL", "");',
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.added)

    def test_patch_neutralizes_remaining_validator_service_endpoints(self):
        for value in (
            'pref("extensions.geckoProfiler.acceptedExtensionIds", "");',
            'pref("mail.cloud_files.learn_more_url", "");',
            'pref("mail.ignore_thread.learn_more_url", "");',
            'pref("mailnews.auto_config_url", "");',
            'pref("mailnews.auto_config.addons_url", "");',
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.added)
        self.assertNotIn('pref("extensions.webextensions.restrictedDomains", "");', self.added)
        self.assertNotIn("extensions.webextensions.restrictedDomains", changed_pref_names(self.patch))

    def test_patch_neutralizes_packaged_chrome_resource_endpoints(self):
        for value in (
            'const DEFAULT_SYMBOL_SERVER_URI = "";',
            "img-src chrome: data: moz-icon:; connect-src *",
            'origin: "",',
            "// about this in the related design discussion and",
            "// See Bug 1582786 for context.",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.added)
        self.assertGreaterEqual(self.added.count('href=""'), 12)
        self.assertGreaterEqual(self.added.count('openUILink("", event);'), 5)

    def test_patch_does_not_modify_account_setup_autoconfig_or_oauth_prefs(self):
        changed = changed_pref_names(self.patch)
        for pref_name in ACCOUNT_PREFS:
            with self.subTest(pref_name=pref_name):
                self.assertNotIn(pref_name, changed)

    def test_patch_applies_after_the_existing_ordered_preimage(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            moz = root / "comm/mail/moz.configure"
            moz.parent.mkdir(parents=True)
            moz.write_bytes(MOZ_FIXTURE.read_bytes())
            result = subprocess.run(
                ["git", "apply", str(ROOT / "patches/0004-mindy-identity-namespace.patch")],
                cwd=root,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            result = subprocess.run(
                ["git", "apply", "--check", "--include=comm/mail/moz.configure", str(PATCH)],
                cwd=root,
                text=True,
                capture_output=True,
            )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_series_appends_service_policy_patch_after_windows_identity(self):
        names = tuple(
            line.split("#", 1)[0].strip()
            for line in (ROOT / "patches/series").read_text(encoding="utf-8").splitlines()
            if line.split("#", 1)[0].strip()
        )
        self.assertEqual("0006-mindy-windows-exe-identity.patch", names[-2])
        self.assertEqual("0007-mindy-service-policy-baseline.patch", names[-1])
        self.assertEqual(hashlib.sha256(PATCH.read_bytes()).hexdigest(), hashlib.sha256((ROOT / "patches" / names[-1]).read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
