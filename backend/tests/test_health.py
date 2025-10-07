def test_health(test_client):
    resp = test_client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_health_is_public_in_production(monkeypatch):
    # Simulate production env with an auth token, but ensure health is public
    from app.main import create_app
    from fastapi.testclient import TestClient

    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("APP_MINIMAL", "1")
    monkeypatch.setenv("AUTH_BEARER_TOKEN", "secret")

    app = create_app(minimal=True)
    client = TestClient(app)

    # No Authorization header should still allow health
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

    # Non-public route should still enforce auth (e.g., metrics route when enabled may be public)
    # Use a guaranteed non-existent route to assert 401 vs 404 ambiguity avoided; pick /api/v1/agents/analyze path method mismatch
    r2 = client.post("/api/v1/agents/analyze", json={"user_id": "u", "query": "q"})
    # Either 401 (auth) or 404 (minimal router) is acceptable in minimal mode; ensure not 200
    assert r2.status_code in {401, 404}
