import pytest
from fastapi.testclient import TestClient
from backend.public_guard import PublicGuard, GuardError


def guard(tmp_path, **options):
    return PublicGuard(tmp_path / 'usage.db', 'test-code', options.get('limit', 10),
                       options.get('budget', 1), 2, 10)


def test_wrong_code_does_not_consume_admission(tmp_path):
    instance = guard(tmp_path, limit=1)
    with pytest.raises(GuardError) as error:
        instance.admit('wrong')
    assert error.value.status == 401
    instance.admit('test-code')


def test_open_access_preserves_persistent_limits(tmp_path):
    path = tmp_path / 'open.db'
    instance = PublicGuard(path, '', 2, .04, 2, 10, require_access_code=False)
    instance.admit('')
    instance.admit('irrelevant')
    instance.reserve(1000, 3000)
    restarted = PublicGuard(path, '', 2, .04, 2, 10, require_access_code=False)
    with pytest.raises(GuardError, match='inspection limit'):
        restarted.admit('')
    with pytest.raises(GuardError, match='budget is exhausted'):
        restarted.reserve(1000, 3000)


def test_missing_code_requires_explicit_open_access(tmp_path):
    with pytest.raises(ValueError):
        PublicGuard(tmp_path / 'closed.db', '', 2, 1, 2, 10)


@pytest.mark.parametrize('path', ['/v1/analyze', '/v1/analyze-json'])
def test_open_routes_admit_without_code(tmp_path, monkeypatch, path):
    from backend import main
    instance = PublicGuard(tmp_path / 'open.db', '', 1, 1, 2, 10,
                           require_access_code=False)
    monkeypatch.setattr(main, 'get_public_guard', lambda: instance)
    client = TestClient(main.app)
    # Invalid image payload reaches request validation rather than a code prompt.
    assert client.post(path, json={'image_base64': 'unused'}).status_code == 422
    assert client.post(path, json={'image_base64': 'unused'}).status_code == 429


def test_request_limit_survives_restart(tmp_path):
    guard(tmp_path, limit=1).admit('test-code')
    with pytest.raises(GuardError, match='inspection limit'):
        guard(tmp_path, limit=1).admit('test-code')


def test_global_rate_limit(tmp_path):
    instance = guard(tmp_path)
    instance.admit('test-code')
    instance.admit('test-code')
    with pytest.raises(GuardError, match='wait a minute'):
        instance.admit('test-code')


def test_reservations_enforce_persistent_budget(tmp_path):
    instance = guard(tmp_path, budget=.04)
    assert instance.reserve(1000, 3000) == 33424
    with pytest.raises(GuardError, match='budget is exhausted'):
        guard(tmp_path, budget=.04).reserve(1000, 3000)


@pytest.mark.parametrize('budget', [0, -1, float('inf'), float('nan')])
def test_incomplete_budget_fails_closed(tmp_path, budget):
    with pytest.raises(ValueError):
        guard(tmp_path, budget=budget)


@pytest.mark.parametrize('path', ['/v1/analyze', '/v1/analyze-json'])
def test_both_analysis_routes_require_access(tmp_path, monkeypatch, path):
    from backend import main
    instance = guard(tmp_path)
    monkeypatch.setattr(main, 'get_public_guard', lambda: instance)
    # No lifespan/model calls needed: admission must reject before analysis.
    client = TestClient(main.app)
    response = client.post(path, json={'image_base64':'unused'})
    assert response.status_code == 401
    assert 'access code' in response.json()['detail']
