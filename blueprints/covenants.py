"""Covenants Blueprint — covenant management endpoints.

Endpoints:
    POST /api/covenants                    Create a covenant
    GET  /api/covenants                    List covenants
    GET  /api/covenants/{id}/validate      Validate a covenant
    POST /api/covenants/{id}/sign          Sign a covenant
"""

from __future__ import annotations

import azure.functions as func

import aos_dispatcher.dispatcher as dispatcher
from .utils import _make_response, _require_json

bp = func.Blueprint()


class CovenantFunctions:
    """Handlers for Covenant Management endpoints."""

    @staticmethod
    async def create_covenant(req: func.HttpRequest) -> func.HttpResponse:
        """Create a covenant."""
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.create_covenant(body))

    @staticmethod
    async def list_covenants(req: func.HttpRequest) -> func.HttpResponse:
        """List covenants."""
        status = req.params.get("status")
        return _make_response(dispatcher.list_covenants(status=status))

    @staticmethod
    async def validate_covenant(req: func.HttpRequest) -> func.HttpResponse:
        """Validate a covenant."""
        cov_id = req.route_params.get("covenant_id", "")
        return _make_response(dispatcher.validate_covenant(cov_id))

    @staticmethod
    async def sign_covenant(req: func.HttpRequest) -> func.HttpResponse:
        """Sign a covenant."""
        cov_id = req.route_params.get("covenant_id", "")
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.sign_covenant(cov_id, body))


# ── func.Blueprint wrappers around CovenantFunctions class method invocations ──


@bp.function_name("create_covenant")
@bp.route(route="covenants", methods=["POST"])
async def create_covenant(req: func.HttpRequest) -> func.HttpResponse:
    return await CovenantFunctions.create_covenant(req)


@bp.function_name("list_covenants")
@bp.route(route="covenants", methods=["GET"])
async def list_covenants(req: func.HttpRequest) -> func.HttpResponse:
    return await CovenantFunctions.list_covenants(req)


@bp.function_name("validate_covenant")
@bp.route(route="covenants/{covenant_id}/validate", methods=["GET"])
async def validate_covenant(req: func.HttpRequest) -> func.HttpResponse:
    return await CovenantFunctions.validate_covenant(req)


@bp.function_name("sign_covenant")
@bp.route(route="covenants/{covenant_id}/sign", methods=["POST"])
async def sign_covenant(req: func.HttpRequest) -> func.HttpResponse:
    return await CovenantFunctions.sign_covenant(req)
