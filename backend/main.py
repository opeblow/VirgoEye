"""FastAPI entry point — SSE analysis endpoint, health, CORS, lifespan."""

import asyncio
import json
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import ValidationError

from backend import config
from backend.pipeline.orchestrator import PipelineOrchestrator
from backend.schema.api import AnalyzeRequest, ErrorResponse

orchestrator: PipelineOrchestrator


def _sse(event: dict) -> str:
    """Serialize one internal event dict into an SSE frame."""
    if event.get("type") == "ping":
        return ": ping\n\n"
    name = event.get("type", "message")
    stage = event.get("stage", "")
    data = json.dumps(event, ensure_ascii=False)
    return f"event: {name}\ndata: {data}\n\n"


async def _event_stream(req: AnalyzeRequest) -> AsyncGenerator[str, None]:
    """Wrap orchestrator yields as SSE frames on demand."""
    try:
        async for ev in orchestrator.analyze(req):
            yield _sse(ev)
    except Exception as exc:  # noqa: BLE001 — never crash the stream
        err = ErrorResponse(error="pipeline_error", message=str(exc), stage="system")
        yield _sse({"type": "error", "stage": "system", "data": err.model_dump()})
    finally:
        yield ": end\n\n"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator
    orchestrator = PipelineOrchestrator()
    await orchestrator.initialize()
    app.state.orchestrator = orchestrator
    yield
    await orchestrator.close()


app = FastAPI(
    title="Virgo-Eye Diagnostic Engine",
    version="2.0.0",
    description="Reasoning-first multimodal diagnostics via Chain-of-Visual-Thought.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/v1/health")
async def health() -> Dict[str, Any]:
    snap = orchestrator.gpu.snapshot()
    return {
        "status": "ok",
        "model": orchestrator.model_name,
        "ollama": orchestrator.ollama_ok,
        "quantization": orchestrator._quantization,
        "demo_mode": orchestrator.demo_mode,
        "gpu": {k: v for k, v in snap.items() if k != "available"},
        "server": {"version": "2.0.0", "time": time.time()},
    }


@app.post("/v1/analyze")
async def analyze(req: AnalyzeRequest) -> StreamingResponse:
    return StreamingResponse(
        _event_stream(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/v1/analyze-json")
async def analyze_json(req: AnalyzeRequest) -> JSONResponse:
    """Non-streaming variant that buffers all stage results and returns JSON."""
    final = {
        "map": None,
        "thoughts": None,
        "critic": None,
        "verdict": None,
        "metrics": None,
        "error": None,
    }
    async for ev in orchestrator.analyze(req):
        if ev.get("type") == "error":
            final["error"] = ev
        elif ev.get("type") == "stage_result":
            stage = ev.get("stage")
            if stage == "mapping":
                final["map"] = ev.get("data")
            elif stage == "deliberation":
                final["thoughts"] = ev.get("data")
            elif stage == "critic":
                final["critic"] = ev.get("data")
            elif stage == "synthesis":
                final["verdict"] = ev.get("data")
        elif ev.get("type") == "metrics":
            final["metrics"] = ev.get("data")
    return JSONResponse(final)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(error="validation_error", message=exc.errors()).model_dump(),
    )


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    return """
    <h1>Virgo-Eye Diagnostic Engine</h1>
    <p><a href="/docs">/docs</a> — OpenAPI.</p>
    <p><a href="/v1/health">/v1/health</a> — status.</p>
    """