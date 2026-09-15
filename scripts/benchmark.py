#!/usr/bin/env python
"""Speed benchmark: latency, tok/s, VRAM against sample images."""

import asyncio
import base64
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.pipeline.image_processor import load_from_base64  # noqa: E402
from backend.pipeline.orchestrator import PipelineOrchestrator  # noqa: E402


def b64file(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    proc = load_from_base64(base64.b64encode(raw).decode())
    return proc.base64


async def main() -> None:
    orc = PipelineOrchestrator()
    await orc.initialize()
    print(f"model={orc.model_name} demo={orc.demo_mode}")

    samples_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "tests", "sample_images")
    if not os.path.isdir(samples_dir):
        print("no sample images; generating...")
        from scripts.generate_test_data import generate  # noqa: PLC0415
        generate(samples_dir)

    results = []
    for name in os.listdir(samples_dir):
        if not name.endswith((".png", ".jpg", ".jpeg")):
            continue
        path = os.path.join(samples_dir, name)
        img = b64file(path)
        t0 = time.perf_counter()
        stage_result = None
        async for ev in orc.analyze(type("R", (), {"image_base64": img, "domain": "pcb", "detail_level": "high"})()):
            if ev.get("type") == "stage_result" and ev.get("stage") == "synthesis":
                stage_result = ev["data"]
        elapsed = (time.perf_counter() - t0) * 1000
        sev = stage_result and stage_result.get("severity") or "?"
        results.append((name, round(elapsed), sev))
        print(f"{name}: {elapsed:,.0f}ms severity={sev}")

    await orc.close()
    print("\n=== SUMMARY ===")
    for n, ms, s in results:
        print(f"  {n:32s} {ms:>8,}ms  {s}")


if __name__ == "__main__":
    asyncio.run(main())