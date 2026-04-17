"""App Registration Blueprint — client application registration endpoints.

Endpoints:
    POST   /api/apps/register     Register a client application
    GET    /api/apps/{app_name}   Get app registration status
    DELETE /api/apps/{app_name}   Deregister a client application
"""

from __future__ import annotations

import azure.functions as func

import aos_dispatcher.dispatcher as dispatcher
from .utils import _make_response, _require_json

bp = func.Blueprint()


class AppRegistrationFunctions:
    """Handlers for client application registration endpoints."""

    @staticmethod
    async def register_app(req: func.HttpRequest) -> func.HttpResponse:
        """Register a client application with AOS.

        Provisions Service Bus queues, topics, and subscriptions for async
        communication.  Returns connection details to the client.

        Request body::

            {
                "app_name": "business-infinity",
                "workflows": ["strategic-review", "market-analysis"],
                "app_id": "optional-azure-ad-app-id"
            }
        """
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.register_app(body))

    @staticmethod
    async def get_app_registration(req: func.HttpRequest) -> func.HttpResponse:
        """Get the registration status of a client application."""
        app_name = req.route_params.get("app_name", "")
        return _make_response(dispatcher.get_app_registration(app_name))

    @staticmethod
    async def deregister_app(req: func.HttpRequest) -> func.HttpResponse:
        """Remove a client application registration."""
        app_name = req.route_params.get("app_name", "")
        return _make_response(dispatcher.deregister_app(app_name))


# ── func.Blueprint wrappers around AppRegistrationFunctions class method invocations ──


@bp.function_name("register_app")
@bp.route(route="apps/register", methods=["POST"])
async def register_app(req: func.HttpRequest) -> func.HttpResponse:
    return await AppRegistrationFunctions.register_app(req)


@bp.function_name("get_app_registration")
@bp.route(route="apps/{app_name}", methods=["GET"])
async def get_app_registration(req: func.HttpRequest) -> func.HttpResponse:
    return await AppRegistrationFunctions.get_app_registration(req)


@bp.function_name("deregister_app")
@bp.route(route="apps/{app_name}", methods=["DELETE"])
async def deregister_app(req: func.HttpRequest) -> func.HttpResponse:
    return await AppRegistrationFunctions.deregister_app(req)
