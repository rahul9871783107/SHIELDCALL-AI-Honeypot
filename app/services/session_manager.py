"""
Session Manager - Conversation Session Management
Manages conversation sessions, tracking, and lifecycle.
"""
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from app.models.request_models import Message
from app.models.response_models import ExtractedIntelligence
from app.core.intelligence_extractor import IntelligenceExtractor
from app.config import settings
from app.utils.logger import app_logger as logger


@dataclass
class ConversationSession:
    """
    Represents a single conversation session with a scammer.
    Tracks all conversation state and intelligence.
    """
    session_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Conversation tracking
    message_count: int = 0
    messages: List[dict] = field(default_factory=list)

    # Scam detection
    scam_detected: bool = False
    scam_confidence: float = 0.0
    risk_level: str = "unknown"
    scam_reasoning: str = ""

    # Intelligence extraction
    intelligence_extractor: IntelligenceExtractor = field(default_factory=IntelligenceExtractor)

    # AI Agent
    persona_key: Optional[str] = None

    # Processing metadata
    processing_path: List[str] = field(default_factory=list)

    # Callback tracking
    callback_sent: bool = False
    callback_timestamp: Optional[datetime] = None
    callback_intel_count: int = 0

    def add_message(self, message: Message):
        """Add a message to the session."""
        self.messages.append(message.dict())
        self.message_count = len(self.messages)
        self.updated_at = datetime.utcnow()

    def is_expired(self) -> bool:
        """Check if session has expired."""
        timeout = timedelta(minutes=settings.session_timeout_minutes)
        return datetime.utcnow() - self.updated_at > timeout

    @property
    def intelligence(self) -> ExtractedIntelligence:
        """Get current intelligence."""
        return self.intelligence_extractor.intelligence


class SessionManager:
    """
    Manages all conversation sessions.
    Handles creation, retrieval, updates, and cleanup.
    """

    def __init__(self):
        """Initialize session manager."""
        self.sessions: Dict[str, ConversationSession] = {}
        logger.info("SessionManager initialized")

    def get_or_create_session(self, session_id: str) -> ConversationSession:
        """
        Get existing session or create new one.

        Args:
            session_id: Unique session identifier

        Returns:
            ConversationSession instance
        """
        if session_id not in self.sessions:
            session = ConversationSession(session_id=session_id)
            self.sessions[session_id] = session
            logger.info(f"Created new session: {session_id}")
        else:
            session = self.sessions[session_id]
            logger.debug(f"Retrieved existing session: {session_id}")

        return session

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        Get session by ID.

        Args:
            session_id: Session ID to retrieve

        Returns:
            ConversationSession or None if not found
        """
        return self.sessions.get(session_id)

    def update_session_intelligence(
        self,
        session_id: str,
        new_intelligence: ExtractedIntelligence
    ):
        """
        Update session with new intelligence.

        Args:
            session_id: Session to update
            new_intelligence: New intelligence extracted
        """
        session = self.get_session(session_id)
        if session:
            session.updated_at = datetime.utcnow()
            logger.debug(f"Updated intelligence for session: {session_id}")

    def mark_scam_detected(
        self,
        session_id: str,
        confidence: float,
        reasoning: str = ""
    ):
        """
        Mark session as scam detected.

        Args:
            session_id: Session ID
            confidence: Detection confidence
            reasoning: Explanation
        """
        session = self.get_session(session_id)
        if session:
            session.scam_detected = True
            session.scam_confidence = confidence
            session.scam_reasoning = reasoning
            session.updated_at = datetime.utcnow()
            logger.warning(f"Scam detected in session {session_id} (confidence: {confidence:.2f})")

    def mark_callback_sent(self, session_id: str):
        """
        Mark that callback has been sent for this session.
        Records intel count so we know when to re-send with better data.
        """
        session = self.get_session(session_id)
        if session:
            session.callback_sent = True
            session.callback_timestamp = datetime.utcnow()
            session.callback_intel_count = session.intelligence.intelligence_count()
            logger.info(
                f"Callback sent for {session_id} "
                f"(intel_count={session.callback_intel_count}, "
                f"turns={session.message_count})"
            )

    def should_send_callback(self, session_id: str) -> bool:
        """
        Determine if we should send final callback for this session.

        Criteria:
        1. Scam has been detected
        2. Either first send or we have NEW intelligence since last send
        3. Minimum 5 turns before first callback (prevents premature firing)
        4. Either:
           - Intelligence count >= MIN_INTELLIGENCE_FOR_CALLBACK
           - OR conversation turns >= AUTO_CALLBACK_AFTER_TURNS
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # Must be detected as scam
        if not session.scam_detected:
            return False

        intelligence_count = session.intelligence.intelligence_count()

        # If callback already sent, only re-send if we have MORE intelligence
        if session.callback_sent:
            if intelligence_count <= session.callback_intel_count:
                return False
            logger.info(
                f"Re-sending callback for {session_id}: "
                f"intel {session.callback_intel_count} -> {intelligence_count}"
            )
            return True

        # First callback: require minimum turns to avoid premature firing
        MIN_TURNS_FOR_FIRST_CALLBACK = 5
        if session.message_count < MIN_TURNS_FOR_FIRST_CALLBACK:
            return False

        has_enough_intel = intelligence_count >= settings.min_intelligence_for_callback
        enough_turns = session.message_count >= settings.auto_callback_after_turns

        should_send = has_enough_intel or enough_turns

        if should_send:
            logger.info(
                f"Callback criteria met for {session_id}: "
                f"intel={intelligence_count}, turns={session.message_count}"
            )

        return should_send

    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions from memory.

        Returns:
            Number of sessions removed
        """
        expired_ids = [
            sid for sid, session in self.sessions.items()
            if session.is_expired()
        ]

        for sid in expired_ids:
            del self.sessions[sid]

        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired sessions")

        return len(expired_ids)

    def get_session_count(self) -> int:
        """Get total number of active sessions."""
        return len(self.sessions)

    def get_all_sessions(self) -> List[ConversationSession]:
        """Get all sessions."""
        return list(self.sessions.values())


# Global session manager instance
_session_manager = None


def get_session_manager() -> SessionManager:
    """Get or create global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
