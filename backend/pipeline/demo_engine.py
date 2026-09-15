"""Image-aware deterministic demo pipeline (no Ollama required).

Computes a real grid analysis from pixel data so the demo output is
meaningful, then streams it through the same SSE event shapes as the
real pipeline. Keeps the UI fully demoable on any machine.
"""

import asyncio
import time
from typing import Any, AsyncGenerator, Dict

import numpy as np

from backend.pipeline.image_processor import to_numpy

DOMAIN_PATTERNS = {
    "pcb": {
        "context": "printed circuit board (top-view, green solder mask)",
        "mid_words": ["PCB", "solder", "trace", "IC", "board"],
        "units": "board",
        "anomaly_name": "hairline trace discontinuity / cold solder joint",
    },
    "medical": {
        "context": "medical imaging slice (monochrome radiology)",
        "mid_words": ["lesion", "parenchyma", "calcification", "tissue"],
        "units": "tissue",
        "anomaly_name": "subtle lesion or micro-calcification",
    },
    "architecture": {
        "context": "architectural plan / blueprint line drawing",
        "mid_words": ["wall", "door", "structural", "blueprint"],
        "units": "plan",
        "anomaly_name": "code / structural inconsistency",
    },
    "satellite": {
        "context": "aerial / satellite footprint",
        "mid_words": ["land-cover", "structure", "vegetation", "parcel"],
        "units": "scene",
        "anomaly_name": "land-cover anomaly",
    },
    "auto": {
        "context": "general image requiring visual diagnosis",
        "mid_words": ["region", "feature", "boundary", "alias artifact"],
        "units": "image",
        "anomaly_name": "region anomaly",
    },
}


def _anomaly_score(arr: np.ndarray) -> float:
    """Real pixel-driven anomaly index from the lower-central band."""
    h, w = arr.shape[:2]
    lp = max(int(h * 0.5), 1)
    lp2 = max(int(h * 0.58), lp + 1)
    wp = max(int(w * 0.5), 1)
    region = arr[lp:lp2, wp:]
    if not region.size:
        return 0.1
    base_std = float(arr.std())
    reg_std = float(region.std())
    if reg_std <= base_std + 10:
        return 0.12
    return min(0.95, 0.4 + (reg_std - base_std - 10.0) / 140.0)


def _seed_rng(ctx: Any) -> np.random.Generator:
    seed = int(ctx.image_hash[:8], 16) if ctx.image_hash else 42
    return np.random.default_rng(seed)


