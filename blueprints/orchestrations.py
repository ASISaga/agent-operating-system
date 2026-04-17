"""Orchestration Blueprint — HTTP endpoints and Service Bus trigger.

Endpoints:
    POST /api/orchestrations              Submit an orchestration request
    GET  /api/orchestrations/{id}         Poll orchestration status
    GET  /api/orchestrations/{id}/result  Retrieve completed result
    POST /api/orchestrations/{id}/cancel  Cancel a running orchestration

Service Bus Triggers:
    aos-orchestration-requests            Process incoming orchestration requests
"""

from __future__ import annotations

import json
import logging

import azure.functions as func

import aos_dispatcher.dispatcher as dispatcher
from .utils import _make_response, _require_json

logger = logging.getLogger(__name__)

bp = func.Blueprint()


class OrchestrationFunctions:
    """HTTP and Service Bus handlers for Orchestration workflows."""

    @staticmethod
    async def submit_orchestration(req: func.HttpRequest) -> func.HttpResponse:
        """Submit an orchestration request.

        Request body (OrchestrationRequest)::

            {
                "orchestration_id": "optional-client-id",
                "agent_ids": ["ceo", "cfo", "cmo"],
                "workflow": "collaborative",
                "task": {"type": "strategic_review", "data": {...}},
                "config": {},
                "callback_url": null
            }
        """
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.process_orchestration_request(body))

    @staticmethod
    async def get_orchestration_status(req: func.HttpRequest) -> func.HttpResponse:
        """Poll the status of a submitted orchestration."""
        orch_id = req.route_params.get("orchestration_id", "")
        return _make_response(dispatcher.get_orchestration_status(orch_id))

    @staticmethod
    async def get_orchestration_result(req: func.HttpRequest) -> func.HttpResponse:
        """Retrieve the final result of a completed orchestration."""
        orch_id = req.route_params.get("orchestration_id", "")
        return _make_response(dispatcher.get_orchestration_result(orch_id))

    @staticmethod
    async def cancel_orchestration(req: func.HttpRequest) -> func.HttpResponse:
        """Cancel a running orchestration."""
        orch_id = req.route_params.get("orchestration_id", "")
        return _make_response(dispatcher.cancel_orchestration(orch_id))

    @staticmethod
    async def service_bus_orchestration_request(msg: func.ServiceBusMessage) -> None:
        """Process an orchestration request received via Service Bus.

        This trigger enables scale-to-zero: AOS sleeps until a message arrives
        on the orchestration requests queue, then wakes up to process it.
        """
        body_bytes = msg.get_body()
        body_str = body_bytes.decode("utf-8")

        try:
            envelope = json.loads(body_str)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Service Bus message: %s", body_str[:200])
            return

        app_name = envelope.get("app_name", "unknown")
        payload = envelope.get("payload", {})

        logger.info(
            "Received orchestration request via Service Bus from app '%s'",
            app_name,
        )

        # Process the request using the same logic as HTTP
        dispatcher.process_orchestration_request(payload, source_app=app_name)

        # TODO: Send result back via Service Bus topic to the client app
        # This would use the aos-orchestration-results topic with a subscription
        # filtered by app_name.


# ── func.Blueprint wrappers around OrchestrationFunctions class method invocations ──


@bp.function_name("submit_orchestration")
@bp.route(route="orchestrations", methods=["POST"])
async def submit_orchestration(req: func.HttpRequest) -> func.HttpResponse:
    return await OrchestrationFunctions.submit_orchestration(req)


@bp.function_name("get_orchestration_status")
@bp.route(route="orchestrations/{orchestration_id}", methods=["GET"])
async def get_orchestration_status(req: func.HttpRequest) -> func.HttpResponse:
    return await OrchestrationFunctions.get_orchestration_status(req)


@bp.function_name("get_orchestration_result")
@bp.route(route="orchestrations/{orchestration_id}/result", methods=["GET"])
async def get_orchestration_result(req: func.HttpRequest) -> func.HttpResponse:
    return await OrchestrationFunctions.get_orchestration_result(req)


@bp.function_name("cancel_orchestration")
@bp.route(route="orchestrations/{orchestration_id}/cancel", methods=["POST"])
async def cancel_orchestration(req: func.HttpRequest) -> func.HttpResponse:
    return await OrchestrationFunctions.cancel_orchestration(req)


@bp.function_name("service_bus_orchestration_request")
@bp.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="aos-orchestration-requests",
    connection="SERVICE_BUS_CONNECTION",
)
async def service_bus_orchestration_request(msg: func.ServiceBusMessage) -> None:
    return await OrchestrationFunctions.service_bus_orchestration_request(msg)
