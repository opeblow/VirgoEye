STAGE_2_DELIBERATION_PROMPT = """
STAGE 2: CHAIN-OF-VISUAL-THOUGHT (CoVT) DELIBERATION
=====================================================
You are performing the SECOND stage of visual diagnosis.

You have been given:
- The original image
- A spatial map of all detected entities (from Stage 1) — {map_json}

YOUR TASK: Perform deep, step-by-step visual reasoning. Analyze the
RELATIONSHIPS between entities. Search for anomalies, discontinuities,
or logical errors.

INSTRUCTIONS:
1. SPATIAL STEP: For each entity, confirm its position and properties
   by cross-referencing with the image. Use EXACT coordinates from the map.

2. RELATIONAL STEP: For each pair of spatially adjacent or logically
   related entities, describe their relationship:
   - "E1 (IC Chip U3) connects to E5 (Trace T12) via E2 (Solder Joint J7)"
   - "E8 (Wall Section) meets E9 (Load-Bearing Column) at [0.45, 0.32]"
   - "E3 (Lesion) is adjacent to E7 (Blood Vessel) at distance ~0.03 units"

3. ANOMALY DETECTION STEP: For each relationship, ask:
   - Is this connection intact or broken?
   - Is this alignment correct or misaligned?
   - Is this size/shape/color within normal parameters?
   - Is there something MISSING that should be here?

4. THOUGHT STEP: Wrap your reasoning in <thought> tags. Think step-by-step.
   Every step must reference specific entity IDs and coordinates.

   <thought>
   Step 1: Examining E1 (IC Chip U3) at [0.12, 0.34, 0.28, 0.51]...
   The chip appears properly seated. Pin count matches expected package.

   Step 2: Tracing connection from E1 to E2 (Solder Joint J7) at [0.31, 0.45]...
   The solder joint shows irregular morphology — expected dome shape but
   observing a flattened profile with a possible micro-crack at [0.315, 0.462].

   Step 3: Following E5 (Trace T12) from E2 toward E9...
   The trace shows a 2px discontinuity at approximately [0.38, 0.46].
   This could indicate a hairline fracture or manufacturing defect.
   ...
   </thought>

5. Do NOT skip any entities. If an entity seems normal, say so explicitly
   with evidence: "E4 appears nominal — correct alignment, expected color,
   proper connection to E6."

BE EXHAUSTIVE. This is SLOW THINKING. Take your time. Miss nothing.

OUTPUT FORMAT: Respond ONLY with your thought chain. No preamble, no
summative verdict — that comes later. Just the <thought> reasoning blocks.
"""


def build_deliberation_prompt(map_json: str, domain: str = "auto") -> str:
    return STAGE_2_DELIBERATION_PROMPT.format(map_json=map_json)