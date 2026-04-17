"""Analytics Blueprint — metrics and KPI endpoints.

Endpoints:
    POST /api/metrics            Record a metric
    GET  /api/metrics            Get metric series
    POST /api/kpis               Create a KPI
    GET  /api/kpis/dashboard     Get KPI dashboard
"""

from __future__ import annotations

import azure.functions as func

import aos_dispatcher.dispatcher as dispatcher
from .utils import _make_response, _require_json

bp = func.Blueprint()


class AnalyticsFunctions:
    """Handlers for Analytics and Metrics endpoints."""

    @staticmethod
    async def record_metric(req: func.HttpRequest) -> func.HttpResponse:
        """Record a metric data point."""
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.record_metric(body))

    @staticmethod
    async def get_metrics(req: func.HttpRequest) -> func.HttpResponse:
        """Retrieve metric time series."""
        name = req.params.get("name", "")
        return _make_response(dispatcher.get_metrics(name=name))

    @staticmethod
    async def create_kpi(req: func.HttpRequest) -> func.HttpResponse:
        """Create a KPI definition."""
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.create_kpi(body))

    @staticmethod
    async def get_kpi_dashboard(req: func.HttpRequest) -> func.HttpResponse:  # noqa: ARG004
        """Get the KPI dashboard."""
        return _make_response(dispatcher.get_kpi_dashboard())


# ── func.Blueprint wrappers around AnalyticsFunctions class method invocations ──


@bp.function_name("record_metric")
@bp.route(route="metrics", methods=["POST"])
async def record_metric(req: func.HttpRequest) -> func.HttpResponse:
    return await AnalyticsFunctions.record_metric(req)


@bp.function_name("get_metrics")
@bp.route(route="metrics", methods=["GET"])
async def get_metrics(req: func.HttpRequest) -> func.HttpResponse:
    return await AnalyticsFunctions.get_metrics(req)


@bp.function_name("create_kpi")
@bp.route(route="kpis", methods=["POST"])
async def create_kpi(req: func.HttpRequest) -> func.HttpResponse:
    return await AnalyticsFunctions.create_kpi(req)


@bp.function_name("get_kpi_dashboard")
@bp.route(route="kpis/dashboard", methods=["GET"])
async def get_kpi_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    return await AnalyticsFunctions.get_kpi_dashboard(req)
