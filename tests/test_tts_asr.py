from starlette.testclient import TestClient


def test_tts_placeholder():
    from backend.server import app
    client = TestClient(app)
    r = client.post("/api/tts/synthesize", json={"text": "Hola"})
    assert r.status_code == 200
    data = r.json()
    assert "audio_base64" in data and data["mime"] == "audio/wav"


def test_asr_placeholder():
    from backend.server import app
    client = TestClient(app)
    # Crear un wav de 10ms en memoria
    import wave
    from io import BytesIO
    sr = 16000
    buf = BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(b"\x00\x00" * int(sr * 0.01))
    buf.seek(0)
    files = {"file": ("test.wav", buf.getvalue(), "audio/wav")}
    r = client.post("/api/asr/transcribe", files=files)
    assert r.status_code == 200
    data = r.json()
    assert "text" in data


