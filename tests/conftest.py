import os
import sys
import importlib
import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Point SQLite to a temp DB
    monkeypatch.setenv('VEUPLUS_DB_PATH', str(tmp_path / 'veuplus_test.db'))
    # Keep transformers local and tiny if ever used
    monkeypatch.setenv('TRANSFORMERS_PROVIDER', 'local')
    monkeypatch.setenv('TRANSFORMERS_MODEL', 'gpt2')
    monkeypatch.setenv('DISABLE_TRANSFORMERS_INIT', '1')
    # Ensure fresh imports for config/db/server
    for mod in ['backend.server', 'backend.database_sql']:
        if mod in sys.modules:
            del sys.modules[mod]
    import backend.server as server
    app = server.app
    return TestClient(app)


