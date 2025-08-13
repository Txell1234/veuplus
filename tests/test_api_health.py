from starlette.testclient import TestClient


def test_api_health_endpoint():
    from backend.server import app
    client = TestClient(app)
    r = client.get('/api/health')
    assert r.status_code == 200
    data = r.json()
    assert data.get('status') in ('healthy', 'ok', 'ready')
