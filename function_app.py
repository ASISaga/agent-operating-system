"""AOS Dispatcher — Azure Functions entry point for the Agent Operating System.

Thin Azure Functions wrapper around the ``aos_dispatcher`` library.  All
business logic lives in ``aos_dispatcher.dispatcher``; this module only handles
Azure Functions-specific concerns by registering domain-specific Blueprints
from the ``blueprints/`` package.

Each Blueprint module contains:
    - A class that implements the handler logic as static methods
    - ``func.Blueprint`` wrappers that delegate to those class methods

Receives all inbound requests and dispatches them to the AOS kernel, analogous
to the dispatcher in a traditional operating system.

All multi-agent orchestration is managed internally by the **Foundry Agent
Service**.  Agents inheriting from PurposeDrivenAgent continue to run as Azure
Functions.  Foundry is an implementation detail — clients interact only with
the standard orchestration endpoints.

AOS Function Apps (3 total — each is a separate Azure Functions deployment):
    aos-dispatcher       This function app — central HTTP/Service Bus dispatcher
    aos-mcp-servers      MCP server deployment & management (ASISaga/aos-mcp-servers)
    aos-realm-of-agents  Agent catalog & registry (ASISaga/aos-realm-of-agents)

    The dispatcher proxies MCP and agent-catalog requests to the dedicated
    function apps via the environment variables MCP_SERVERS_BASE_URL and
    REALM_OF_AGENTS_BASE_URL.  When those variables are not set (e.g. in
    local development) the dispatcher falls back to in-memory stubs.

Blueprint modules:
    blueprints.orchestrations    — OrchestrationFunctions (HTTP + Service Bus)
    blueprints.app_registration  — AppRegistrationFunctions
    blueprints.health            — HealthFunctions
    blueprints.knowledge         — KnowledgeFunctions
    blueprints.risks             — RiskFunctions
    blueprints.audit             — AuditFunctions
    blueprints.covenants         — CovenantFunctions
    blueprints.analytics         — AnalyticsFunctions
    blueprints.mcp               — MCPFunctions
    blueprints.agents            — AgentFunctions
    blueprints.network           — NetworkFunctions

Endpoints — Orchestrations (all managed by Foundry Agent Service):
    POST /api/orchestrations              Submit an orchestration request
    GET  /api/orchestrations/{id}         Poll orchestration status
    GET  /api/orchestrations/{id}/result  Retrieve completed result
    POST /api/orchestrations/{id}/cancel  Cancel a running orchestration

Endpoints — Knowledge Base:
    POST /api/knowledge/documents         Create a document
    GET  /api/knowledge/documents         Search documents
    GET  /api/knowledge/documents/{id}    Get document by ID
    POST /api/knowledge/documents/{id}    Update document
    DELETE /api/knowledge/documents/{id}  Delete document

Endpoints — Risk Registry:
    POST /api/risks                       Register a risk
    GET  /api/risks                       List risks
    POST /api/risks/{id}/assess           Assess a risk
    POST /api/risks/{id}/status           Update risk status
    POST /api/risks/{id}/mitigate         Add mitigation plan

Endpoints — Audit Trail:
    POST /api/audit/decisions             Log a decision
    GET  /api/audit/decisions             Get decision history
    GET  /api/audit/trail                 Get audit trail

Endpoints — Covenants:
    POST /api/covenants                   Create a covenant
    GET  /api/covenants                   List covenants
    GET  /api/covenants/{id}/validate     Validate a covenant
    POST /api/covenants/{id}/sign         Sign a covenant

Endpoints — Analytics:
    POST /api/metrics                     Record a metric
    GET  /api/metrics                     Get metric series
    POST /api/kpis                        Create a KPI
    GET  /api/kpis/dashboard              Get KPI dashboard

Endpoints — MCP (proxied to aos-mcp-servers via MCP_SERVERS_BASE_URL):
    GET  /api/mcp/servers                 List MCP servers
    POST /api/mcp/servers/{s}/tools/{t}   Call an MCP tool
    GET  /api/mcp/servers/{s}/status      Get MCP server status

Endpoints — Agents:
    GET  /api/agents                      List agents (proxied to aos-realm-of-agents)
    GET  /api/agents/{id}                 Get agent descriptor (proxied to aos-realm-of-agents)
    POST /api/agents/register             Register a PurposeDrivenAgent with Foundry
    POST /api/agents/{id}/ask             Ask an agent
    POST /api/agents/{id}/send            Send to an agent
    POST /api/agents/{id}/message         Send message via Foundry bridge

Endpoints — Network:
    POST /api/network/discover            Discover peers
    POST /api/network/{id}/join           Join a network
    GET  /api/network                     List networks

Endpoints — App Registration:
    POST /api/apps/register               Register a client application
    GET  /api/apps/{app_name}             Get app registration status
    DELETE /api/apps/{app_name}           Deregister a client application

Endpoints — Health:
    GET  /api/health                      Health check

Service Bus Triggers:
    aos-orchestration-requests            Process incoming orchestration requests
"""

from __future__ import annotations

import azure.functions as func

from blueprints.agents import bp as agents_bp
from blueprints.analytics import bp as analytics_bp
from blueprints.app_registration import bp as app_registration_bp
from blueprints.audit import bp as audit_bp
from blueprints.covenants import bp as covenants_bp
from blueprints.health import bp as health_bp
from blueprints.knowledge import bp as knowledge_bp
from blueprints.mcp import bp as mcp_bp
from blueprints.network import bp as network_bp
from blueprints.orchestrations import bp as orchestrations_bp
from blueprints.risks import bp as risks_bp

app = func.FunctionApp()

app.register_blueprint(orchestrations_bp)
app.register_blueprint(app_registration_bp)
app.register_blueprint(health_bp)
app.register_blueprint(knowledge_bp)
app.register_blueprint(risks_bp)
app.register_blueprint(audit_bp)
app.register_blueprint(covenants_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(mcp_bp)
app.register_blueprint(agents_bp)
app.register_blueprint(network_bp)
