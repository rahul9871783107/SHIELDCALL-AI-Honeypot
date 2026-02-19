"""
Response Models - Pydantic Schemas for API Responses
Structures all API responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class AgentResponse(BaseModel):
    """Standard response from the AI agent to continue conversation."""
    status: str = Field(default="success", description="Response status")
    reply: str = Field(..., description="Agent's reply to the scammer")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "reply": "Oh no! Why is my account being blocked? What should I do?"
            }
        }


class ExtractedIntelligence(BaseModel):
    """Intelligence extracted from scammer during conversation."""
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    emailAddresses: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)
    caseIds: List[str] = Field(default_factory=list)
    policyNumbers: List[str] = Field(default_factory=list)
    orderNumbers: List[str] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to dictionary format for callback."""
        return {
            "bankAccounts": self.bankAccounts,
            "upiIds": self.upiIds,
            "phishingLinks": self.phishingLinks,
            "phoneNumbers": self.phoneNumbers,
            "emailAddresses": self.emailAddresses,
            "suspiciousKeywords": self.suspiciousKeywords,
            "caseIds": self.caseIds,
            "policyNumbers": self.policyNumbers,
            "orderNumbers": self.orderNumbers,
        }

    def has_intelligence(self) -> bool:
        """Check if any intelligence has been extracted."""
        return bool(
            self.bankAccounts or
            self.upiIds or
            self.phishingLinks or
            self.phoneNumbers or
            self.emailAddresses or
            self.caseIds or
            self.policyNumbers or
            self.orderNumbers
        )

    def intelligence_count(self) -> int:
        """Count total pieces of intelligence."""
        return (
            len(self.bankAccounts) +
            len(self.upiIds) +
            len(self.phishingLinks) +
            len(self.phoneNumbers) +
            len(self.emailAddresses) +
            len(self.caseIds) +
            len(self.policyNumbers) +
            len(self.orderNumbers)
        )


class FinalResultCallback(BaseModel):
    """
    Final result payload to be sent to GUVI evaluation endpoint.
    This is mandatory for evaluation.
    """
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: Dict[str, List[str]]
    agentNotes: str

    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "abc123-session-id",
                "scamDetected": True,
                "totalMessagesExchanged": 18,
                "extractedIntelligence": {
                    "bankAccounts": ["XXXX-XXXX-XXXX"],
                    "upiIds": ["scammer@upi"],
                    "phishingLinks": ["http://malicious-link.example"],
                    "phoneNumbers": ["+91XXXXXXXXXX"],
                    "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
                },
                "agentNotes": "Scammer used urgency tactics and payment redirection"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    status: str = "error"
    message: str
    details: Optional[Dict[str, Any]] = None
