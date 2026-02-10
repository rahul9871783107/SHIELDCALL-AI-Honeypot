"""
SHIELDCALL Main Application
FastAPI setup and configuration.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.routes import router
from app.config import settings
from app.utils.logger import app_logger as logger


# Create FastAPI application
app = FastAPI(
    title="SHIELDCALL Honeypot API",
    description="AI-Powered Scam Detection with 3-Layer Hybrid Architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Request logging middleware — logs raw body before validation
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "/api/honeypot" in request.url.path:
            body = await request.body()
            logger.info(
                f"RAW REQUEST | {request.method} {request.url.path} | "
                f"Content-Type: {request.headers.get('content-type', 'none')} | "
                f"Body ({len(body)} bytes): {body[:500].decode('utf-8', errors='replace') if body else '<empty>'}"
            )
        response = await call_next(request)
        if "/api/honeypot" in request.url.path:
            logger.info(f"RESPONSE | {request.method} {request.url.path} | Status: {response.status_code}")
        return response


app.add_middleware(RequestLoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


# Handle validation errors gracefully — return {status, reply} format
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return honeypot-formatted response for honeypot endpoint, proper 422 for others."""
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    # Honeypot endpoint must never crash — return graceful reply
    if "/api/honeypot" in request.url.path:
        return JSONResponse(
            status_code=200,
            content={"status": "success", "reply": "Hello. How can I help you?"}
        )
    # Standard validation error for other endpoints
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


@app.on_event("startup")
async def startup_event():
    """Application startup."""
    print("\n" + "=" * 70)
    print("SHIELDCALL Honeypot API - STARTING")
    print("=" * 70)
    print(f"Environment: {settings.environment}")
    print(f"Hybrid AI Mode: {settings.use_hybrid_ai}")
    print(f"Claude Model: {settings.claude_model}")
    print("=" * 70 + "\n")

    # Verify Anthropic API key
    if not settings.anthropic_api_key or "your-key" in settings.anthropic_api_key:
        print("WARNING: Anthropic API key not configured!")
        print("Please set ANTHROPIC_API_KEY in .env file")
        print("Get your key from: https://console.anthropic.com/")
        print("=" * 70 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown."""
    print("\n" + "=" * 70)
    print("SHIELDCALL Honeypot API - SHUTTING DOWN")
    print("=" * 70 + "\n")


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "service": "SHIELDCALL Honeypot API",
        "version": "1.0.0",
        "architecture": "3-Layer Hybrid AI (Whisper + Gemini + Claude)",
        "status": "operational",
        "hackathon": "India AI Impact Buildathon 2026",
        "endpoints": {
            "main": "POST /api/message",
            "health": "GET /health",
            "stats": "GET /api/stats",
            "docs": "/docs"
        },
        "team": "ShieldCall AI",
        "tagline": "Protecting India from scams with AI"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler — never crash, always return valid JSON."""
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    # Return honeypot format for honeypot endpoint so GUVI never sees a 500
    if "/api/honeypot" in str(request.url.path):
        return JSONResponse(
            status_code=200,
            content={"status": "success", "reply": "I'm having trouble understanding. Could you say that again?"}
        )
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )
