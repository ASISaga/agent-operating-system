"""Health Blueprint — system health-check endpoint.

Endpoints:
    GET /api/health   Health check
"""

from __future__ import annotations

import azure.functions as func

import aos_dispatcher.dispatcher as dispatcher
from .utils import _make_response

bp = func.Blueprint()


class HealthFunctions:
    """Handler for the health-check endpoint."""

    @staticmethod
    async def health(req: func.HttpRequest) -> func.HttpResponse:  # noqa: ARG001
        """Health check endpoint."""
        return _make_response(dispatcher.health())


# ── func.Blueprint wrapper around HealthFunctions class method invocation ──


@bp.function_name("health")
@bp.route(route="health", methods=["GET"])
async def health(req: func.HttpRequest) -> func.HttpResponse:
    return await HealthFunctions.health(req)
