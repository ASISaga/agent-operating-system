"""Agents Blueprint — agent catalog and interaction endpoints.

GET /api/agents and GET /api/agents/{id} proxy to *aos-realm-of-agents*
(ASISaga/aos-realm-of-agents).  Configure REALM_OF_AGENTS_BASE_URL in App
Settings to point at the deployed instance.

Endpoints:
    GET  /api/agents                  List agents (proxied to aos-realm-of-agents)
    GET  /api/agents/{id}             Get agent descriptor (proxied)
    POST /api/agents/register         Register a PurposeDrivenAgent with Foundry
    POST /api/agents/{id}/ask         Ask an agent
    POST /api/agents/{id}/send        Send to an agent
    POST /api/agents/{id}/message     Send message via Foundry bridge
"""

from __future__ import annotations

import azure.functions as func

import aos_dispatcher.dispatcher as dispatcher
from .utils import _make_response, _require_json

bp = func.Blueprint()


class AgentFunctions:
    """Handlers for Agent Catalog and Interaction endpoints."""

    @staticmethod
    async def list_agents(req: func.HttpRequest) -> func.HttpResponse:
        """List agents from the realm-of-agents catalog (proxied to aos-realm-of-agents)."""
        agent_type = req.params.get("agent_type")
        return _make_response(await dispatcher.list_agents(agent_type=agent_type))

    @staticmethod
    async def get_agent_descriptor(req: func.HttpRequest) -> func.HttpResponse:
        """Get an agent descriptor from the realm-of-agents catalog."""
        agent_id = req.route_params.get("agent_id", "")
        return _make_response(await dispatcher.get_agent_descriptor(agent_id))

    @staticmethod
    async def ask_agent(req: func.HttpRequest) -> func.HttpResponse:
        """Direct message to an agent."""
        agent_id = req.route_params.get("agent_id", "")
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.ask_agent(agent_id, body))

    @staticmethod
    async def send_to_agent(req: func.HttpRequest) -> func.HttpResponse:
        """Fire-and-forget message to an agent."""
        agent_id = req.route_params.get("agent_id", "")
        return _make_response(dispatcher.send_to_agent(agent_id))

    @staticmethod
    async def register_agent(req: func.HttpRequest) -> func.HttpResponse:
        """Register a PurposeDrivenAgent with the Foundry Agent Service.

        Request body::

            {
                "agent_id": "ceo",
                "purpose": "Strategic leadership and executive decision-making",
                "name": "CEO Agent",
                "adapter_name": "leadership",
                "capabilities": ["strategic_planning", "decision_making"],
                "model": "gpt-4o"
            }
        """
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.register_agent(body))

    @staticmethod
    async def message_agent(req: func.HttpRequest) -> func.HttpResponse:
        """Send a message to a PurposeDrivenAgent via the Foundry message bridge.

        Request body::

            {
                "message": "What is the strategic direction?",
                "orchestration_id": "optional-orch-id",
                "direction": "foundry_to_agent"
            }
        """
        agent_id = req.route_params.get("agent_id", "")
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.message_agent(agent_id, body))


# ── func.Blueprint wrappers around AgentFunctions class method invocations ──


@bp.function_name("list_agents")
@bp.route(route="agents", methods=["GET"])
async def list_agents(req: func.HttpRequest) -> func.HttpResponse:
    return await AgentFunctions.list_agents(req)


@bp.function_name("get_agent_descriptor")
@bp.route(route="agents/{agent_id}", methods=["GET"])
async def get_agent_descriptor(req: func.HttpRequest) -> func.HttpResponse:
    return await AgentFunctions.get_agent_descriptor(req)


@bp.function_name("ask_agent")
@bp.route(route="agents/{agent_id}/ask", methods=["POST"])
async def ask_agent(req: func.HttpRequest) -> func.HttpResponse:
    return await AgentFunctions.ask_agent(req)


@bp.function_name("send_to_agent")
@bp.route(route="agents/{agent_id}/send", methods=["POST"])
async def send_to_agent(req: func.HttpRequest) -> func.HttpResponse:
    return await AgentFunctions.send_to_agent(req)


@bp.function_name("register_agent")
@bp.route(route="agents/register", methods=["POST"])
async def register_agent(req: func.HttpRequest) -> func.HttpResponse:
    return await AgentFunctions.register_agent(req)


@bp.function_name("message_agent")
@bp.route(route="agents/{agent_id}/message", methods=["POST"])
async def message_agent(req: func.HttpRequest) -> func.HttpResponse:
    return await AgentFunctions.message_agent(req)
