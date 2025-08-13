from __future__ import annotations

import logging
from typing import Tuple

logger = logging.getLogger("veuplus.metrics")

# Optional Prometheus integration
_PROM_AVAILABLE = False
try:
    from prometheus_client import (
        Counter,
        Histogram,
        CollectorRegistry,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )

    _registry = CollectorRegistry()
    _http_requests_total = Counter(
        "veuplus_http_requests_total",
        "Total HTTP requests",
        labelnames=["method", "path", "status"],
        registry=_registry,
    )
    _http_request_duration = Histogram(
        "veuplus_http_request_duration_seconds",
        "HTTP request duration (seconds)",
        labelnames=["method", "path"],
        registry=_registry,
    )
    _custom_events = Counter(
        "veuplus_events_total",
        "Custom application events",
        labelnames=["name"],
        registry=_registry,
    )
    # Chat specific
    _chat_requests_total = Counter(
        "veuplus_chat_requests_total",
        "Total chat stream requests",
        labelnames=[],
        registry=_registry,
    )
    _chat_response_seconds = Histogram(
        "veuplus_chat_response_seconds",
        "Chat response duration (seconds)",
        labelnames=[],
        registry=_registry,
    )
    _PROM_AVAILABLE = True
except Exception:
    # Fallback counters
    _events_simple = {}


def record_http_request(method: str, path: str, status: int, duration_seconds: float) -> None:
    if _PROM_AVAILABLE:
        try:
            _http_requests_total.labels(method=method, path=path, status=str(status)).inc()
            _http_request_duration.labels(method=method, path=path).observe(duration_seconds)
        except Exception:
            pass
    else:
        # minimal fallback logging
        logger.info("http %s %s %s %.3f", method, path, status, duration_seconds)


def record_event(name: str, value: float | int = 1) -> None:
    if _PROM_AVAILABLE:
        try:
            _custom_events.labels(name=name).inc(value)
        except Exception:
            pass
    else:
        logger.info("metric %s=%s", name, value)


def record_chat_request() -> None:
    if _PROM_AVAILABLE:
        try:
            _chat_requests_total.inc()
        except Exception:
            pass
    else:
        logger.info("metric chat.requests_total=1")


def observe_chat_duration(seconds: float) -> None:
    if _PROM_AVAILABLE:
        try:
            _chat_response_seconds.observe(seconds)
        except Exception:
            pass
    else:
        logger.info("metric chat.response_seconds=%.3f", seconds)


def get_metrics_export() -> Tuple[bytes, str]:
    """Return metrics body and content-type (Prometheus if available)."""
    if _PROM_AVAILABLE:
        try:
            return generate_latest(_registry), CONTENT_TYPE_LATEST
        except Exception as e:
            body = f"# metrics error\nveuplus_metrics_error_total 1\n# {e}".encode()
            return body, "text/plain; version=0.0.4"
    # Fallback: export simple counters
    lines = ["# HELP veuplus_fallback_events_total Fallback events", "# TYPE veuplus_fallback_events_total counter"]
    for k, v in _events_simple.items():
        lines.append(f"veuplus_fallback_events_total{{name=\"{k}\"}} {float(v)}")
    return ("\n".join(lines) + "\n").encode(), "text/plain; version=0.0.4"


