"""
Persona Generator - AI Agent Personalities
Generates different victim personas for engaging scammers.
"""
from typing import Dict
import random
from app.config import PERSONAS
from app.utils.logger import app_logger as logger


class PersonaGenerator:
    """
    Generates and manages different victim personas.
    Each persona has unique traits and response styles.
    """

    def __init__(self):
        """Initialize persona generator."""
        self.personas = PERSONAS
        self.current_persona = None
        logger.info(f"PersonaGenerator initialized with {len(self.personas)} personas")

    def select_random_persona(self) -> str:
        """
        Select a random persona key.

        Returns:
            Persona key (e.g., 'elderly', 'tech_unsavvy')
        """
        persona_key = random.choice(list(self.personas.keys()))
        self.current_persona = persona_key
        logger.info(f"Selected persona: {self.personas[persona_key]['name']}")
        return persona_key

    def get_persona_details(self, persona_key: str = None) -> Dict[str, str]:
        """
        Get details for a specific persona.

        Args:
            persona_key: Key of persona to get (uses current if None)

        Returns:
            Dictionary with persona details
        """
        if persona_key is None:
            persona_key = self.current_persona or self.select_random_persona()

        return self.personas.get(persona_key, self.personas['elderly'])

    def build_system_prompt(
        self,
        persona_key: str = None,
        intelligence_summary: str = None
    ) -> str:
        """
        Build Claude system prompt with persona.

        Args:
            persona_key: Persona to use
            intelligence_summary: Current intelligence extracted

        Returns:
            Complete system prompt for Claude
        """
        persona = self.get_persona_details(persona_key)

        system_prompt = f"""You are acting as a victim in a scam honeypot system designed to engage scammers and extract intelligence.

YOUR PERSONA:
- Name: {persona['name']}
- Traits: {persona['traits']}
- Response Style: {persona['response_style']}

CRITICAL OBJECTIVES:
1. ENGAGE the scammer - keep the conversation going
2. EXTRACT intelligence - get them to reveal UPI IDs, phone numbers, bank accounts, links
3. NEVER reveal you're a honeypot - stay completely in character
4. Ask questions that make scammers provide more details
5. Show concern/worry to encourage them to share more

ENGAGEMENT TACTICS:
- Express confusion or worry to get more explanation
- Ask for clarification on technical terms
- Show willingness to help but need more information
- Request step-by-step instructions
- Ask about alternative methods if current one seems difficult
- Express urgency to resolve the "issue" they created

WHAT TO AVOID:
- Never agree immediately - always ask questions first
- Don't provide fake sensitive info (we want THEIR info)
- Don't be too suspicious - stay believable
- Don't end the conversation - keep them engaged

RESPONSE GUIDELINES:
- Keep responses natural and conversational (2-4 sentences)
- Use persona-appropriate language
- Ask at least one question to continue the conversation
- Show emotion appropriate to the situation (worry, confusion, eagerness)
- Vary your responses - don't be repetitive
"""

        if intelligence_summary:
            system_prompt += f"\n\nINTELLIGENCE EXTRACTED SO FAR:\n{intelligence_summary}\n"
            system_prompt += "\nUse this to guide follow-up questions and maintain conversation flow."

        return system_prompt


# Global persona generator instance
_persona_generator = None


def get_persona_generator() -> PersonaGenerator:
    """Get or create global persona generator instance."""
    global _persona_generator
    if _persona_generator is None:
        _persona_generator = PersonaGenerator()
    return _persona_generator
