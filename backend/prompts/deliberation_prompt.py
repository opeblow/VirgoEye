"""Produce a concise, public-facing evidence summary."""
def build_deliberation_prompt(map_json: str, domain: str = "auto") -> str:
    return f"""Review this image and the preliminary region map for {domain}: {map_json}
Provide a concise evidence summary, NOT a private chain of thought.
Use three short sections: Visible observations (cite mapped entity IDs),
Uncertainty and alternative explanations, and Suggested field checks.
Separate observed appearance from possible causes. Do not identify a disease,
recommend chemical treatment, or imply a healthy crop solely from one image.
Mention if this is an illustration or inadequate for field inspection.
Stay under 250 words. Do not invent coordinates or additional entity IDs."""
