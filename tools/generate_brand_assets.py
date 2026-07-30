#!/usr/bin/env python3
"""Generate the portable Mindy option-01 branding derivatives."""

import argparse
import hashlib
import json
import re
import struct
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets" / "brand-production"
OUTPUT = ASSET_ROOT / "generated"
SOURCES = ("mindy-mark.svg", "mindy-wordmark.svg")
DEFAULTS = {f"default{size}.png": (size, 23 if size == 24 else size) for size in (16, 22, 24, 32, 48, 64, 128, 256)}
PNG = {**DEFAULTS, "VisualElements_70.png": (126, 126), "VisualElements_150.png": (270, 270),
       "msix/Assets/Calendar44x44.png": (44, 44), "msix/Assets/Email44x44.png": (44, 44),
       "msix/Assets/LargeTile.scale-200.png": (620, 620), "msix/Assets/News44x44.png": (44, 44),
       "msix/Assets/SmallTile.scale-200.png": (142, 142), "msix/Assets/Square150x150Logo.scale-200.png": (300, 300),
       "msix/Assets/Square44x44Logo.altform-lightunplated_targetsize-256.png": (256, 256),
       "msix/Assets/Square44x44Logo.altform-unplated_targetsize-256.png": (256, 256),
       "msix/Assets/Square44x44Logo.scale-200.png": (88, 88), "msix/Assets/Square44x44Logo.targetsize-256.png": (256, 256),
       "msix/Assets/StoreLogo.scale-200.png": (100, 100), "msix/Assets/Wide310x150Logo.scale-200.png": (620, 300),
       "content/about-logo.png": (192, 192), "content/about-logo@2x.png": (384, 384), "content/about.png": (300, 236)}
ICO = {name: (16, 32, 48, 64, 128, 256) for name in ("addressbook.ico", "writeMessage.ico", "newmail.ico", "messengerWindow.ico")}
BMP = {"wizHeader.bmp": (150, 57), "wizHeaderRTL.bmp": (150, 57), "wizWatermark.bmp": (164, 314)}
SYMBOLIC = "TB-symbolic.svg"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def svg_path(data):
    require(re.fullmatch(r"[MLVQ0-9.\s-]+", data) is not None, "unsupported SVG path")
    tokens = re.findall(r"[MLVQ]|-?\d+(?:\.\d+)?", data)
    position, command, index, segments = (0.0, 0.0), None, 0, []
    lengths = {"M": 2, "L": 2, "V": 1, "Q": 4}
    while index < len(tokens):
        if tokens[index] in lengths:
            command, index = tokens[index], index + 1
        require(command in lengths and index + lengths[command] <= len(tokens), "unsupported SVG path")
        values = tuple(float(value) for value in tokens[index:index + lengths[command]])
        index += lengths[command]
        if command == "M":
            position = values
        elif command == "V":
            end = position[0], values[0]
            segments.append((position, end))
            position = end
        elif command == "L":
            segments.append((position, values))
            position = values
        else:
            control, end = values[:2], values[2:]
            segments.append((position, control, end))
            position = end
    require(segments, "empty SVG path")
    return segments


def mark_geometry():
    mark = ET.fromstring((ASSET_ROOT / SOURCES[0]).read_bytes())
    wordmark = ET.fromstring((ASSET_ROOT / SOURCES[1]).read_bytes())
    require(not mark.findall(".//{*}text") and not wordmark.findall(".//{*}text"), "SVG text is forbidden")
    paths = mark.findall("{*}path")
    require(len(paths) == 3, "Mindy mark path count differs")
    for source in SOURCES:
        require(not any(name in (ASSET_ROOT / source).read_text(encoding="utf-8").lower() for name in ("thunderbird", "mozilla", "outlook")), "prohibited product identity")
    return [(svg_path(path.attrib["d"]), float(path.attrib["stroke-width"]),
             tuple(int(path.attrib["stroke"][index:index + 2], 16) for index in (1, 3, 5))) for path in paths]


def paint(canvas, width, height, x, y, radius, color):
    left, right = max(0, int(x - radius)), min(width - 1, int(x + radius + 1))
    top, bottom = max(0, int(y - radius)), min(height - 1, int(y + radius + 1))
    for row in range(top, bottom + 1):
        for column in range(left, right + 1):
            if (column - x) ** 2 + (row - y) ** 2 <= radius ** 2:
                offset = (row * width + column) * 4
                canvas[offset:offset + 4] = bytes((*color, 255))


def stroke(canvas, width, height, points, width_source, color, scale, left, top):
    points = [(left + x * scale, top + y * scale) for x, y in points]
    radius = max(0.5, width_source * scale / 2)
    for start, end in zip(points, points[1:]):
        distance = max(abs(end[0] - start[0]), abs(end[1] - start[1]))
        for step in range(int(distance) + 1):
            fraction = step / max(1, int(distance))
            paint(canvas, width, height, start[0] + (end[0] - start[0]) * fraction,
                  start[1] + (end[1] - start[1]) * fraction, radius, color)


