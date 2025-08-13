Contiene, de forma clara y ejecutable:



\- Arranque local (CPU)

&nbsp; - Comando con `scripts/start\_api\_cpu.ps1` y URL `http://localhost:8010`.

\- Arranque con Docker (dev)

&nbsp; - `docker compose -f docker-compose.backend.yml up --build`.

\- Arranque producción (Gunicorn + Nginx)

&nbsp; - Contenido de `nginx.prod.conf`.

&nbsp; - `docker compose -f docker-compose.prod.yml up --build`.

&nbsp; - URL `http://localhost`.

\- Endpoints

&nbsp; - `GET /api/health`, `GET /metrics`, `POST /api/chat/stream`, `POST /api/tts/synthesize`, `POST /api/asr/transcribe`.

\- Variables de entorno

&nbsp; - `TRANSFORMERS\_PROVIDER/MODEL/MAX\_LENGTH`, `MAX\_UPLOAD\_SIZE\_MB`, `DEVELOPMENT\_MODE`.

&nbsp; - Rate limiting: `RATE\_LIMIT\_GLOBAL\_RPM`, `RATE\_LIMIT\_CHAT\_RPM`, `RATE\_LIMIT\_TTS\_RPM`, `RATE\_LIMIT\_ASR\_RPM`, `RATE\_LIMIT\_WINDOW\_S`.

\- Tests

&nbsp; - `DISABLE\_TRANSFORMERS\_INIT=1` y `pytest tests/ -v`.

\- Métricas

&nbsp; - Series HTTP y Chat (Prometheus).

\- Logs

&nbsp; - JSON con `request\_id`, método, path, status, `duration\_ms`.

\- Notas

&nbsp; - Rate limit in‑memory (para 1 instancia), ASR/TTS placeholders.

