# Stage 1: Build React App
FROM node:20 AS frontend-build
ARG FRONTEND_ENV
ENV FRONTEND_ENV=${FRONTEND_ENV}
WORKDIR /app
COPY frontend/ /app/
RUN rm /app/.env
RUN touch /app/.env
RUN echo "${FRONTEND_ENV}" | tr ',' '\n' > /app/.env
RUN cat /app/.env
RUN yarn install --frozen-lockfile && yarn build

# Stage 2: Install Python Backend
FROM python:3.11-slim as backend
WORKDIR /app
COPY backend/ /app/
COPY requirements.txt /app/requirements.txt
RUN rm /app/.env

# Stage 3: Final Image (Debian-based)
FROM nginx:stable

# Copy built frontend
COPY --from=frontend-build /app/build /usr/share/nginx/html

# Copy backend
COPY --from=backend /app /backend

# Copy nginx config and entrypoint
COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# System dependencies for audio/TTS and Python
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       python3 python3-venv python3-pip \
       ffmpeg espeak-ng libsndfile1 git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Environment and caches
ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/root/.cache/huggingface \
    TRANSFORMERS_CACHE=/root/.cache/huggingface/transformers \
    TORCH_HOME=/root/.cache/torch

# Preinstall torch/torchaudio CPU wheels, then remaining deps
RUN python3 -m pip install --upgrade pip setuptools wheel \
    && python3 -m pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch torchaudio \
    && python3 -m pip install --no-cache-dir -r /backend/requirements.txt

# Start both services: Uvicorn and Nginx
CMD ["/entrypoint.sh"]
