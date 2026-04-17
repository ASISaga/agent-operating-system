"""Shared Azure Functions response helpers used by all Blueprint modules."""

from __future__ import annotations

import json

import azure.functions as func


def _make_response(result: tuple) -> func.HttpResponse:
    """Convert a library ``(body, status_code)`` tuple to ``func.HttpResponse``.

    - ``body is None``   → 204 No Content (no body, no Content-Type)
    - ``body`` is bytes  → raw bytes passed through (proxy responses)
    - ``body`` is dict   → JSON-serialised with ``application/json``
    """
    body, status_code = result
    if body is None:
        return func.HttpResponse(status_code=status_code)
    if isinstance(body, bytes):
        return func.HttpResponse(body, status_code=status_code, mimetype="application/json")
    return func.HttpResponse(
        json.dumps(body),
        status_code=status_code,
        mimetype="application/json",
    )


def _require_json(req: func.HttpRequest) -> tuple:
    """Parse JSON body from request.

    Returns:
        ``(body_dict, None)`` on success.
        ``(None, error_response)`` when the body is not valid JSON.
    """
    try:
        return req.get_json(), None
    except ValueError:
        return None, _make_response(({"error": "Invalid JSON body"}, 400))
