"""Azure Functions Blueprint classes for the AOS Dispatcher.

Each sub-module contains a domain-specific class that implements the handler
logic and a ``func.Blueprint`` instance (``bp``) whose routes delegate to that
class.  ``function_app.py`` imports every ``bp`` and registers it with the
top-level ``func.FunctionApp``.

Modules:
    agents          — Agent catalog & interaction endpoints
    analytics       — Metrics and KPI endpoints
    app_registration — Client-application registration endpoints
    audit           — Audit trail / decision-ledger endpoints
    covenants       — Covenant management endpoints
    health          — Health-check endpoint
    knowledge       — Knowledge-base document endpoints
    mcp             — MCP server proxy endpoints
    network         — Network discovery endpoints
    orchestrations  — Orchestration request endpoints + Service Bus trigger
    risks           — Risk-registry endpoints
    utils           — Shared response helpers
"""
