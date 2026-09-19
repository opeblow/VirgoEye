#!/usr/bin/env python
"""Generate synthetic diagnostic test images.

Earth-Forward set (NextStep Hacks 2026 theme): satellite land-cover,
agriculture crop stress, wildlife survey, and post-disaster assessment —
plus the original PCB / X-ray / blueprint samples.
"""

import os
import sys

import numpy as np
from PIL import Image, ImageDraw


def make_pcb(seed: int = 1) -> Image.Image:
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (512, 512), (18, 50, 30))  # green board
    d = ImageDraw.Draw(img)
    for _ in range(6):
        x, y = int(rng.integers(50, 400)), int(rng.integers(50, 400))
        d.rectangle([x, y, x + 60, y + 30], outline=(120, 160, 120), width=2)
        d.rectangle([x + 4, y + 4, x + 56, y + 26], fill=(35, 70, 45), outline=(160, 200, 160))
    # traces
    for _ in range(14):
        x1 = int(rng.integers(20, 470))
        y1 = int(rng.integers(20, 470))
        d.line([x1, y1, x1 + int(rng.integers(30, 120)), y1], fill=(200, 210, 190), width=2)
    # a hairline break in one trace
    x = int(rng.integers(40, 300))
    y = int(rng.integers(40, 300))
    d.line([x, y, x + 60, y], fill=(200, 210, 190), width=2)
    d.line([x + 28, y, x + 34, y], fill=(18, 50, 30), width=2)  # invisible gap = fault
    # solder joints
    for _ in range(10):
        jx = int(rng.integers(20, 470))
        jy = int(rng.integers(20, 470))
        d.ellipse([jx, jy, jx + 8, jy + 8], outline=(170, 200, 170), width=1)
    return img


def make_xray(seed: int = 2) -> Image.Image:
    rng = np.random.default_rng(seed)
    noise = rng.normal(128, 38, (512, 512))
    noise = np.clip(noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(noise, "L").convert("RGB")
    d = ImageDraw.Draw(img)
    # bone-like structures
    for i in range(6):
        w = 14 - i
        d.line([180, 40 + i * 60, 420, 60 + i * 60], fill=(190, 190, 195), width=w)
    # subtle micro-calcification cluster
    for i in range(5):
        x = 250 + i * 8
        d.ellipse([x, 300, x + 3, 303], fill=(235, 235, 240))
    return img


def make_blueprint(seed: int = 3) -> Image.Image:
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (512, 512), (10, 25, 55))
    d = ImageDraw.Draw(img)
    # outer walls
    d.rectangle([40, 40, 470, 470], outline=(160, 200, 255), width=3)
    # inner rooms
    d.line([40, 250, 250, 250], fill=(160, 200, 255), width=2)
    d.line([250, 250, 250, 470], fill=(160, 200, 255), width=2)
    d.line([250, 40, 470, 40], fill=(160, 200, 255), width=2)
    # door gaps
    d.line([250, 40, 250, 470], fill=(160, 200, 255), width=2)
    # column
    d.rectangle([110, 110, 130, 130], outline=(230, 240, 255), width=2)
    # a dimension label (text-like lines)
    d.line([40, 470, 40, 495], fill=(120, 160, 255), width=1)
    d.line([40, 495, 470, 495], fill=(120, 160, 255), width=1)
    d.line([470, 470, 470, 495], fill=(120, 160, 255), width=1)
    return img


