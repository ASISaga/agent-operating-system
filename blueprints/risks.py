"""Risk Registry Blueprint — risk management endpoints.

Endpoints:
    POST /api/risks                    Register a risk
    GET  /api/risks                    List risks
    POST /api/risks/{id}/assess        Assess a risk
    POST /api/risks/{id}/status        Update risk status
    POST /api/risks/{id}/mitigate      Add mitigation plan
"""

from __future__ import annotations

import azure.functions as func

import aos_dispatcher.dispatcher as dispatcher
from .utils import _make_response, _require_json

bp = func.Blueprint()


class RiskFunctions:
    """Handlers for Risk Registry endpoints."""

    @staticmethod
    async def register_risk(req: func.HttpRequest) -> func.HttpResponse:
        """Register a new risk."""
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.register_risk(body))

    @staticmethod
    async def list_risks(req: func.HttpRequest) -> func.HttpResponse:
        """List risks with optional filters."""
        status = req.params.get("status")
        category = req.params.get("category")
        return _make_response(dispatcher.list_risks(status=status, category=category))

    @staticmethod
    async def assess_risk(req: func.HttpRequest) -> func.HttpResponse:
        """Assess a risk."""
        risk_id = req.route_params.get("risk_id", "")
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.assess_risk(risk_id, body))

    @staticmethod
    async def update_risk_status(req: func.HttpRequest) -> func.HttpResponse:
        """Update risk status."""
        risk_id = req.route_params.get("risk_id", "")
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.update_risk_status(risk_id, body))

    @staticmethod
    async def add_mitigation_plan(req: func.HttpRequest) -> func.HttpResponse:
        """Add a mitigation plan to a risk."""
        risk_id = req.route_params.get("risk_id", "")
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.add_mitigation_plan(risk_id, body))


# ── func.Blueprint wrappers around RiskFunctions class method invocations ──


@bp.function_name("register_risk")
@bp.route(route="risks", methods=["POST"])
async def register_risk(req: func.HttpRequest) -> func.HttpResponse:
    return await RiskFunctions.register_risk(req)


@bp.function_name("list_risks")
@bp.route(route="risks", methods=["GET"])
async def list_risks(req: func.HttpRequest) -> func.HttpResponse:
    return await RiskFunctions.list_risks(req)


@bp.function_name("assess_risk")
@bp.route(route="risks/{risk_id}/assess", methods=["POST"])
async def assess_risk(req: func.HttpRequest) -> func.HttpResponse:
    return await RiskFunctions.assess_risk(req)


@bp.function_name("update_risk_status")
@bp.route(route="risks/{risk_id}/status", methods=["POST"])
async def update_risk_status(req: func.HttpRequest) -> func.HttpResponse:
    return await RiskFunctions.update_risk_status(req)


@bp.function_name("add_mitigation_plan")
@bp.route(route="risks/{risk_id}/mitigate", methods=["POST"])
async def add_mitigation_plan(req: func.HttpRequest) -> func.HttpResponse:
    return await RiskFunctions.add_mitigation_plan(req)
