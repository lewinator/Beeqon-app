"""Generate Android launcher variants from the same artwork used by iPhone.

Run with Python 3 and Pillow: python3 scripts/generate-mobile-icons.py
"""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png"
RES = ROOT / "android/app/src/main/res"
DENSITIES = {"mdpi": (48, 108), "hdpi": (72, 162), "xhdpi": (96, 216),
             "xxhdpi": (144, 324), "xxxhdpi": (192, 432)}


def generate():
    source = Image.open(SOURCE).convert("RGBA")
    files = {}
    for density, (legacy_size, adaptive_size) in DENSITIES.items():
        folder = RES / f"mipmap-{density}"
        folder.mkdir(parents=True, exist_ok=True)
        legacy = source.resize((legacy_size, legacy_size), Image.Resampling.LANCZOS)
        # Android masks 108dp layers. Keep the complete artwork within the central
        # 72dp, with the existing artwork's own whitespace providing safe-area inset.
        foreground = Image.new("RGBA", (adaptive_size, adaptive_size))
        art_size = adaptive_size * 2 // 3
        artwork = source.resize((art_size, art_size), Image.Resampling.LANCZOS)
        offset = (adaptive_size - art_size) // 2
        foreground.paste(artwork, (offset, offset))
        for name, image in [("ic_launcher.png", legacy),
                            ("ic_launcher_round.png", legacy),
                            ("ic_launcher_foreground.png", foreground)]:
            path = folder / name
            image.save(path)
            files[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    record = {"source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "files": files}
    (ROOT / "scripts/mobile-icons.json").write_text(json.dumps(record, indent=2) + "\n")
    print("Generated 15 Android icon variants from the iPhone Beeqon artwork.")


if __name__ == "__main__":
    generate()