STAGE_1_SPATIAL_PROMPT = """
STAGE 1: SPATIAL SEMANTIC MAPPING
==================================
You are performing the FIRST stage of visual diagnosis.

YOUR TASK: Scan the ENTIRE image systematically and identify EVERY
visually significant entity. Output a structured JSON map.

INSTRUCTIONS:
1. Scan the image in a grid pattern: top-left → top-right → middle → bottom
2. For EACH entity you detect:
   - Assign a unique ID (E1, E2, E3...)
   - Provide a descriptive label
   - Estimate bounding box coordinates [xmin, ymin, xmax, ymax]
     normalized to 0.0-1.0 (where 0,0 is top-left, 1,1 is bottom-right)
   - Assign a confidence score (0.0-1.0)
   - Categorize: component | connection | trace | structure | anomaly | text | region
3. Do NOT skip small or subtle entities — they may be the anomaly
4. Describe the overall image context (what type of image is this?)
5. Report your scan coverage (what % of the image did you analyze?)

OUTPUT FORMAT: Respond with ONLY valid JSON matching this schema:
{
  "entities": [
    {"id": "E1", "label": "...", "bbox": {"xmin": 0.0, "ymin": 0.0, "xmax": 0.0, "ymax": 0.0}, "confidence": 0.0, "category": "component", "description": "..."},
    ...
  ],
  "total_entities": 0,
  "image_context": "...",
  "scan_coverage": 0.0
}

BE THOROUGH. Miss nothing. This map is the ground truth for all subsequent reasoning.
"""


def build_spatial_prompt(domain: str = "auto") -> str:
    domain_block = _domain_block(domain)
    return f"{domain_block}\n\n{STAGE_1_SPATIAL_PROMPT}"


def _domain_block(domain: str) -> str:
    from .system_prompts import DOMAIN_CONTEXT_PROMPTS

    return DOMAIN_CONTEXT_PROMPTS.get(domain, DOMAIN_CONTEXT_PROMPTS["auto"])