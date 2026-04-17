"""Knowledge Base Blueprint — document CRUD endpoints.

Endpoints:
    POST   /api/knowledge/documents          Create a document
    GET    /api/knowledge/documents          Search documents
    GET    /api/knowledge/documents/{id}     Get document by ID
    POST   /api/knowledge/documents/{id}     Update document
    DELETE /api/knowledge/documents/{id}     Delete document
"""

from __future__ import annotations

import azure.functions as func

import aos_dispatcher.dispatcher as dispatcher
from .utils import _make_response, _require_json

bp = func.Blueprint()


class KnowledgeFunctions:
    """Handlers for Knowledge Base document endpoints."""

    @staticmethod
    async def create_document(req: func.HttpRequest) -> func.HttpResponse:
        """Create a knowledge document."""
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.create_document(body))

    @staticmethod
    async def get_document(req: func.HttpRequest) -> func.HttpResponse:
        """Get a knowledge document by ID."""
        doc_id = req.route_params.get("document_id", "")
        return _make_response(dispatcher.get_document(doc_id))

    @staticmethod
    async def search_documents(req: func.HttpRequest) -> func.HttpResponse:
        """Search knowledge documents."""
        query = req.params.get("query") or ""
        doc_type = req.params.get("doc_type")
        limit = int(req.params.get("limit", "10"))
        return _make_response(dispatcher.search_documents(query=query, doc_type=doc_type, limit=limit))

    @staticmethod
    async def update_document(req: func.HttpRequest) -> func.HttpResponse:
        """Update a knowledge document's content."""
        doc_id = req.route_params.get("document_id", "")
        body, err = _require_json(req)
        if err:
            return err
        return _make_response(dispatcher.update_document(doc_id, body))

    @staticmethod
    async def delete_document(req: func.HttpRequest) -> func.HttpResponse:
        """Delete a knowledge document."""
        doc_id = req.route_params.get("document_id", "")
        return _make_response(dispatcher.delete_document(doc_id))


# ── func.Blueprint wrappers around KnowledgeFunctions class method invocations ──


@bp.function_name("create_document")
@bp.route(route="knowledge/documents", methods=["POST"])
async def create_document(req: func.HttpRequest) -> func.HttpResponse:
    return await KnowledgeFunctions.create_document(req)


@bp.function_name("search_documents")
@bp.route(route="knowledge/documents", methods=["GET"])
async def search_documents(req: func.HttpRequest) -> func.HttpResponse:
    return await KnowledgeFunctions.search_documents(req)


@bp.function_name("get_document")
@bp.route(route="knowledge/documents/{document_id}", methods=["GET"])
async def get_document(req: func.HttpRequest) -> func.HttpResponse:
    return await KnowledgeFunctions.get_document(req)


@bp.function_name("update_document")
@bp.route(route="knowledge/documents/{document_id}", methods=["POST"])
async def update_document(req: func.HttpRequest) -> func.HttpResponse:
    return await KnowledgeFunctions.update_document(req)


@bp.function_name("delete_document")
@bp.route(route="knowledge/documents/{document_id}", methods=["DELETE"])
async def delete_document(req: func.HttpRequest) -> func.HttpResponse:
    return await KnowledgeFunctions.delete_document(req)
