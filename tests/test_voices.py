import io
import zipfile


def build_dummy_voice_zip():
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, 'w') as z:
        z.writestr('final_model.json', '{}')
        z.writestr('training_config.json', '{}')
        z.writestr('sample.wav', b'\x00' * 2048)
    mem.seek(0)
    return mem


def test_voices_import_and_list(client):
    # List initial
    r = client.get('/api/voices')
    assert r.status_code == 200

    # Import dummy
    f = build_dummy_voice_zip()
    files = {'file': ('model.zip', f, 'application/zip')}
    r = client.post('/api/voices/import?name=Dummy', files=files)
    assert r.status_code == 200
    voice_id = r.json()['voice_id']

    # Verify in list
    r = client.get('/api/voices')
    assert any(v['id'] == voice_id for v in r.json()['voices'])


