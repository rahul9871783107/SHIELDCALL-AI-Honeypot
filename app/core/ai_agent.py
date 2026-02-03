"""
AI Agent - Claude Sonnet 4 Integration
Layer 3: Deep analysis and natural conversation generation.
"""
from typing import List, Optional
from anthropic import Anthropic
from app.config import settings
from app.core.persona_generator import get_persona_generator
from app.models.request_models import Message
from app.utils.logger import app_logger as logger
import random


class AIAgent:
    """
    Claude-powered AI agent for scam engagement.

    Features:
    - Natural conversation generation
    - Multiple personas
    - Context-aware responses
    - Intelligence-focused prompting
    """

    def __init__(self):
        """Initialize Claude AI agent."""
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.persona_generator = get_persona_generator()
        self.current_persona = None
        self.conversation_initialized = False

        logger.info(f"AIAgent initialized with model: {settings.claude_model}")

    def initialize_conversation(self, persona_key: str = None) -> str:
        """
        Initialize conversation with a persona.

        Args:
            persona_key: Specific persona to use (random if None)

        Returns:
            Selected persona key
        """
        if persona_key is None:
            self.current_persona = self.persona_generator.select_random_persona()
        else:
            self.current_persona = persona_key

        self.conversation_initialized = True
        logger.info(f"Conversation initialized with persona: {self.current_persona}")
        return self.current_persona

    def generate_response(
        self,
        current_message: str,
        conversation_history: List[Message] = None,
        intelligence_summary: str = None
    ) -> str:
        """
        Generate AI response using Claude.

        Args:
            current_message: Latest message from scammer
            conversation_history: Previous messages
            intelligence_summary: Current intelligence extracted

        Returns:
            AI-generated response
        """
        # Initialize persona if not done
        if not self.conversation_initialized:
            self.initialize_conversation()

        try:
            # Build system prompt
            system_prompt = self.persona_generator.build_system_prompt(
                self.current_persona,
                intelligence_summary
            )

            # Build message history for Claude
            messages = []

            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    # Handle both Message objects and raw dicts
                    if isinstance(msg, dict):
                        sender = msg.get("sender", "scammer")
                        text = msg.get("text", msg.get("content", ""))
                    else:
                        sender = msg.sender
                        text = msg.text
                    role = "assistant" if sender == "user" else "user"
                    messages.append({
                        "role": role,
                        "content": text
                    })

            # Add current message
            messages.append({
                "role": "user",
                "content": current_message
            })

            logger.info(f"Generating Claude response (messages: {len(messages)})...")

            # Call Claude API
            response = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
                system=system_prompt,
                messages=messages
            )

            # Extract response text
            reply = response.content[0].text

            logger.info(f"Claude response generated: {reply[:80]}...")

            return reply

        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            # Fallback response
            return self._get_fallback_response()

    def _get_fallback_response(self) -> str:
        """
        Get fallback response if Claude fails.

        Returns:
            Safe fallback response
        """
        fallback_responses = [
            "I'm not sure I understand. Can you explain more?",
            "This is concerning. What should I do next?",
            "I want to help but I'm confused. Can you clarify?",
            "Please tell me exactly what I need to do.",
        ]
        return random.choice(fallback_responses)


# Global AI agent instance
_ai_agent = None


def get_ai_agent() -> AIAgent:
    """Get or create global AI agent instance."""
    global _ai_agent
    if _ai_agent is None:
        _ai_agent = AIAgent()
    return _ai_agent
