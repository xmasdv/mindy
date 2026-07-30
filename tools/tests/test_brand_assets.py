import hashlib
import importlib.util
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets" / "brand-production"
OUTPUT = ASSETS / "generated"
SPEC = importlib.util.spec_from_file_location("brand_assets", ROOT / "tools" / "generate_brand_assets.py")
brand = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(brand)


class BrandAssetTests(unittest.TestCase):
    def test_sources_are_editable_option_01_without_product_identity(self):
        for source in brand.SOURCES:
            text = (ASSETS / source).read_text(encoding="utf-8")
            with self.subTest(source=source):
                self.assertNotIn("<text", text.lower())
                self.assertFalse(any(name in text.lower() for name in ("thunderbird", "mozilla", "outlook")))
                ET.fromstring(text)
        mark = ET.fromstring((ASSETS / "mindy-mark.svg").read_bytes())
        self.assertEqual(("#051B40", "#0EA5A4", "#2563EB"), tuple(node.attrib["stroke"] for node in mark.findall("{*}path")))
        self.assertEqual((36.0, 30.0, 30.0), tuple(width for _, width, _ in brand.mark_geometry()))

    def test_manifest_hashes_dimensions_and_source_relationship(self):
        manifest = json.loads((OUTPUT / "manifest.json").read_text(encoding="utf-8"))
        expected = set(brand.PNG) | set(brand.ICO) | set(brand.BMP) | {"content/about-logo.svg", "content/about-wordmark.svg"}
        self.assertEqual(34, len(expected))
        self.assertEqual(expected, set(manifest["derivatives"]))
        self.assertEqual("tools/generate_brand_assets.py", manifest["generator"])
        for source in brand.SOURCES:
            self.assertEqual(hashlib.sha256((ASSETS / source).read_bytes()).hexdigest(), manifest["sources"][source])
        self.assertEqual((ASSETS / "mindy-mark.svg").read_bytes(), (OUTPUT / "content/about-logo.svg").read_bytes())
        self.assertEqual((ASSETS / "mindy-wordmark.svg").read_bytes(), (OUTPUT / "content/about-wordmark.svg").read_bytes())
        for path, details in manifest["derivatives"].items():
            data = (OUTPUT / path).read_bytes()
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256(data).hexdigest(), details["sha256"])
                if path.endswith(".png"):
                    self.assertEqual(brand.PNG[path], tuple(struct.unpack(">II", data[16:24])))
                if path.endswith(".bmp"):
                    self.assertEqual(brand.BMP[path], tuple(struct.unpack("<ii", data[18:26])))

    def test_png_alpha_and_ico_containers_are_valid(self):
        for path in brand.PNG:
            data = (OUTPUT / path).read_bytes()
            with self.subTest(path=path):
                self.assertEqual(b"\x89PNG\r\n\x1a\n", data[:8])
                self.assertEqual((8, 6), (data[24], data[25]))
                raw = zlib.decompress(data[data.index(b"IDAT") + 4:-12])
                self.assertIn(0, raw[4::4])
                self.assertIn(255, raw[4::4])
        for path, sizes in brand.ICO.items():
            data = (OUTPUT / path).read_bytes()
            with self.subTest(path=path):
                self.assertEqual((0, 1, len(sizes)), struct.unpack("<HHH", data[:6]))
                frames = [struct.unpack("<BBBBHHII", data[offset:offset + 16]) for offset in range(6, 6 + len(sizes) * 16, 16)]
                self.assertEqual(list(sizes), [frame[0] or 256 for frame in frames])
                self.assertTrue(all(data[frame[7]:frame[7] + 8] == b"\x89PNG\r\n\x1a\n" for frame in frames))
        self.assertTrue(all(len(sizes) > 1 for sizes in brand.ICO.values()))

    def test_regeneration_is_deterministic_and_rejects_drift(self):
        brand.generate(check=True)
        original = (OUTPUT / "default16.png").read_bytes()
        try:
            (OUTPUT / "default16.png").write_bytes(original + b"drift")
            with self.assertRaisesRegex(ValueError, "generated assets differ"):
                brand.generate(check=True)
            (OUTPUT / "default16.png").unlink()
            with self.assertRaisesRegex(ValueError, "generated assets differ"):
                brand.generate(check=True)
        finally:
            (OUTPUT / "default16.png").write_bytes(original)

    def test_master_geometry_and_style_causally_change_every_raster_family(self):
        for before, after in (("stroke-width=\"36\"", "stroke-width=\"42\""), ("#0EA5A4", "#14B8A6"), ("M96 336", "M104 336")):
            with self.subTest(change=before), tempfile.TemporaryDirectory() as temporary:
                isolated = Path(temporary) / "brand-production"
                shutil.copytree(ASSETS, isolated)
                master = isolated / "mindy-mark.svg"
                old_root, brand.ASSET_ROOT = brand.ASSET_ROOT, isolated
                try:
                    original = brand.derivatives()
                    master.write_text(master.read_text(encoding="utf-8").replace(before, after, 1), encoding="utf-8", newline="\n")
                    changed = brand.derivatives()
                finally:
                    brand.ASSET_ROOT = old_root
                for path in set(brand.PNG) | set(brand.ICO) | set(brand.BMP):
                    self.assertNotEqual(original[path], changed[path])

    def test_autocrlf_clone_keeps_hash_bound_files_and_generator_check(self):
        with tempfile.TemporaryDirectory() as temporary:
            clone = Path(temporary) / "clone"
            revision = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
            subprocess.run(["git", "clone", "--quiet", "--no-checkout", "--no-local", str(ROOT), str(clone)], check=True)
            subprocess.run(["git", "-C", str(clone), "-c", "core.autocrlf=true", "checkout", "--quiet", "--detach", revision], check=True)
            for path in ("mindy-mark.svg", "mindy-wordmark.svg", "generated/manifest.json"):
                self.assertNotIn(b"\r\n", (clone / "assets" / "brand-production" / path).read_bytes())
            result = subprocess.run([sys.executable, str(clone / "tools" / "generate_brand_assets.py"), "--check"], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
