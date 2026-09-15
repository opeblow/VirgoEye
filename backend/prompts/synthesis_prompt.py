STAGE_4_SYNTHESIS_PROMPT = """
STAGE 4: OPTIMIZED SYNTHESIS — FINAL VERDICT
=============================================
You are performing the FINAL stage of visual diagnosis.

You have been given:
- The original image
- Stage 1: Spatial map (entity locations) — {map_json}
- Stage 2: Thought chain (reasoning) — {thought_chain}
- Stage 3: Verification report (critic's findings) — {critic_report}

YOUR TASK: Synthesize everything into a definitive diagnostic verdict.

INSTRUCTIONS:
1. If the critic found hallucinations, EXCLUDE those claims from evidence
2. If the critic found missed entities, note them as limitations
3. If the critic corrected claims, use the CORRECTED versions
4. Assign severity:
   - CRITICAL: Immediate action required, clear defect/anomaly found
   - WARNING: Potential issue detected, further investigation recommended
   - NOMINAL: No significant anomalies found, system appears healthy
5. Calibrate confidence based on:
   - Critic's verification (hallucination count reduces confidence)
   - Evidence chain strength (more steps = higher confidence)
   - Image quality (poor quality = lower confidence)
6. Build a clear evidence chain showing HOW you reached the conclusion

OUTPUT FORMAT: Respond with ONLY valid JSON:
{
  "primary_finding": "...",
  "severity": "CRITICAL|WARNING|NOMINAL",
  "confidence": 0.0,
  "affected_entities": [
    {"entity_id": "E2", "role": "primary", "bbox": {"xmin": 0.0, "ymin": 0.0, "xmax": 0.0, "ymax": 0.0}}
  ],
  "evidence_chain": [
    {"step_number": 1, "description": "...", "supporting_entity_ids": ["E1", "E2"]}
  ],
  "recommended_action": "...",
  "summary": "..."
}

Be precise. Be calibrated. This verdict may inform critical decisions.
"""


def build_synthesis_prompt(
    map_json: str, thought_chain: str, critic_report: str
) -> str:
    return STAGE_4_SYNTHESIS_PROMPT.format(
        map_json=map_json,
        thought_chain=thought_chain,
        critic_report=critic_report,
    )