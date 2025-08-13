import types

from starlette.testclient import TestClient
from fastapi import FastAPI


def test_chat_stream_sse(monkeypatch):
    # Build minimal app mounting only chat router
    import backend.api.chat as chat_mod  # type: ignore
    app = FastAPI()
    app.include_router(chat_mod.router)
    client = TestClient(app)

    def fake_stream_response(**kwargs):
        # simple generator producing two tokens and done
        yield "data: {\"type\": \"token\", \"data\": {\"text\": \"Hola\"}}\n\n"
        yield "data: {\"type\": \"token\", \"data\": {\"text\": \"!\"}}\n\n"
        yield "data: {\"type\": \"done\", \"data\": {}}\n\n"

    monkeypatch.setattr(chat_mod, "stream_response", fake_stream_response, raising=True)

    payload = {"messages": [{"role": "user", "content": "test"}]}

    with client.stream("POST", "/api/chat/stream", json=payload) as r:
        assert r.status_code == 200
        assert "text/event-stream" in r.headers.get("content-type", "")
        chunks = list(r.iter_text())
        assert any("\"type\": \"token\"" in c for c in chunks)
        assert any("\"type\": \"done\"" in c for c in chunks)

    # No metrics check in this minimal app

