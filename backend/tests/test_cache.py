"""KV-cache replay correctness and terminal stage-failure behaviour."""

import asyncio

from backend.pipeline.kv_cache_manager import KVCacheManager, PipelineContext
from backend.pipeline.orchestrator import PipelineOrchestrator


class _Img:
    resolution_label = "1024x1024"


def make_ctx(**kw):
    kw.setdefault("image", _Img())
    kw.setdefault("model_name", "m")
    kw.setdefault("image_hash", "abcdef1234567890")
    return PipelineContext(**kw)


def test_cache_ignores_error_frames():
    cache = KVCacheManager()
    cache.store("mapping", {"type": "error", "stage": "mapping", "message": "boom"})
    assert cache.get("mapping") is None
    assert cache.hits() == 0


def test_cache_stores_full_stage_result_event():
    cache = KVCacheManager()
    ev = {"type": "stage_result", "stage": "mapping", "data": {"total": 1, "entities": []}}
    cache.store("mapping", ev)
    assert cache.get("mapping") == ev


def test_cache_key_includes_domain_and_detail_level():
    k1 = make_ctx(domain="pcb", detail_level="high").stage_prompt_variant("mapping")
    k2 = make_ctx(domain="medical", detail_level="high").stage_prompt_variant("mapping")
    k3 = make_ctx(domain="pcb", detail_level="low").stage_prompt_variant("mapping")
    assert len({k1, k2, k3}) == 3


def test_cache_key_includes_prompt_version():
    from backend.pipeline.kv_cache_manager import PROMPT_VERSION

    key = make_ctx().stage_prompt_variant("mapping")
    assert PROMPT_VERSION in key


def test_restore_rehydrates_mapping():
    ctx = make_ctx()
    ctx.restore("mapping", {"type": "stage_result", "stage": "mapping", "data": {"total": 2, "entities": []}})
    assert '"total": 2' in ctx.map_json


def test_restore_rehydrates_deliberation():
    ctx = make_ctx()
    ctx.restore("deliberation", {"type": "stage_result", "stage": "deliberation", "data": {"thought_chain": "chain"}})
    assert ctx.reasoning_output == "chain"


def test_restore_rehydrates_critic():
    ctx = make_ctx()
    ctx.restore("critic", {"type": "stage_result", "stage": "critic", "data": {"verified": True}})
    assert '"verified": true' in ctx.critique_json


class _FakeAgent:
    def __init__(self, stage_name):
        self.stage_name = stage_name

    async def run(self, ctx, image_b64):
        yield {"type": "error", "stage": self.stage_name, "message": "boom"}


def _pipeline_events(orch, ctx, image_b64):
    async def collect():
        return [e async for e in orch._real_pipeline(ctx, image_b64, 0.0)]

    return asyncio.run(collect())


def test_stage_error_is_terminal_no_metrics():
    orch = PipelineOrchestrator()
    orch._model_name = "test-model"
    orch.agent = lambda cls, **kw: _FakeAgent("mapping")

    events = _pipeline_events(orch, make_ctx(model_name="test-model"), "b64")

    assert [e.get("type") for e in events] == ["error"]
    assert not any(e.get("type") == "metrics" for e in events)
    assert not any(e.get("type") == "stage_result" for e in events)


def test_cache_hit_skips_agent_and_replays_typed_event():
    # Seed the KV cache; the orchestrator must replay the stored event and
    # NOT invoke the stage agent again. If the agent did run, it would emit
    # an error frame (the fake's run() always errors).
    orch = PipelineOrchestrator()
    orch.cache = KVCacheManager()
    orch._model_name = "test-model"
    orch.agent = lambda cls, **kw: _FakeAgent(cls.stage_name)

    ev = {
        "type": "stage_result",
        "stage": "mapping",
        "data": {"total": 3, "entities": []},
    }
    ctx = make_ctx(model_name="test-model")
    orch.cache.store(ctx.stage_prompt_variant("mapping"), ev)

    events = _pipeline_events(orch, ctx, "b64")

    assert events[0] == ev
    # No error from stage "mapping": the agent was not re-run on the hit.
    assert not any(e.get("type") == "error" and e.get("stage") == "mapping" for e in events)
    # The replayed mapping must have been restored onto the context for the
    # pipe to continue to the next stage, which attempted to run.
    assert ctx.map_json


def test_cache_disabled_returns_none():
    cache = KVCacheManager(enabled=False)
    cache.store("k", {"type": "stage_result", "stage": "mapping", "data": {}})
    assert cache.get("k") is None

def test_optional_review_keeps_synthesis_cache_separate():
    standard = make_ctx(extra_review=False)
    reviewed = make_ctx(extra_review=True)
    assert standard.stage_prompt_variant("mapping") == reviewed.stage_prompt_variant("mapping")
    assert standard.stage_prompt_variant("synthesis") != reviewed.stage_prompt_variant("synthesis")


def test_standard_pipeline_skips_critic():
    import json
    orch = PipelineOrchestrator()
    ctx = make_ctx(extra_review=False)
    class SuccessAgent:
        def __init__(self, name): self.stage_name = name
        async def run(self, context, image):
            assert self.stage_name != "critic"
            if self.stage_name == "synthesis":
                assert json.loads(context.critique_json)["review_performed"] is False
            yield {"type":"stage_result", "stage":self.stage_name, "data":{}}
    orch.agent = lambda cls, **kw: SuccessAgent(cls.stage_name)
    events = _pipeline_events(orch, ctx, "b64")
    assert any(e["type"] == "review_skipped" for e in events)
    assert not any(e.get("type") == "stage_result" and e.get("stage") == "critic" for e in events)
