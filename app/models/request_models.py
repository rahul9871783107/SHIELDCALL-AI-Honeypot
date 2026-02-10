"""
Request Models - Pydantic Schemas for Incoming Requests
Validates all incoming API requests.
Flexible enough to accept both GUVI's test format and our full format.
"""
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Union, Any
from datetime import datetime, timezone
import uuid


class Message(BaseModel):
    """Individual message in a conversation."""
    sender: str = Field(default="scammer", description="Message sender")
    text: str = Field(..., description="Message text content")
    timestamp: Union[str, int, float] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp - accepts ISO-8601 string or epoch int"
    )


class Metadata(BaseModel):
    """Optional metadata about the conversation context."""
    channel: Optional[str] = Field(default="SMS", description="Communication channel")
    language: Optional[str] = Field(default="English", description="Language used")
    locale: Optional[str] = Field(default="IN", description="Country or region")

    class Config:
        extra = "allow"


class IncomingMessageRequest(BaseModel):
    """
    Main request model for incoming scam messages.
    Accepts both GUVI's simple format and full structured format.

    GUVI simple:  {"sessionId": "x", "message": "text here"}
    Full format:  {"sessionId": "x", "message": {"sender": "scammer", "text": "...", "timestamp": "..."}}
    """
    sessionId: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Latest incoming message")
    conversationHistory: List[Message] = Field(
        default_factory=list,
        description="All previous messages in the conversation"
    )
    metadata: Optional[Metadata] = Field(
        default=None,
        description="Optional context about the conversation"
    )

    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "sessionId": "test-session-123",
                "message": "Your bank account will be blocked today. Verify immediately."
            }
        }

    @model_validator(mode="before")
    @classmethod
    def normalize_request(cls, data: Any) -> Any:
        """Normalize various input formats into our internal structure."""
        if not isinstance(data, dict):
            return data

        # Accept session_id as alias for sessionId
        if "session_id" in data and "sessionId" not in data:
            data["sessionId"] = data.pop("session_id")

        # Accept conversation_history as alias for conversationHistory
        if "conversation_history" in data and "conversationHistory" not in data:
            data["conversationHistory"] = data.pop("conversation_history")

        # Normalize message: string -> Message object
        msg = data.get("message")
        if isinstance(msg, str):
            data["message"] = {
                "sender": "scammer",
                "text": msg,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        elif isinstance(msg, dict):
            # Fill in missing fields with defaults
            msg.setdefault("sender", "scammer")
            msg.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
            # Accept 'content' as alias for 'text'
            if "text" not in msg and "content" in msg:
                msg["text"] = msg.pop("content")
            # Accept 'body' as alias for 'text'
            if "text" not in msg and "body" in msg:
                msg["text"] = msg.pop("body")

        # Normalize conversationHistory entries
        history = data.get("conversationHistory", [])
        if isinstance(history, list):
            normalized = []
            for item in history:
                if isinstance(item, str):
                    normalized.append({
                        "sender": "scammer",
                        "text": item,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
                elif isinstance(item, dict):
                    item.setdefault("sender", "scammer")
                    item.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
                    if "text" not in item and "content" in item:
                        item["text"] = item.pop("content")
                    if "text" not in item and "body" in item:
                        item["text"] = item.pop("body")
                    normalized.append(item)
                else:
                    normalized.append(item)
            data["conversationHistory"] = normalized

        return data


class HackathonResponse(BaseModel):
    """Hackathon API response format - ONLY these two fields."""
    status: str = "success"
    reply: str


class HackathonRequest(BaseModel):
    """
    GUVI hackathon request format - flexible input.
    Accepts both string and object message formats.
    """
    sessionId: Optional[str] = Field(default=None, description="Unique session identifier")
    message: Any = Field(default=None, description="Message text or object")
    conversationHistory: Optional[List[Any]] = Field(
        default_factory=list,
        description="Previous conversation messages"
    )
    metadata: Optional[dict] = Field(
        default_factory=dict,
        description="Optional metadata"
    )

    class Config:
        extra = "allow"

    @model_validator(mode="before")
    @classmethod
    def normalize_hackathon_input(cls, data: Any) -> Any:
        """Accept snake_case aliases, normalize input, auto-generate missing fields."""
        if not isinstance(data, dict):
            return data
        # Accept session_id as alias for sessionId
        if "session_id" in data and "sessionId" not in data:
            data["sessionId"] = data.pop("session_id")
        # Accept conversation_history as alias
        if "conversation_history" in data and "conversationHistory" not in data:
            data["conversationHistory"] = data.pop("conversation_history")
        # Auto-generate sessionId if missing or empty
        if not data.get("sessionId"):
            data["sessionId"] = f"auto-{uuid.uuid4().hex[:12]}"
        # Ensure conversationHistory is a list
        ch = data.get("conversationHistory")
        if ch is not None and not isinstance(ch, list):
            data["conversationHistory"] = []
        return data

    def get_message_text(self) -> str:
        """Extract message text from string or object format."""
        msg = self.message
        if isinstance(msg, str):
            return msg
        if isinstance(msg, dict):
            return msg.get("text", msg.get("content", msg.get("body", "")))
        return str(msg) if msg else ""
