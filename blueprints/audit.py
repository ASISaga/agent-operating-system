"""Audit Trail Blueprint — decision ledger and audit trail endpoints.

Endpoints:
    POST /api/audit/decisions   Log a decision
    GET  /api/audit/decisions   Get decision history
    GET  /api/audit/trail       Get audit trail
"""

from __future__ import annotations

import azure.functions as func

import aos_dispatcher.dispatcher as dispatcher
from .utils import _make_response, _require_json

bp = func.Blueprint()


class AuditFunctions:
    """Handlers for Audit Trail / Decision Ledger endpoints."""

    @staticmethod
    async def log_decision(req: func.HttpRequest) -> func.HttpResponse:
        """Log a decision."""
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.log_decision(body))

    @staticmethod
    async def get_decision_history(req: func.HttpRequest) -> func.HttpResponse:
        """Get decision history."""
        orch_id = req.params.get("orchestration_id")
        agent_id = req.params.get("agent_id")
        return _make_response(dispatcher.get_decision_history(orch_id=orch_id, agent_id=agent_id))

    @staticmethod
    async def get_audit_trail(req: func.HttpRequest) -> func.HttpResponse:  # noqa: ARG004
        """Get the audit trail."""
        return _make_response(dispatcher.get_audit_trail())


# ── func.Blueprint wrappers around AuditFunctions class method invocations ──


@bp.function_name("log_decision")
@bp.route(route="audit/decisions", methods=["POST"])
async def log_decision(req: func.HttpRequest) -> func.HttpResponse:
    return await AuditFunctions.log_decision(req)


@bp.function_name("get_decision_history")
@bp.route(route="audit/decisions", methods=["GET"])
async def get_decision_history(req: func.HttpRequest) -> func.HttpResponse:
    return await AuditFunctions.get_decision_history(req)


@bp.function_name("get_audit_trail")
@bp.route(route="audit/trail", methods=["GET"])
async def get_audit_trail(req: func.HttpRequest) -> func.HttpResponse:
    return await AuditFunctions.get_audit_trail(req)
