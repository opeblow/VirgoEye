STAGE_3_CRITIC_PROMPT = """
STAGE 3: COUNTER-FACTUAL VERIFICATION
======================================
You are the CRITIC. Your job is to find flaws in the Stage 2 reasoning.

You have been given:
- The original image
- The Stage 1 spatial map (ground truth coordinates) — {map_json}
- The Stage 2 thought chain (reasoning to verify) — {thought_chain}

YOUR TASK: Systematically verify every claim in the thought chain.

CHECK FOR:
1. SPATIAL HALLUCINATIONS: Did the reasoner reference coordinates that
   don't match the Stage 1 map? Did it claim an entity exists at a
   location where the map shows nothing?

2. LOGICAL FALLACIES: Did the reasoning make invalid logical jumps?
   Example: "E2 has irregular shape, therefore the entire board is faulty"
   (hasty generalization)

3. MISSED ENTITIES: Are there entities in the Stage 1 map that were
   NEVER analyzed in the thought chain? List them.

4. FALSE POSITIVES: Did the reasoner flag something as anomalous that
   is actually normal? Cross-reference with the image.

5. FALSE NEGATIVES: Based on your own observation of the image, did
   the reasoner MISS an actual anomaly?

6. CONFIDENCE CALIBRATION: Is the reasoner's implied confidence level
   appropriate given the evidence? Over-confident? Under-confident?

OUTPUT FORMAT: Respond with ONLY valid JSON:
{{
  "verified": true,
  "hallucination_count": 0,
  "hallucinations": [
    {{"chunk_id": 0, "claim": "...", "issue": "...", "severity": "minor|major|critical"}}
  ],
  "missed_entities": ["E4", "E11"],
  "corrections": [
    {{"original_claim": "...", "issue": "...", "corrected_claim": "..."}}
  ],
  "critic_confidence": 0.0,
  "critic_notes": "..."
}}

Be ruthless. Your job is to catch errors. The final verdict depends on you.
"""


def build_critic_prompt(map_json: str, thought_chain: str) -> str:
    return STAGE_3_CRITIC_PROMPT.format(
        map_json=map_json, thought_chain=thought_chain
    )