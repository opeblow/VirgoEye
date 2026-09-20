import asyncio
from types import SimpleNamespace
import pytest
from backend.ml_utils.anthropic_client import AnthropicVisionClient

class FakeStream:
    def __init__(self, reason): self.reason=reason
    async def __aenter__(self): return self
    async def __aexit__(self,*args): pass
    @property
    def text_stream(self):
        async def chunks():
            yield '{"ok":'
            yield 'true}'
        return chunks()
    async def get_final_message(self):
        return SimpleNamespace(stop_reason=self.reason,usage=SimpleNamespace(output_tokens=7))

class FakeClient:
    def __init__(self, reason='end_turn'):
        self.reason=reason
        self.messages=self
    def stream(self,**kwargs):
        self.payload=kwargs
        return FakeStream(self.reason)

def test_stream_uses_image_and_authoritative_usage():
    async def run():
        client=FakeClient()
        adapter=AnthropicVisionClient(client)
        events=[e async for e in adapter.chat_stream('image-data','inspect')]
        assert events[-1]['eval_count']==7
        assert events[-1]['response']=='{"ok":true}'
        assert client.payload['messages'][0]['content'][0]['source']['data']=='image-data'
        assert client.payload['max_tokens']<=3000
    asyncio.run(run())

def test_truncated_output_fails_instead_of_completing():
    async def run():
        with pytest.raises(RuntimeError,match='incomplete'):
            async for _ in AnthropicVisionClient(FakeClient('max_tokens')).chat_stream('data','inspect'):
                pass
    asyncio.run(run())

def test_mapping_uses_provider_schema_with_required_coordinates():
    from backend.schema.diagnostic_map import DiagnosticMap
    async def run():
        client=FakeClient()
        adapter=AnthropicVisionClient(client)
        async for _ in adapter.chat_stream('data','inspect',response_schema=DiagnosticMap.model_json_schema()):
            pass
        output=client.payload['output_config']['format']
        assert output['type']=='json_schema'
        bbox=output['schema']['$defs']['BoundingBox']
        assert 'ymax' in bbox['required']
        assert bbox['additionalProperties'] is False
    asyncio.run(run())
