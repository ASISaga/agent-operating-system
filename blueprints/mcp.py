"""MCP Blueprint — MCP server proxy endpoints.

These endpoints proxy to the *aos-mcp-servers* function app
(ASISaga/aos-mcp-servers).  Configure MCP_SERVERS_BASE_URL in App Settings to
point at the deployed aos-mcp-servers instance.  When the variable is unset a
minimal stub response is returned so local development stays functional.

Endpoints:
    GET  /api/mcp/servers                  List MCP servers
    POST /api/mcp/servers/{s}/tools/{t}    Call an MCP tool
    GET  /api/mcp/servers/{s}/status       Get MCP server status
"""

from __future__ import annotations

import azure.functions as func

import aos_dispatcher.dispatcher as dispatcher
from .utils import _make_response

bp = func.Blueprint()


class MCPFunctions:
    """Handlers for MCP Server Integration endpoints (proxied to aos-mcp-servers)."""

    @staticmethod
    async def list_mcp_servers(req: func.HttpRequest) -> func.HttpResponse:
        """List available MCP servers (proxied to aos-mcp-servers)."""
        server_type = req.params.get("server_type")
        return _make_response(await dispatcher.list_mcp_servers(server_type=server_type))

    @staticmethod
    async def call_mcp_tool(req: func.HttpRequest) -> func.HttpResponse:
        """Invoke a tool on an MCP server (proxied to aos-mcp-servers)."""
        server = req.route_params.get("server", "")
        tool = req.route_params.get("tool", "")
        return _make_response(await dispatcher.call_mcp_tool(server, tool, req.get_body()))

    @staticmethod
    async def get_mcp_server_status(req: func.HttpRequest) -> func.HttpResponse:
        """Get MCP server status (proxied to aos-mcp-servers)."""
        server = req.route_params.get("server", "")
        return _make_response(await dispatcher.get_mcp_server_status(server))


# ── func.Blueprint wrappers around MCPFunctions class method invocations ──


@bp.function_name("list_mcp_servers")
@bp.route(route="mcp/servers", methods=["GET"])
async def list_mcp_servers(req: func.HttpRequest) -> func.HttpResponse:
    return await MCPFunctions.list_mcp_servers(req)


@bp.function_name("call_mcp_tool")
@bp.route(route="mcp/servers/{server}/tools/{tool}", methods=["POST"])
async def call_mcp_tool(req: func.HttpRequest) -> func.HttpResponse:
    return await MCPFunctions.call_mcp_tool(req)


@bp.function_name("get_mcp_server_status")
@bp.route(route="mcp/servers/{server}/status", methods=["GET"])
async def get_mcp_server_status(req: func.HttpRequest) -> func.HttpResponse:
    return await MCPFunctions.get_mcp_server_status(req)
