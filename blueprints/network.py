"""Network Blueprint — network discovery endpoints.

Endpoints:
    POST /api/network/discover        Discover peers
    POST /api/network/{id}/join       Join a network
    GET  /api/network                 List networks
"""

from __future__ import annotations

import azure.functions as func

import aos_dispatcher.dispatcher as dispatcher
from .utils import _make_response

bp = func.Blueprint()


class NetworkFunctions:
    """Handlers for Network Discovery endpoints."""

    @staticmethod
    async def discover_peers(req: func.HttpRequest) -> func.HttpResponse:  # noqa: ARG001
        """Discover peer applications."""
        return _make_response(dispatcher.discover_peers())

    @staticmethod
    async def join_network(req: func.HttpRequest) -> func.HttpResponse:  # noqa: ARG001
        """Join a network."""
        network_id = req.route_params.get("network_id", "")
        return _make_response(dispatcher.join_network(network_id))

    @staticmethod
    async def list_networks(req: func.HttpRequest) -> func.HttpResponse:  # noqa: ARG001
        """List available networks."""
        return _make_response(dispatcher.list_networks())


# ── func.Blueprint wrappers around NetworkFunctions class method invocations ──


@bp.function_name("discover_peers")
@bp.route(route="network/discover", methods=["POST"])
async def discover_peers(req: func.HttpRequest) -> func.HttpResponse:
    return await NetworkFunctions.discover_peers(req)


@bp.function_name("join_network")
@bp.route(route="network/{network_id}/join", methods=["POST"])
async def join_network(req: func.HttpRequest) -> func.HttpResponse:
    return await NetworkFunctions.join_network(req)


@bp.function_name("list_networks")
@bp.route(route="network", methods=["GET"])
async def list_networks(req: func.HttpRequest) -> func.HttpResponse:
    return await NetworkFunctions.list_networks(req)
