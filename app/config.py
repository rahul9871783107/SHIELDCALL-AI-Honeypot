"""
Configuration Management - SHIELDCALL
Loads all settings from environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_key: str = Field(default="hackathon-secret-key-2026", env="API_KEY")
    port: int = Field(default=8000, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")

    # AI API Keys - Hybrid Architecture
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")

    # GUVI Configuration
    guvi_callback_url: str = Field(
        default="https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
        env="GUVI_CALLBACK_URL"
    )

    # Application Settings
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    environment: str = Field(default="production", env="ENVIRONMENT")

    # Scam Detection Settings
    scam_confidence_threshold: float = Field(default=0.65, env="SCAM_CONFIDENCE_THRESHOLD")
    max_conversation_turns: int = Field(default=25, env="MAX_CONVERSATION_TURNS")
    session_timeout_minutes: int = Field(default=30, env="SESSION_TIMEOUT_MINUTES")

    # AI Settings
    ai_model: str = Field(default="claude-sonnet-4-20250514", env="AI_MODEL")
    ai_max_tokens: int = Field(default=200, env="AI_MAX_TOKENS")
    ai_temperature: float = Field(default=0.6, env="AI_TEMPERATURE")

    # Hybrid AI Settings
    use_hybrid_ai: bool = Field(default=True, env="USE_HYBRID_AI")
    whisper_model: str = Field(default="whisper-1", env="WHISPER_MODEL")
    gemini_model: str = Field(default="gemini-2.0-flash", env="GEMINI_MODEL")
    gemini_max_tokens: int = Field(default=500, env="GEMINI_MAX_TOKENS")
    gemini_temperature: float = Field(default=0.3, env="GEMINI_TEMPERATURE")
    claude_model: str = Field(default="claude-sonnet-4-20250514", env="CLAUDE_MODEL")

    # Intelligence Extraction
    auto_callback_after_turns: int = Field(default=15, env="AUTO_CALLBACK_AFTER_TURNS")
    min_intelligence_for_callback: int = Field(default=1, env="MIN_INTELLIGENCE_FOR_CALLBACK")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Scam Keywords (for detection)
SCAM_KEYWORDS = {
    "urgency": ["urgent", "immediately", "now", "hurry", "quick", "asap", "today"],
    "threats": ["block", "suspend", "freeze", "locked", "deactivate", "closed", "expire"],
    "financial": ["bank", "account", "upi", "payment", "transaction", "refund", "money"],
    "verification": ["verify", "confirm", "validate", "authenticate", "update", "kyc", "otp"],
    "action_required": ["click", "call", "share", "send", "provide", "submit"],
    "rewards": ["won", "prize", "reward", "cashback", "lucky", "winner"],
}

# Regex patterns for intelligence extraction
INTELLIGENCE_PATTERNS = {
    "upi_id": r"[\w.-]+@[a-zA-Z][\w.-]*",
    "phone_number": r"(?:\+91[\s\-]*)?\b[6-9]\d{2,3}[\s\-]?\d{2,3}[\s\-]?\d{4,5}\b",
    "bank_account": r"\b\d{9,18}\b",
    "url": r"https?://[^\s]+",
    "url_www": r"\bwww\.[^\s]+",
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
}

# AI Agent Personas
PERSONAS = {
    "elderly": {
        "name": "Concerned Senior Citizen",
        "traits": "elderly person, cautious, asks many questions",
        "response_style": "polite, concerned, slightly confused",
    },
    "tech_unsavvy": {
        "name": "Tech-Unsavvy User",
        "traits": "unfamiliar with technology",
        "response_style": "simple language, asks basic questions",
    },
    "worried_customer": {
        "name": "Worried Bank Customer",
        "traits": "anxious about account",
        "response_style": "cooperative but cautious",
    },
}