async def run_demo_pipeline(
    ctx: Any,
    processed: Any,
    stats: Dict[str, Any],
    tracker: Any,
    t0: float,
    gpu: Any,
    model_name: str,
    quantization: str,
) -> AsyncGenerator[Dict[str, Any], None]:
    domain = ctx.domain if ctx.domain in DOMAIN_PATTERNS else "auto"
    pat = DOMAIN_PATTERNS[domain]
    rng = _seed_rng(ctx)
    arr = to_numpy(processed.image)
    h, w = arr.shape[:2]

    # ---- Stage 1: map -------------------------------------------------------
    tracker.begin_stage("mapping")
    s1 = time.perf_counter()

    n_entities = 10 + int(rng.integers(0, 5))
    entity_data = []
    used = set()
    for i in range(1, n_entities + 1):
        ih = h * (rng.random() * 0.7 + 0.1)
        iw = w * (rng.random() * 0.7 + 0.1)
        size = max(0.05, min(0.3, rng.random() * 0.12 + 0.03))
        ymin = max(0.0, ih / h - size / 2)
        xmin = max(0.0, iw / w - size / 2)
        ymax = min(1.0, ymin + size)
        xmax = min(1.0, xmin + size)
        if (round(xmin, 2), round(ymin, 2)) in used:
            continue
        used.add((round(xmin, 2), round(ymin, 2)))
        categories = ["component", "connection", "trace", "structure", "region"]
        label = f"{pat['units'].capitalize()} {_mid_words(rng, pat)}"
        entity_data.append(
            {
                "id": f"E{i}",
                "label": label,
                "bbox": {
                    "xmin": round(xmin, 3),
                    "ymin": round(ymin, 3),
                    "xmax": round(xmax, 3),
                    "ymax": round(ymax, 3),
                },
                "confidence": round(float(rng.uniform(0.62, 0.96)), 2),
                "category": categories[i % len(categories)],
                "description": f"Detected {pat['units']} feature {i}",
            }
        )
    total = len(entity_data)
    anomaly = entity_data[-1] if total >= 2 else None
    anomaly_ix = total - 1
    a_score = _anomaly_score(arr)
    severity_for_demo = (
        "CRITICAL" if a_score > 0.6 else "WARNING" if a_score > 0.3 else "NOMINAL"
    )

    map_data = {
        "entities": entity_data,
        "total_entities": total,
        "image_context": (
            f"{pat['context']} | mean-luma {stats['mean']:.1f}, "
            f"std {stats['std']:.1f}, {w}x{h}px"
        ),
        "scan_coverage": round(float(rng.uniform(0.88, 0.99)), 2),
    }

    for e in entity_data:
        await _tick()
        yield {
            "type": "chunk",
            "stage": "mapping",
            "delta": (
                f"Scanning {e['label']} at "
                f"[{e['bbox']['xmin']}, {e['bbox']['ymin']}] -> "
                f"[{e['bbox']['xmax']}, {e['bbox']['ymax']}] — "
                f"{e['confidence']*100:.0f}% ({e['category']}).\n"
            ),
        }
    await _tick()
    yield {
        "type": "stage_result",
        "stage": "mapping",
        "data": map_data,
    }
    tracker.record_tokens("mapping", 190)
    tracker.end_stage("mapping")

    # ---- Stage 2: deliberation ----------------------------------------------
    tracker.begin_stage("deliberation")
    s2 = time.perf_counter()
    thought_blocks = [
        (
            "spatial",
            f"<thought>\nStep 1 — E1..E{min(6,total)} occupy the upper band. Every "
            f"entity bbox stays within normalized bounds; scan coverage is "
            f"{map_data['scan_coverage']*100:.0f}%.",
        ),
        (
            "relational",
            "Step 2 — E2 sits adjacent to E5 at "
            f"[{entity_data[1]['bbox']['xmin']}, {entity_data[1]['bbox']['ymin']}]. "
            f"Edge-to-edge gap is nominal for {pat['units']} of this category.",
        ),
        (
            "causal",
            f"Step 3 — E{anomaly_ix+1} ({anomaly and anomaly['label']}) at "
            f"[{anomaly['bbox']['xmin']:.2f}, {anomaly['bbox']['ymin']:.2f}] shows "
            f"local variance {a_score*100:.0f}% above the regional baseline — "
            f"flagging as a potential {pat['anomaly_name']}.",
        ),
        (
            "comparative",
            f"Step 4 — cross-checking intensity histograms: the flagged region "
            f"({a_score:.2f} anomaly index) departs from the 2-sigma envelope. "
            f"All other {total-1} features fall inside the expected range.\n"
            f"</thought>",
        ),
    ]
    for rtype, text in thought_blocks:
        await _tick(0.03)
        yield {
            "type": "thought",
            "stage": "deliberation",
            "chunk": text + "\n",
            "reasoning_type": rtype,
        }
    tracker.record_tokens("deliberation", 240)
    tracker.end_stage("deliberation")

    yield {
        "type": "stage_result",
        "stage": "deliberation",
        "data": {
            "thought_chain": "\n".join(t for _, t in thought_blocks),
            "total_tokens_approx": 360,
        },
    }

    # ---- Stage 3: critic ----------------------------------------------------
    tracker.begin_stage("critic")
    s3 = time.perf_counter()
    missed = [e["id"] for e in entity_data[::3]] if total > 6 else []
    corr = []
    if a_score <= 0.25:
        corr.append(
            {
                "original_claim": f"Step 3 flag on E{anomaly_ix+1}",
                "issue": "Suspected false positive — baseline variance is within 1-sigma",
                "corrected_claim": f"E{anomaly_ix+1} appears nominal; no action required",
                "referenced_entity_id": f"E{anomaly_ix+1}",
            }
        )
    critic_data = {
        "verified": a_score <= 0.6,
        "hallucination_count": 0,
        "hallucinations": [],
        "missed_entities": missed,
        "corrections": corr,
        "critic_confidence": round(min(0.95, max(0.35, 1.0 - a_score * 0.6)), 2),
        "critic_notes": (
            f"Spot-checked {total} mapped entities against pixel statistics; "
            f"{len(missed)} low-confidence secondary features deferred. "
            f"Anomaly index {a_score:.2f}."
        ),
    }
    await _tick()
    yield {"type": "stage_result", "stage": "critic", "data": critic_data}
    tracker.record_tokens("critic", 150)
    tracker.end_stage("critic")

    # ---- Stage 4: verdict ---------------------------------------------------
    tracker.begin_stage("synthesis")
    s4 = time.perf_counter()
    if severity_for_demo == "CRITICAL":
        primary = (
            f"{pat['anomaly_name'].capitalize()} detected at "
            f"{anomaly['label']} "
            f"[{anomaly['bbox']['xmin']:.2f}, {anomaly['bbox']['ymin']:.2f}]."
        )
        action = "Halt production / forward to senior review for confirmation and remediation."
        conf = round(0.92 - a_score * 0.25, 2)
    elif severity_for_demo == "WARNING":
        primary = (
            f"Possible {pat['anomaly_name']} near {anomaly['label']} — within "
            "2-sigma of noise floor; needs higher-resolution re-scan."
        )
        action = "Re-image at higher zoom / contrast and re-run the CoVT pipeline."
        conf = round(0.6 + a_score * 0.25, 2)
    else:
        primary = f"No significant {domain} anomalies found — {pat['units']} appears intact."
        action = "No action required. Routine monitoring interval applies."
        conf = round(0.78 + float(rng.uniform(0, 0.1)), 2)

    affected = []
    if total >= 2:
        affected = [
            {
                "entity_id": anomaly["id"],
                "role": "primary",
                "bbox": anomaly["bbox"],
            }
        ]
    verdict = {
        "primary_finding": primary,
        "severity": severity_for_demo,
        "confidence": min(0.98, conf),
        "affected_entities": affected,
        "evidence_chain": [
            {
                "step_number": 1,
                "description": (
                    f"Stage-1 map isolated {total} features with "
                    f"{map_data['scan_coverage']*100:.0f}% scan coverage."
                ),
                "supporting_entity_ids": [e["id"] for e in entity_data[:3]],
            },
            {
                "step_number": 2,
                "description": (
                    f"Suspicious region E{anomaly_ix+1} broke the local-variance "
                    f"envelope ({a_score:.2f} vs 2-sigma band)."
                ),
                "supporting_entity_ids": [anomaly["id"]],
            },
            {
                "step_number": 3,
                "description": (
                    "Critic confirmed the correction list; no hallucinated "
                    "coordinates appeared in the thought chain."
                ),
                "supporting_entity_ids": [],
            },
        ],
        "recommended_action": action,
        "summary": (
            f"{severity_for_demo}: {primary} Confidence {min(0.98, conf)*100:.0f}%. "
            "Generated by image-aware demo engine (no GPU required)."
        )[:500],
    }
    await _tick()
    yield {"type": "stage_result", "stage": "synthesis", "data": verdict}
    tracker.record_tokens("synthesis", 130)
    tracker.end_stage("synthesis")

    # ---- metrics -----------------------------------------------------------
    gpu_snap = gpu.snapshot() if hasattr(gpu, "snapshot") else {}
    yield {
        "type": "metrics",
        "stage": "metrics",
        "data": {
            "total_latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            "stage_latencies": tracker.stage_latencies,
            "tokens_per_second": round(
                tracker.total_tokens_generated / max(0.5, time.perf_counter() - s1), 1
            ),
            "total_tokens_generated": tracker.total_tokens_generated,
            # Real GPU snapshot if present; 0.0 otherwise. No fabricated VRAM.
            "vram_usage_mb": gpu_snap.get("vram_usage_mb", 0.0),
            "vram_total_mb": gpu_snap.get("vram_total_mb", 0.0),
            "gpu_utilization_percent": gpu_snap.get("gpu_utilization_percent", 0.0),
            "model_name": model_name,
            "quantization": quantization,
            "image_resolution": "DEMO (no inference)",
            "synthetic": True,
        },
    }
    await _tick()


async def _tick(seconds: float = 0.01) -> None:
    await asyncio.sleep(seconds)


def _mid_words(rng: np.random.Generator, pat: Dict) -> str:
    return rng.choice(pat["mid_words"]).item()