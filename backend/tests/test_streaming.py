from fastapi.testclient import TestClient


def test_sse_progress_disables_proxy_transformation(monkeypatch):
    from backend import main

    async def events(_request):
        yield 'event: info\ndata: {"type":"info"}\n\n'

    monkeypatch.setattr(main, 'get_public_guard', lambda: None)
    monkeypatch.setattr(main, '_event_stream', events)
    response = TestClient(main.app).post(
        '/v1/analyze', json={'image_base64': 'a' * 16}
    )
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/event-stream')
    assert 'no-transform' in response.headers['cache-control']
    assert response.headers['x-accel-buffering'] == 'no'
    assert 'event: info\n' in response.text
