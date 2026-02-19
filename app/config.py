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
    claude_model: str = Field(default="claude-3-5-haiku-20241022", env="CLAUDE_MODEL")

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
    # Phone: handles +91, 91, (91), leading 0, any digit grouping with spaces/dots/dashes
    "phone_number": r"(?<!\d)(?:(?:\+91|91|\(91\)|0)[\s.\-]*)?[6-9](?:[\s.\-]?\d){9}(?!\d)",
    # Bank: plain 9-18 digit numbers (primary)
    "bank_account": r"\b\d{9,18}\b",
    # Bank: numbers with dashes/spaces like 1234-5678-9012-3456
    "bank_account_formatted": r"\b\d{4}[\s\-]\d{4}[\s\-]\d{4}(?:[\s\-]\d{4})?\b",
    # Bank: prefixed like "a/c no: 50100123456789" or "account: 1234567890"
    "bank_account_prefixed": r"(?:a/c\s*(?:no\.?|number)?|account\s*(?:no\.?|number)?)\s*:?\s*(\d{9,18})",
    "url": r"https?://[^\s]+",
    "url_www": r"\bwww\.[^\s]+",
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    # IFSC code pattern (to exclude from bank accounts)
    "ifsc": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
    # Case/Reference IDs
    "case_id": r"(?:case\s*(?:number|no\.?|id)|reference\s*(?:number|no\.?|:)|ref\b\s*(?:no\.?|id)?|complaint\s*(?:number|no\.?)|ticket\s*(?:number|no\.?))\s*:?\s*([A-Za-z0-9][\w\-]{3,30})",
    # Policy numbers
    "policy_number": r"(?:policy\s*(?:number|no\.?|id))\s*:?\s*([A-Za-z0-9][\w\-]{3,30})",
    # Order numbers
    "order_number": r"(?:order\s*(?:number|no\.?|id|#))\s*:?\s*([A-Za-z0-9][\w\-]{3,30})",
}

# Scam type classification keywords
SCAM_TYPE_KEYWORDS = {
    "bank_fraud": ["bank", "account compromised", "sbi", "hdfc", "icici", "axis", "account block", "account frozen", "unauthorized transaction"],
    "upi_fraud": ["upi", "cashback", "paytm", "gpay", "google pay", "phonepe", "bhim"],
    "phishing": ["click", "link", "deal", "offer price", "flash sale", "iphone", "flipkart", "amazon offer"],
    "kyc_fraud": ["kyc", "aadhaar", "pan card", "wallet block", "paytm kyc", "mobikwik"],
    "job_scam": ["job", "work from home", "hiring", "vacancy", "salary", "recruitment", "registration fee"],
    "lottery_scam": ["lottery", "lucky draw", "won", "prize", "winner", "jackpot", "lakh"],
    "electricity_bill": ["electricity", "bill overdue", "disconnection", "bijli", "bses", "mseb", "power cut"],
    "govt_scheme": ["government", "yojana", "subsidy", "pm kisan", "scheme", "eligible", "benefit"],
    "crypto_investment": ["bitcoin", "crypto", "investment", "trading", "returns guaranteed", "forex"],
    "customs_parcel": ["customs", "parcel", "duty", "courier", "package", "held at"],
    "tech_support": ["microsoft", "virus", "malware", "tech support", "computer", "antivirus", "security patch"],
    "loan_approval": ["loan", "pre-approved", "emi", "interest rate", "cibil", "personal loan", "credit"],
    "income_tax": ["income tax", "tax refund", "itr", "tax department", "refund pending", "form 16"],
    "refund_scam": ["refund", "failed transaction", "order cancel", "return", "cashback failed"],
    "insurance": ["insurance", "lic", "policy maturity", "claim", "premium", "nomination", "endowment"],
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
