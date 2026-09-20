STAGE_4_SYNTHESIS_PROMPT = """
STAGE 4: OPTIMIZED SYNTHESIS — FINAL VERDICT
=============================================
You are performing the FINAL stage of visual diagnosis.

You have been given:
- The original image
- Stage 1: Spatial map (entity locations) — {map_json}
- Stage 2: Thought chain (reasoning) — {thought_chain}
- Stage 3: Verification report (critic's findings) — {critic_report}

YOUR TASK: Synthesize everything into a provisional visual inspection finding.

INSTRUCTIONS:
1. If the critic found hallucinations, EXCLUDE those claims from evidence
2. If the critic found missed entities, note them as limitations
3. If the critic corrected claims, use the CORRECTED versions
4. First assess image suitability and observable concern:
   - image_suitability: adequate (relevant and clear), limited (some usable evidence),
     unsuitable (unrelated, illustration, or too blurred to assess).
   - visible_concern: present (clear abnormal tissue/lesions/discoloration),
     absent (no convincing visible abnormality), uncertain (evidence cannot distinguish).
   Missing field context is a limitation, NOT itself an abnormality. Normal leaf
   lobing, tiny ambiguous specks and image noise alone should not trigger an alert.
   Unsuitable images must use uncertain; recommend a clear relevant photo.
   A clear healthy-looking leaf can have absent concerns without proving whole-plant health.
   Assign severity:
   - CRITICAL: Immediate action required, clear defect/anomaly found
   - WARNING: Potential issue detected, further investigation recommended
   - NOMINAL: No convincing concern visible in this image; not proof of plant health
5. Give an uncalibrated model confidence estimate based on:
   - Critic's verification (hallucination count reduces confidence)
   - Quality of observable evidence (more steps do not imply greater confidence)
   - Image quality (poor quality = lower confidence)
6. Build a clear evidence chain showing HOW you reached the conclusion
7. Fill every output field with substantive text, never placeholder, TODO, or ellipses.
   Even an inconclusive inspection needs a useful recommended_action and summary.
   When image detail is inadequate, ask for a clear, in-focus crop photograph.

OUTPUT FORMAT: Respond with ONLY valid JSON:
{{
  "primary_finding": "Concise finding, at most 250 characters",
  "image_suitability": "adequate|limited|unsuitable",
  "visible_concern": "present|absent|uncertain",
  "severity": "CRITICAL|WARNING|NOMINAL",
  "confidence": 0.0,
  "affected_entities": [
    {{"entity_id": "E2", "role": "primary", "bbox": {{"xmin": 0.0, "ymin": 0.0, "xmax": 0.0, "ymax": 0.0}}}}
  ],
  "evidence_chain": [
    {{"step_number": 1, "description": "...", "supporting_entity_ids": ["E1", "E2"]}}
  ],
  "recommended_action": "...",
  "summary": "Short headline, maximum 400 characters"
}}

Be concise. Include uncertainty and a practical field check. A photograph cannot establish a diagnosis or justify chemical treatment. If this is an illustration, irrelevant input or inadequate evidence, say the inspection is inconclusive and recommend obtaining a real, relevant field photograph.
"""


def build_synthesis_prompt(
    map_json: str, thought_chain: str, critic_report: str
) -> str:
    return STAGE_4_SYNTHESIS_PROMPT.format(
        map_json=map_json,
        thought_chain=thought_chain,
        critic_report=critic_report,
    )
