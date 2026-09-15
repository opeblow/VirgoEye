import base64
import os

import pytest

from backend.agents.base_agent import extract_json_block, parse_json
from backend.ml_utils.speed_tracker import SpeedTracker


def test_extract_json_block_from_prose():
    text = 'Here is my answer.\n\n{"entities": [], "total": 0}\n\nDone.'
    assert parse_json(text) == {"entities": [], "total": 0}


def test_extract_json_with_braces_in_string():
    text = '{"note": "brace { inside", "ok": 1}'
    assert parse_json(text) == {"note": "brace { inside", "ok": 1}


def test_extract_json_skips_prefix():
    text = 'prefix junk\n[1, 2, 3]'
    assert parse_json(text) == [1, 2, 3]


def test_extract_json_raises_without_json():
    with pytest.raises(ValueError):
        extract_json_block("no json here")


def test_speed_tracker_stage_latencies():
    import time

    t = SpeedTracker()
    t.begin_stage("mapping")
    time.sleep(0.01)
    t.end_stage("mapping")
    t.record_tokens("mapping", 100)
    m = t.metrics(model_name="test", quantization="q4", resolution="512x512")
    assert m["total_latency_ms"] >= 0
    assert "mapping" in m["stage_latencies"]
    assert m["total_tokens_generated"] >= 100
    assert m["model_name"] == "test"


def test_speed_tracker_tokens_per_sec():
    t = SpeedTracker()
    t.begin_stage("deliberation")
    t.record_tokens("deliberation", 50)
    import time

    time.sleep(0.05)
    t.end_stage("deliberation")
    assert t.stage_tokens_per_sec("deliberation") > 0