def make_satellite(seed: int = 4) -> Image.Image:
    rng = np.random.default_rng(seed)
    # variegated terrain base
    noise = rng.normal(96, 22, (512, 512))
    noise = np.clip(noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(noise, "L").convert("RGB")
    d = ImageDraw.Draw(img)
    # forest / canopy blobs
    for _ in range(120):
        cx, cy = int(rng.integers(0, 500)), int(rng.integers(0, 500))
        r = int(rng.integers(6, 24))
        d.ellipse([cx, cy, cx + r, cy + r], fill=(34, 70, 42), outline=(28, 58, 36))
    # a river winding through
    pts = [(30 + i * 6, 120 + int(np.sin(i / 4) * 60)) for i in range(78)]
    d.line(pts, fill=(70, 110, 150), width=6)
    # anomalous geometric clearing = deforestation patch
    d.rectangle([340, 120, 452, 232], fill=(150, 140, 116), outline=(190, 182, 154), width=2)
    d.line([360, 150, 430, 200], fill=(205, 196, 168), width=2)
    # unauthorized structure line inside restricted zone
    d.rectangle([112, 388, 150, 404], fill=(214, 210, 200))
    d.rectangle([182, 388, 220, 404], fill=(214, 210, 200))
    return img


def make_crop(seed: int = 5) -> Image.Image:
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (512, 512), (86, 122, 48))
    d = ImageDraw.Draw(img)
    # crop rows
    for i in range(32):
        y = i * 16
        dark = (62, 96, 34) if i % 2 else (104, 140, 56)
        d.rectangle([0, y, 512, y + 7], fill=dark)
    # water-stressed / chlorotic patch crossing rows
    d.ellipse([150, 96, 336, 260], fill=(176, 164, 74), outline=(146, 136, 60))
    for _ in range(6):
        py = int(rng.integers(96, 250))
        pcol = (140, 128, 62)
        px = int(rng.integers(160, 320))
        d.ellipse([px, py, px + 6, py + 6], fill=pcol)
    # irrigation gap: dry strip
    d.rectangle([420, 0, 436, 512], fill=(150, 132, 92))
    return img


def make_wildlife(seed: int = 6) -> Image.Image:
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (512, 512), (58, 84, 46))
    d = ImageDraw.Draw(img)
    # canopy mosaic
    for _ in range(160):
        cx, cy = int(rng.integers(0, 500)), int(rng.integers(0, 500))
        r = int(rng.integers(4, 18))
        d.ellipse([cx, cy, cx + r, cy + r], fill=(44, 66, 36))
    # dirt road = habitat fragmentation corridor
    pts = [(0, int(rng.integers(180, 260))), (220, 380), (512, 260)]
    d.line(pts, fill=(180, 160, 130), width=10)
    d.line(pts, fill=(150, 132, 106), width=6)
    # fresh disturbance scar (cleared plot)
    d.rectangle([120, 60, 236, 148], fill=(120, 108, 82), outline=(160, 146, 116), width=2)
    # fauna specks along the corridor
    for _ in range(7):
        px, py = int(rng.integers(40, 470)), int(rng.integers(200, 420))
        d.ellipse([px, py, px + 4, py + 4], fill=(22, 26, 22))
    return img


def make_disaster(seed: int = 7) -> Image.Image:
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (512, 512), (108, 96, 88))
    d = ImageDraw.Draw(img)
    # building blocks
    for _ in range(14):
        bx, by = int(rng.integers(20, 380)), int(rng.integers(20, 300))
        d.rectangle([bx, by, bx + int(rng.integers(40, 90)), by + int(rng.integers(34, 60))],
                    fill=(122, 108, 100), outline=(150, 134, 124), width=2)
    # floodwater across the lower band connecting to a river on the left
    d.rectangle([0, 300, 512, 512], fill=(58, 92, 128))
    d.polygon([(256, 252), (268, 330), (244, 330)], fill=(58, 92, 128))
    # partially submerged roofs
    d.rectangle([70, 300, 126, 344], fill=(168, 152, 140))
    d.rectangle([340, 296, 402, 346], fill=(176, 160, 148))
    # debris specks
    for _ in range(18):
        dx = int(rng.integers(20, 470))
        dy = int(rng.integers(120, 400))
        d.rectangle([dx, dy, dx + 5, dy + 5], fill=(70, 62, 56))
    # downed line
    d.line([40, 84, 160, 132], fill=(30, 30, 30), width=3)
    return img


def generate(dest_dir: str) -> None:
    os.makedirs(dest_dir, exist_ok=True)
    maps = {
        "pcb_fault.png": make_pcb,
        "xray_sample.png": make_xray,
        "blueprint_sample.png": make_blueprint,
        "satellite_landcover.png": make_satellite,
        "crop_stress.png": make_crop,
        "wildlife_disturbance.png": make_wildlife,
        "disaster_flood.png": make_disaster,
    }
    for fname, fn in maps.items():
        img = fn()
        path = os.path.join(dest_dir, fname)
        img.save(path)
        print(f"wrote {path}")


if __name__ == "__main__":
    dest = sys.argv[1] if len(sys.argv) > 1 else "backend/tests/sample_images"
    generate(os.path.abspath(dest))