def curve(start, control, end):
    return [((1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control[0] + t ** 2 * end[0],
             (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control[1] + t ** 2 * end[1]) for t in (n / 32 for n in range(33))]


def raster(width, height, geometry):
    canvas = bytearray(width * height * 4)
    scale = min(width, height) * .88 / 512
    left, top = (width - 512 * scale) / 2, (height - 512 * scale) / 2
    for segments, width_source, color in geometry:
        points = [segments[0][0]]
        for segment in segments:
            points.extend([segment[-1]] if len(segment) == 2 else curve(*segment)[1:])
        stroke(canvas, width, height, points, width_source, color, scale, left, top)
    return bytes(canvas)


def chunk(name, data):
    return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xffffffff)


def png(width, height, geometry):
    pixels = raster(width, height, geometry)
    rows = b"".join(b"\0" + pixels[row * width * 4:(row + 1) * width * 4] for row in range(height))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")


def ico(sizes, geometry):
    images = [png(size, size, geometry) for size in sizes]
    offset = 6 + 16 * len(images)
    entries = []
    for size, image in zip(sizes, images):
        entries.append(struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(image), offset))
        offset += len(image)
    return struct.pack("<HHH", 0, 1, len(images)) + b"".join(entries + images)


def bmp(width, height, geometry):
    source, stride = raster(width, height, geometry), (width * 3 + 3) & ~3
    rows = []
    for row in range(height - 1, -1, -1):
        pixels = bytearray()
        for column in range(width):
            red, green, blue, alpha = source[(row * width + column) * 4:(row * width + column + 1) * 4]
            background = (242, 250, 252)
            pixels += bytes((blue * alpha // 255 + background[2] * (255 - alpha) // 255,
                             green * alpha // 255 + background[1] * (255 - alpha) // 255,
                             red * alpha // 255 + background[0] * (255 - alpha) // 255))
        rows.append(bytes(pixels).ljust(stride, b"\0"))
    body = b"".join(rows)
    return b"BM" + struct.pack("<IHHI", 54 + len(body), 0, 0, 54) + struct.pack("<IIIHHIIIIII", 40, width, height, 1, 24, 0, len(body), 0, 0, 0, 0) + body


def symbolic():
    mark = ET.fromstring((ASSET_ROOT / "mindy-mark.svg").read_bytes())
    paths = mark.findall("{*}path")
    require(len(paths) == 3 and not mark.findall(".//{*}text"), "invalid Mindy mark")
    lines = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">']
    for path in paths:
        lines.append(f'  <path d="{path.attrib["d"]}" fill="none" stroke="currentColor" stroke-width="{path.attrib["stroke-width"]}" stroke-linecap="{path.attrib["stroke-linecap"]}" stroke-linejoin="{path.attrib.get("stroke-linejoin", "round")}"/>')
    return ("\n".join(lines + ["</svg>"]) + "\n").encode()


def derivatives():
    geometry = mark_geometry()
    result = {"content/about-logo.svg": (ASSET_ROOT / "mindy-mark.svg").read_bytes(),
              "content/about-wordmark.svg": (ASSET_ROOT / "mindy-wordmark.svg").read_bytes()}
    result.update({path: png(*size, geometry) for path, size in PNG.items()})
    result.update({path: ico(sizes, geometry) for path, sizes in ICO.items()})
    result.update({path: bmp(*size, geometry) for path, size in BMP.items()})
    result[SYMBOLIC] = symbolic()
    return result


def metadata(path, data):
    if path.endswith(".png"):
        width, height = struct.unpack(">II", data[16:24])
    elif path.endswith(".bmp"):
        width, height = struct.unpack("<ii", data[18:26])
    else:
        width = height = None
    return {"sha256": hashlib.sha256(data).hexdigest(), "format": Path(path).suffix[1:].upper(), "width": width, "height": height}


def generate(check=False):
    files = derivatives()
    manifest = {"schema": 1, "generator": "tools/generate_brand_assets.py", "sources": {name: hashlib.sha256((ASSET_ROOT / name).read_bytes()).hexdigest() for name in SOURCES}, "derivatives": {name: metadata(name, data) for name, data in sorted(files.items())}}
    expected = {OUTPUT / name: data for name, data in files.items()}
    expected[OUTPUT / "manifest.json"] = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    mismatches = [path for path, data in expected.items() if not path.is_file() or path.read_bytes() != data]
    stale = [path for path in OUTPUT.rglob("*") if path.is_file() and path not in expected]
    if check:
        require(not mismatches and not stale, "generated assets differ: " + ", ".join(str(path.relative_to(ROOT)) for path in mismatches + stale))
    else:
        for path, data in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        for path in stale:
            path.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        generate(args.check)
    except (OSError, ValueError, ET.ParseError) as error:
        raise SystemExit(f"Mindy brand asset generation failed: {error}")
