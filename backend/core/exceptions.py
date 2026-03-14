"""Custom exception handlers for consistent API responses."""

from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.core.logger import get_logger

log = get_logger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    log.warning("HTTP %d | %s %s | %s", exc.status_code, request.method, request.url.path, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail, "status": exc.status_code},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for err in exc.errors():
        loc = [str(part) for part in err.get("loc", []) if part != "body"]
        details.append({"field": ".".join(loc), "message": err.get("msg", "Invalid input")})
    log.warning("Validation 422 | %s %s | %d errors", request.method, request.url.path, len(details))
    return JSONResponse(status_code=422, content={"success": False, "error": "Validation failed", "details": details})


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log.exception("Unhandled error | %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"success": False, "error": "Internal server error", "status": 500})
