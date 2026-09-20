STAGE_1_SPATIAL_PROMPT = """
STAGE 1: SPATIAL SEMANTIC MAPPING
==================================
You are performing the FIRST stage of visual diagnosis.

YOUR TASK: Identify up to 6 meaningful visible regions relevant to the inspection. Output a structured JSON map.

INSTRUCTIONS:
1. Scan the image in a grid pattern: top-left → top-right → middle → bottom
2. For EACH entity you detect:
   - Assign a unique ID (E1, E2, E3...)
   - Provide a descriptive label
   - Estimate bounding box coordinates [xmin, ymin, xmax, ymax]
     normalized to 0.0-1.0 (where 0,0 is top-left, 1,1 is bottom-right)
   - Assign a confidence score (0.0-1.0)
   - Categorize: component | connection | trace | structure | anomaly | text | region
3. Do not invent anomalies from tiny specks, natural leaf lobing, glare or background noise.
   A normal leaf does not need an anomaly entity. Use fewer regions when appropriate.
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

This map is a fallible model estimate, NOT ground truth. Boxes are approximate.
If the image is too blurred or unrelated to the selected domain, state that plainly.
"""


def build_spatial_prompt(domain: str = "auto") -> str:
    domain_block = _domain_block(domain)
    return f"{domain_block}\n\n{STAGE_1_SPATIAL_PROMPT}"


def _domain_block(domain: str) -> str:
    from .system_prompts import DOMAIN_CONTEXT_PROMPTS

    return DOMAIN_CONTEXT_PROMPTS.get(domain, DOMAIN_CONTEXT_PROMPTS["auto"])