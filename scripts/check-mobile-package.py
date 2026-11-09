"""Fail a release check if native identity, icon assets or permissions drift.

Uses only Python's standard library; run on both release runners.
"""
from pathlib import Path
import hashlib
import json
import plistlib
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ANDROID = "{http://schemas.android.com/apk/res/android}"


class MobilePackageChecks(unittest.TestCase):
    def test_both_apps_use_beeqon_identity(self):
        config = (ROOT / "capacitor.config.ts").read_text()
        self.assertRegex(config, r"appId:\s*['\"]beeqon\.co\.za['\"]")
        self.assertRegex(config, r"appName:\s*['\"]Beeqon['\"]")
        self.assertIn("https://beeqon.co.za/auth", config)
        gradle = (ROOT / "android/app/build.gradle").read_text()
        self.assertIn('applicationId "beeqon.co.za"', gradle)
        xcode = (ROOT / "ios/App/App.xcodeproj/project.pbxproj").read_text()
        self.assertIn("PRODUCT_BUNDLE_IDENTIFIER = beeqon.co.za;", xcode)
        info = plistlib.loads((ROOT / "ios/App/App/Info.plist").read_bytes())
        self.assertEqual(info["CFBundleDisplayName"], "Beeqon")

    def test_android_artwork_is_generated_from_current_iphone_artwork(self):
        record = json.loads((ROOT / "scripts/mobile-icons.json").read_text())
        self.assertEqual(hashlib.sha256((ROOT / record["source"]).read_bytes()).hexdigest(),
                         record["source_sha256"], "Artwork changed: regenerate Android icons")
        self.assertEqual(len(record["files"]), 15)
        for path, expected in record["files"].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected,
                                 "Android icon changed independently: regenerate both from the source")
        for density in ["mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"]:
            for name in ["ic_launcher", "ic_launcher_round", "ic_launcher_foreground"]:
                self.assertIn(f"android/app/src/main/res/mipmap-{density}/{name}.png", record["files"])

    def test_launcher_references_and_microphone_permissions(self):
        manifest = ET.parse(ROOT / "android/app/src/main/AndroidManifest.xml").getroot()
        app = manifest.find("application")
        self.assertIsNotNone(app)
        self.assertEqual(app.get(ANDROID + "icon"), "@mipmap/ic_launcher")
        self.assertEqual(app.get(ANDROID + "roundIcon"), "@mipmap/ic_launcher_round")
        permissions = {node.get(ANDROID + "name") for node in manifest.findall("uses-permission")}
        self.assertIn("android.permission.CAMERA", permissions)
        self.assertIn("android.permission.RECORD_AUDIO", permissions)
        info = plistlib.loads((ROOT / "ios/App/App/Info.plist").read_bytes())
        for key in ["NSCameraUsageDescription", "NSPhotoLibraryUsageDescription", "NSMicrophoneUsageDescription"]:
            self.assertTrue(info.get(key))

    def test_release_workflows_validate_both_packages(self):
        for platform in ["android", "ios"]:
            workflow = (ROOT / f".github/workflows/{platform}-release.yml").read_text()
            self.assertIn("python3 scripts/check-mobile-package.py", workflow)
            self.assertIn(f"bunx cap sync {platform}", workflow)
        android = (ROOT / ".github/workflows/android-release.yml").read_text()
        self.assertRegex(android, r"packageName:\s*beeqon\.co\.za(?:\s|$)")


if __name__ == "__main__":
    unittest.main()