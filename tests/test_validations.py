from starlette.testclient import TestClient


def _app():
    from backend.server import app
    return app


def test_health_extended_fields():
    client = TestClient(_app())
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert "transformers" in data and "limits" in data and "flags" in data


def test_tts_text_validation():
    client = TestClient(_app())
    # empty
    r = client.post("/api/tts/synthesize", json={"text": ""})
    assert r.status_code == 422
    # too long
    r = client.post("/api/tts/synthesize", json={"text": "x" * 2000})
    assert r.status_code == 422


def test_chat_messages_validation():
    client = TestClient(_app())
    # empty messages
    r = client.post("/api/chat/stream", json={"messages": []})
    assert r.status_code in (400, 422)
    # too many messages
    msgs = [{"role": "user", "content": "hi"}] * 70
    r = client.post("/api/chat/stream", json={"messages": msgs})
    assert r.status_code in (400, 422)


def test_asr_size_limit():
    client = TestClient(_app())
    # create >20MB in memory (simulate) — use 21MB zero bytes
    big = b"0" * (21 * 1024 * 1024)
    files = {"file": ("big.wav", big, "audio/wav")}
    r = client.post("/api/asr/transcribe", files=files)
    assert r.status_code == 413


