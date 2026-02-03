"""
Logging Configuration - Structured Logging with Loguru
Provides colorized, structured logging for the entire application.
"""
import sys
from loguru import logger
from app.config import settings


def setup_logger():
    """Configure the application logger with loguru."""
    # Remove default handler
    logger.remove()

    # Custom format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Console logging (always enabled)
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
    )

    # File logging (only in production)
    if settings.environment == "production":
        logger.add(
            "logs/shieldcall_{time:YYYY-MM-DD}.log",
            format=log_format,
            level="INFO",
            rotation="1 day",
            retention="7 days",
            compression="zip",
        )

    logger.info("=" * 70)
    logger.info("SHIELDCALL Logger Initialized")
    logger.info(f"Log Level: {settings.log_level}")
    logger.info(f"Environment: {settings.environment}")
    logger.info("=" * 70)

    return logger


# Initialize logger globally
app_logger = setup_logger()
