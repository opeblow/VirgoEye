"""Prompt builders must render without Python format errors and keep their
literal JSON schema blocks intact (braces were previously unescaped and
crashed at runtime with KeyError/IndexError during .format())."""

from backend.prompts.critic_prompt import build_critic_prompt
from backend.prompts.deliberation_prompt import build_deliberation_prompt
from backend.prompts.spatial_prompt import build_spatial_prompt
from backend.prompts.synthesis_prompt import build_synthesis_prompt


def test_critic_prompt_renders():
    p = build_critic_prompt('{"entities": []}', "thought chain")
    assert '{"entities": []}' in p
    assert "thought chain" in p
    # no un-formatted double-open braces survive (double-close is legit JSON)
    assert "{{" not in p


def test_critic_prompt_keeps_literal_json_example():
    # The OUTPUT FORMAT block must survive .format() with literal braces.
    p = build_critic_prompt("{}", "{}")
    assert '\n{\n  "verified"' in p
    assert '"hallucinations"' in p


def test_synthesis_prompt_renders():
    p = build_synthesis_prompt("map", "thought", "critic report")
    assert "map" in p and "thought" in p and "critic report" in p
    assert "{{" not in p


def test_synthesis_prompt_keeps_literal_json_example():
    p = build_synthesis_prompt("{}", "{}", "{}")
    assert '\n{\n  "primary_finding"' in p
    assert '"affected_entities"' in p


def test_deliberation_prompt_renders():
    p = build_deliberation_prompt('{"entities": ["E1"]}')
    assert '{"entities": ["E1"]}' in p
    assert "<thought>" in p


def test_spatial_prompt_renders_with_domain():
    p = build_spatial_prompt("pcb")
    assert "OUTPUT FORMAT" in p
    # no placeholders left behind
    assert "{domain}" not in p