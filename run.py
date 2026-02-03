#!/usr/bin/env python3
"""
SHIELDCALL Honeypot API - Application Runner
India AI Impact Buildathon 2026
"""
import uvicorn
from app.config import settings


if __name__ == "__main__":
    print("=" * 70)
    print("SHIELDCALL - AI-Powered Scam Detection Honeypot")
    print("=" * 70)
    print(f"Host: {settings.host}")
    print(f"Port: {settings.port}")
    print(f"Environment: {settings.environment}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Hybrid AI: {settings.use_hybrid_ai}")
    print("=" * 70)
    print(f"\nAPI Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"Health Check: http://{settings.host}:{settings.port}/health")
    print(f"Root: http://{settings.host}:{settings.port}/")
    print("\nPress CTRL+C to stop the server\n")
    print("=" * 70)

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
