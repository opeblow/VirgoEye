#!/usr/bin/env python
"""Generate synthetic diagnostic test images (PCB / X-ray / blueprint)."""

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


def generate(dest_dir: str) -> None:
    os.makedirs(dest_dir, exist_ok=True)
    maps = {
        "pcb_fault.png": make_pcb,
        "xray_sample.png": make_xray,
        "blueprint_sample.png": make_blueprint,
    }
    for fname, fn in maps.items():
        img = fn()
        path = os.path.join(dest_dir, fname)
        img.save(path)
        print(f"wrote {path}")


if __name__ == "__main__":
    dest = sys.argv[1] if len(sys.argv) > 1 else "backend/tests/sample_images"
    generate(os.path.abspath(dest))