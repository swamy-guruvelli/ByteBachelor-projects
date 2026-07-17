import json
import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("system-design-lab")

app = FastAPI(
    title="Gateway and Identity",
    version="0.1.0",
    description="Executable contract shell. Domain implementation is planned.",
)


@app.exception_handler(StarletteHTTPException)
async def handle_http_error(request: Request, error: StarletteHTTPException):
    return JSONResponse(
        status_code=error.status_code,
        media_type="application/problem+json",
        content={
            "type": f"urn:system-design-lab:problem:http-{error.status_code}",
            "title": "HTTP request failed",
            "status": error.status_code,
            "detail": str(error.detail),
            "instance": request.url.path,
        },
    )


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    started = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(json.dumps({
        "event": "request.completed",
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round((perf_counter() - started) * 1000, 2),
        "request_id": request_id,
    }))
    return response


@app.get("/health/live", tags=["health"])
def live():
    return {"status": "alive"}


@app.get("/health/ready", tags=["health"])
def ready():
    return {"status": "ready", "milestone": "contract-shell"}


@app.get("/api/v1/planned", tags=["roadmap"])
def planned(request: Request):
    return JSONResponse(
        status_code=501,
        media_type="application/problem+json",
        content={
            "type": "urn:system-design-lab:problem:milestone-planned",
            "title": "Domain milestone not implemented",
            "status": 501,
            "detail": "Gateway and Identity is scheduled in roadmap order.",
            "instance": str(request.url.path),
        },
    )