import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as auth_router
from app.api.v1.events import router as events_router
from app.core.config import settings
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Teardown database engine
    await engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Celebration & Event Planner Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware with strict allowlist
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Simple sliding window rate limit simulation in memory (for auth and expensive endpoints)
CALL_TRACKER = {}

# Maximum Request Size limit enforcement (default 10MB)
MAX_REQUEST_BYTES = settings.MAX_REQUEST_SIZE_MB * 1024 * 1024

@app.middleware("http")
async def rate_limit_and_security_headers(request: Request, call_next):
    # Enforce request content length limit
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_BYTES:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "Payload too large. Exceeds allowed limit."}
        )

    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    # Check rate limit on AI chat / Auth endpoints
    if "/chat" in request.url.path or "/auth" in request.url.path:
        history = CALL_TRACKER.get(client_ip, [])
        # Prune older than 60s
        history = [t for t in history if now - t < 60]
        if len(history) >= settings.RATE_LIMIT_CALLS_PER_MINUTE:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please slow down and try again in a minute."}
            )
        history.append(now)
        CALL_TRACKER[client_ip] = history

    response = await call_next(request)
    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Include V1 Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(events_router, prefix=settings.API_V1_PREFIX)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "demo_mode": settings.DEMO_MODE,
        "ai_model": settings.GEMINI_MODEL
    }

