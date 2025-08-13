from starlette.testclient import TestClient


def test_chat_rate_limit(monkeypatch):
    from backend.server import app
    client = TestClient(app)

    # Monkeypatch limits to be very low during this test
    import backend.server as srv
    # Reset limiter state to avoid cross-test leakage
    from backend.core.ratelimit import limiter
    limiter._events.clear()
    limiter._active_sse.clear()
    monkeypatch.setattr(srv, "_RL_WINDOW", 60, raising=False)
    monkeypatch.setattr(srv, "_RL_CHAT", 3, raising=False)

    # Avoid loading real transformers; fake streaming
    import backend.api.chat as chat_mod  # type: ignore
    def fake_stream_response(**kwargs):
        yield "data: {\"type\": \"token\", \"data\": {\"text\": \"hola\"}}\n\n"
        yield "data: {\"type\": \"done\", \"data\": {}}\n\n"
    monkeypatch.setattr(chat_mod, "stream_response", fake_stream_response, raising=True)

    payload = {"messages": [{"role": "user", "content": "hola"}]}
    for i in range(3):
        r = client.post("/api/chat/stream", json=payload)
        assert r.status_code in (200, 204, 200)
    # 4ª debería ser limitada
    r = client.post("/api/chat/stream", json=payload)
    assert r.status_code == 429


def test_tts_rate_limit(monkeypatch):
    from backend.server import app
    client = TestClient(app)

    import backend.server as srv
    # Reset limiter state to avoid cross-test leakage
    from backend.core.ratelimit import limiter
    limiter._events.clear()
    limiter._active_sse.clear()
    monkeypatch.setattr(srv, "_RL_WINDOW", 60, raising=False)
    monkeypatch.setattr(srv, "_RL_TTS", 3, raising=False)

    for i in range(3):
        r = client.post("/api/tts/synthesize", json={"text": "hola"})
        assert r.status_code == 200
    r = client.post("/api/tts/synthesize", json={"text": "hola"})
    assert r.status_code == 429


