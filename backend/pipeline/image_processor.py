"""Image loading, validation, resizing, and Base64 encoding."""

import base64
import io
import re
from dataclasses import dataclass
from typing import Optional

import numpy as np
from PIL import Image, UnidentifiedImageError

from backend import config


class ImageValidationError(ValueError):
    pass


@dataclass
class ProcessedImage:
    image: Image.Image
    data: bytes
    mime: str
    base64: str
    original_w: int
    original_h: int
    resized_w: int
    resized_h: int
    resolution_label: str

    @property
    def aspect(self) -> float:
        return self.resized_w / self.resized_h if self.resized_h else 1.0


def _clean_b64(raw: str) -> str:
    """Strip data-URI prefix and any whitespace from a base64 string."""
    raw = raw.strip()
    if "," in raw and raw.startswith("data:"):
        raw = raw.split(",", 1)[1]
    raw = re.sub(r"\s+", "", raw)
    return raw


def decode_image_data(encoded: str) -> bytes:
    try:
        enc = _clean_b64(encoded)
        return base64.b64decode(enc, validate=True)
    except Exception as exc:
        raise ImageValidationError(f"Invalid base64 payload: {exc}") from exc


def _detect_mime(data: bytes) -> str:
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data[:2] == b"BM":
        return "image/bmp"
    raise ImageValidationError(
        "Unrecognized image format — expected JPEG, PNG, WebP, or BMP"
    )


# Upper bound on the base64-encoded payload for MAX_IMAGE_BYTES bytes
# (4 chars per 3 bytes, rounded up), plus slack for data-URI prefixes.
def _max_encoded_bytes() -> int:
    return ((config.MAX_IMAGE_BYTES + 2) // 3) * 4


def load_from_base64(encoded: str) -> ProcessedImage:
    cleaned = _clean_b64(encoded)
    if len(cleaned) > _max_encoded_bytes():
        raise ImageValidationError(
            f"Encoded image too large ({len(cleaned)} base64 chars > "
            f"max {config.MAX_IMAGE_BYTES} bytes)"
        )
    data = decode_image_data(cleaned)
    if len(data) > config.MAX_IMAGE_BYTES:
        raise ImageValidationError(
            f"Image too large ({len(data)} bytes > {config.MAX_IMAGE_BYTES})"
        )
    mime = _detect_mime(data)
    if mime not in config.SUPPORTED_MIME:
        raise ImageValidationError(f"Unsupported image type: {mime}")
    if len(data) == 0:
        raise ImageValidationError("Empty image payload")
    try:
        pil = Image.open(io.BytesIO(data))
        pil.load()
    except (UnidentifiedImageError, OSError) as exc:
        # PIL raises UnidentifiedImageError, but truncated/corrupt payloads
        # surface as OSError ("broken data stream") — both mean "not an image".
        raise ImageValidationError("Decoded bytes are not a valid image") from exc

    pil = pil.convert("RGB")
    orig_w, orig_h = pil.size

    longest = max(orig_w, orig_h)
    if longest > config.MAX_IMAGE_SIZE:
        scale = config.MAX_IMAGE_SIZE / longest
        new_w = max(1, round(orig_w * scale))
        new_h = max(1, round(orig_h * scale))
        pil = pil.resize((new_w, new_h), Image.Resampling.LANCZOS)

    out = io.BytesIO()
    pil.save(out, format="JPEG", quality=config.JPEG_QUALITY, optimize=True)
    out_bytes = out.getvalue()

    return ProcessedImage(
        image=pil,
        data=out_bytes,
        mime="image/jpeg",
        base64=base64.b64encode(out_bytes).decode("ascii"),
        original_w=orig_w,
        original_h=orig_h,
        resized_w=pil.width,
        resized_h=pil.height,
        resolution_label=f"{orig_w}x{orig_h} -> {pil.width}x{pil.height}",
    )


def to_numpy(img: Image.Image) -> np.ndarray:
    return np.asarray(img, dtype=np.uint8)


def brightness_stats(img: Image.Image) -> dict:
    arr = to_numpy(img)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "p5": float(np.percentile(arr, 5)),
        "p95": float(np.percentile(arr, 95)),
        "width": img.width,
        "height": img.height,
    }