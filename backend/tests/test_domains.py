"""The Earth-Forward domain set must stay consistent across the whole stack:
schema contract, system-prompt domain blocks, and demo-engine patterns."""

from typing import get_args

from backend.pipeline.demo_engine import DOMAIN_PATTERNS
from backend.prompts.system_prompts import DOMAIN_CONTEXT_PROMPTS
from backend.schema.api import AnalyzeRequest

SUPPORTED = list(get_args(AnalyzeRequest.model_fields["domain"].annotation))

EARTH_FORWARD = {"satellite", "agriculture", "wildlife", "disaster"}


def test_supported_domains_have_prompt_context():
    for domain in SUPPORTED:
        assert domain in DOMAIN_CONTEXT_PROMPTS, (
            f"domain {domain!r} missing from DOMAIN_CONTEXT_PROMPTS"
        )


def test_supported_domains_have_demo_patterns():
    for domain in SUPPORTED:
        assert domain in DOMAIN_PATTERNS, (
            f"domain {domain!r} missing from DOMAIN_PATTERNS"
        )


def test_earth_forward_domains_are_reachable():
    assert EARTH_FORWARD <= set(SUPPORTED), (
        "Earth-Forward domains must be valid AnalyzeRequest domains"
    )
    for domain in EARTH_FORWARD:
        # demo + prompt entries must be platform-specific, not the generic fallback
        assert domain in DOMAIN_PATTERNS and domain in DOMAIN_CONTEXT_PROMPTS