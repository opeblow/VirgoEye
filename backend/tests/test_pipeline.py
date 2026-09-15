import base64
import io

import numpy as np
import pytest
from PIL import Image

from backend.pipeline.image_processor import (
    ImageValidationError,
    load_from_base64,
)


def make_png_bytes(size=(300, 400)) -> bytes:
    h, w = size
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :, 1] = np.linspace(0, 120, w, dtype=np.uint8)[None, :]
    arr[h // 2 - 20 : h // 2 + 20, w // 3 : w // 2, :] = (220, 40, 20)  # red anomaly blob
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def encode(png: bytes) -> str:
    return base64.b64encode(png).decode("ascii")


@pytest.fixture
def sample_b64() -> str:
    return encode(make_png_bytes())


def test_load_from_base64(sample_b64):
    proc = load_from_base64(sample_b64)
    # numpy creates (h, w, c), PIL interprets width as x-size
    assert proc.image.width == 400
    assert proc.image.height == 300
    assert proc.mime == "image/jpeg"  # always re-encoded to JPEG by the loader
    assert proc.base64


def test_load_from_base64_rejects_garbage():
    with pytest.raises(Exception):
        load_from_base64("!!!not-base64!!!")


def test_data_uri_supported(sample_b64):
    with_uri = f"data:image/png;base64,{sample_b64}"
    proc = load_from_base64(with_uri)
    assert proc.image.size == (400, 300)  # (width, height)


def test_resize_long_side():
    b64 = encode(make_png_bytes((2000, 900)))
    proc = load_from_base64(b64)
    assert max(proc.image.width, proc.image.height) <= 1280


def test_unknown_format_is_rejected_not_defaulted_to_jpeg():
    junk = b"\x00\x01\x02\x03" * 16
    with pytest.raises(ImageValidationError):
        load_from_base64(base64.b64encode(junk).decode("ascii"))


def test_nonexistent_format_is_rejected():
    with pytest.raises(ImageValidationError):
        # A valid base64 encoding of random bytes that is NOT an image.
        load_from_base64(encode(make_png_bytes()[:64] + b"\x00" * 64))


def test_oversized_payload_rejected_before_decode():
    from backend import config

    # base64 of more than MAX_IMAGE_BYTES — checked on the encoded string
    # length before any base64 decoding happens.
    huge = "A" * (((config.MAX_IMAGE_BYTES + 2) // 3) * 4 + 64)
    with pytest.raises(ImageValidationError):
        load_from_base64(huge)