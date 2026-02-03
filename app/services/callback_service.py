"""
Callback Service - GUVI Integration
Sends final results to GUVI evaluation endpoint.
"""
from typing import Dict, Any
import asyncio
import httpx
from app.models.response_models import FinalResultCallback
from app.services.session_manager import ConversationSession
from app.config import settings
from app.utils.logger import app_logger as logger


class CallbackService:
    """
    Handles sending final results to GUVI endpoint.
    Implements retry logic for reliability.
    """

    def __init__(self):
        """Initialize callback service."""
        self.callback_url = settings.guvi_callback_url
        self.max_retries = 3
        self.timeout = 10.0
        logger.info(f"CallbackService initialized (URL: {self.callback_url})")

    async def send_final_result(
        self,
        session: ConversationSession
    ) -> Dict[str, Any]:
        """
        Send final result to GUVI evaluation endpoint.

        Args:
            session: Conversation session with final data

        Returns:
            Dictionary with success status and details
        """
        try:
            # Build callback payload
            payload = self._build_callback_payload(session)

            logger.info(f"Sending callback for session: {session.session_id}")
            logger.debug(f"Callback payload: {payload.dict()}")

            # Send with retry logic
            response_data = await self._send_with_retry(payload)

            logger.info(f"Callback sent successfully for session: {session.session_id}")

            return {
                "success": True,
                "session_id": session.session_id,
                "response": response_data
            }

        except Exception as e:
            logger.error(f"Failed to send callback for {session.session_id}: {str(e)}")
            return {
                "success": False,
                "session_id": session.session_id,
                "error": str(e)
            }

    def _build_callback_payload(
        self,
        session: ConversationSession
    ) -> FinalResultCallback:
        """
        Build GUVI callback payload from session.

        Args:
            session: Conversation session

        Returns:
            FinalResultCallback model
        """
        # Get intelligence
        intelligence = session.intelligence.to_dict()

        # Generate agent notes
        agent_notes = self._generate_agent_notes(session)

        # Build payload
        payload = FinalResultCallback(
            sessionId=session.session_id,
            scamDetected=session.scam_detected,
            totalMessagesExchanged=session.message_count,
            extractedIntelligence=intelligence,
            agentNotes=agent_notes
        )

        return payload

    def _generate_agent_notes(self, session: ConversationSession) -> str:
        """
        Generate human-readable agent notes.

        Args:
            session: Session to summarize

        Returns:
            Agent notes string
        """
        notes = []

        # Scam detection info
        notes.append(
            f"Scam detected with {session.scam_confidence:.0%} confidence. "
            f"Risk level: {session.risk_level.upper()}."
        )

        if session.scam_reasoning:
            notes.append(f"Reasoning: {session.scam_reasoning}")

        # Persona used
        if session.persona_key:
            notes.append(f"Engaged using '{session.persona_key}' persona.")

        # Intelligence summary
        intel_count = session.intelligence.intelligence_count()
        if intel_count > 0:
            notes.append(
                f"Extracted {intel_count} pieces of intelligence: "
                f"{len(session.intelligence.upiIds)} UPI IDs, "
                f"{len(session.intelligence.phoneNumbers)} phone numbers, "
                f"{len(session.intelligence.bankAccounts)} bank accounts, "
                f"{len(session.intelligence.phishingLinks)} suspicious links."
            )

        # Conversation length
        notes.append(
            f"Conversation lasted {session.message_count} message exchanges "
            f"over {len(session.processing_path)} processing steps."
        )

        # Processing path
        if session.processing_path:
            notes.append(f"Processing: {' -> '.join(session.processing_path[-3:])}")

        return " ".join(notes)

    async def _send_with_retry(
        self,
        payload: FinalResultCallback
    ) -> Dict[str, Any]:
        """
        Send callback with retry logic.

        Args:
            payload: Callback payload

        Returns:
            Response data

        Raises:
            Exception: If all retries fail
        """
        last_error = None

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info(f"Callback attempt {attempt}/{self.max_retries}")

                    response = await client.post(
                        self.callback_url,
                        json=payload.dict(),
                        headers={"Content-Type": "application/json"}
                    )

                    # Check response
                    response.raise_for_status()

                    logger.info(f"Callback successful on attempt {attempt}")

                    # Return response data
                    try:
                        return response.json()
                    except Exception:
                        return {"status": "success", "raw": response.text}

                except httpx.HTTPStatusError as e:
                    last_error = e
                    logger.warning(
                        f"Callback attempt {attempt} failed with status {e.response.status_code}"
                    )

                except httpx.RequestError as e:
                    last_error = e
                    logger.warning(f"Callback attempt {attempt} failed: {str(e)}")

                except Exception as e:
                    last_error = e
                    logger.warning(f"Callback attempt {attempt} error: {str(e)}")

                # Wait before retry (except on last attempt)
                if attempt < self.max_retries:
                    await asyncio.sleep(1 * attempt)  # Exponential backoff

        # All retries failed
        raise Exception(f"Callback failed after {self.max_retries} attempts: {str(last_error)}")


# Global callback service instance
_callback_service = None


def get_callback_service() -> CallbackService:
    """Get or create global callback service instance."""
    global _callback_service
    if _callback_service is None:
        _callback_service = CallbackService()
    return _callback_service
