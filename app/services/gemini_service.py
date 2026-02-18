"""
Gemini Service - Primary Engagement + Risk Screening
Uses Google Gemini 2.0 Flash for ultra-fast persona engagement.
"""
from typing import Dict, List, Literal
import google.generativeai as genai
from app.config import settings
from app.utils.logger import app_logger as logger
import json
import re

RiskLevel = Literal["low", "medium", "high"]

# Max messages from history to send to Gemini
MAX_HISTORY_MESSAGES = 6

# Refusal phrases to detect broken character
REFUSAL_PHRASES = [
    "i can't roleplay", "i cannot roleplay",
    "can't participate", "cannot participate",
    "i'm an ai", "i am an ai", "as an ai",
    "i'm a language model", "i am a language model",
    "appears to be a scam", "this is a scam",
    "i need to warn you", "i must warn you",
    "not comfortable", "i cannot assist",
    "i can't assist", "i will not",
    "i cannot engage", "i can't engage",
    "potential scam", "scam attempt",
    "i recommend contacting", "contact the authorities",
    "i do not engage", "i do not feel",
    "i do not actually", "i cannot and will not",
    "please be cautious", "be careful with",
    "this looks like a fraud", "fraudulent activity",
]


class GeminiService:
    """
    Gemini Flash for primary persona engagement + risk screening.

    Features:
    - Ultra-fast persona engagement (<2s)
    - Fallback risk screening
    - No refusals on scam roleplay
    """

    def __init__(self):
        """Initialize Gemini service."""
        if settings.google_api_key and settings.google_api_key != "your-google-key-here":
            try:
                genai.configure(api_key=settings.google_api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
                self.enabled = True
                logger.info("GeminiService initialized with model: gemini-2.0-flash")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {str(e)}")
                self.model = None
                self.enabled = False
        else:
            self.model = None
            self.enabled = False
            logger.warning("Google API key not set. Gemini service disabled.")

    def generate_persona_response(
        self,
        current_message: str,
        conversation_history: List = None,
        persona_prompt: str = "",
    ) -> str:
        """
        Generate an in-character persona response using Gemini 2.0 Flash.

        Args:
            current_message: The scammer's latest message
            conversation_history: Previous messages in the conversation
            persona_prompt: Full system prompt with persona instructions

        Returns:
            In-character response string, or None if Gemini fails/refuses
        """
        if not self.enabled:
            logger.warning("Gemini not enabled, skipping persona engagement")
            return None

        try:
            # Build conversation contents for Gemini
            contents = self._build_engagement_contents(
                current_message, conversation_history, persona_prompt
            )

            response = self.model.generate_content(
                contents=contents,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=200,
                    temperature=0.7,
                ),
            )

            reply = response.text.strip()

            # Check for refusal
            reply_lower = reply.lower()
            if any(phrase in reply_lower for phrase in REFUSAL_PHRASES):
                logger.warning(f"Gemini refusal detected: {reply[:80]}...")
                return None

            # Strip any meta-commentary
            reply = re.sub(r'\s*\[.*?(?:NOTE|note|Note).*?\]', '', reply, flags=re.DOTALL).strip()
            reply = re.sub(r'\s*\((?:Note|NOTE|As an AI|Disclaimer).*?\)', '', reply, flags=re.DOTALL).strip()

            if not reply or len(reply) < 10:
                logger.warning("Gemini response too short or empty")
                return None

            logger.info(f"Gemini persona response: {reply[:80]}...")
            return reply

        except Exception as e:
            logger.error(f"Gemini engagement error: {str(e)}")
            return None

    def _build_engagement_contents(
        self,
        current_message: str,
        conversation_history: List = None,
        persona_prompt: str = "",
    ) -> list:
        """Build Gemini conversation contents with persona + history."""
        contents = []

        # First message: persona prompt + first scammer message
        # Gemini doesn't have a separate system prompt, so we prepend it
        history_messages = []
        if conversation_history:
            recent = conversation_history
            if len(conversation_history) > MAX_HISTORY_MESSAGES:
                recent = conversation_history[-MAX_HISTORY_MESSAGES:]

            for msg in recent:
                if isinstance(msg, dict):
                    sender = msg.get("sender", "scammer")
                    text = msg.get("text", msg.get("content", ""))
                else:
                    sender = getattr(msg, "sender", "scammer")
                    text = getattr(msg, "text", "")
                if text:
                    role = "model" if sender == "user" else "user"
                    history_messages.append({"role": role, "parts": [text]})

        # Build contents: system prompt as first user message, then history, then current
        if history_messages:
            # Prepend persona to first user message in history
            first_msg = history_messages[0]
            if first_msg["role"] == "user":
                first_msg["parts"] = [persona_prompt + "\n\nSCAMMER MESSAGE:\n" + first_msg["parts"][0]]
                contents = history_messages
            else:
                # History starts with model — prepend a user message with prompt
                contents = [{"role": "user", "parts": [persona_prompt + "\n\nRespond in character."]}]
                contents.extend(history_messages)
            # Add current message
            contents.append({"role": "user", "parts": [current_message]})
        else:
            # No history — single turn with persona + current message
            contents = [
                {
                    "role": "user",
                    "parts": [persona_prompt + "\n\nSCAMMER MESSAGE:\n" + current_message],
                }
            ]

        # Ensure alternating roles (Gemini requirement)
        contents = self._fix_alternating_roles(contents)

        return contents

    def _fix_alternating_roles(self, contents: list) -> list:
        """Ensure Gemini gets alternating user/model roles."""
        if not contents:
            return contents
        fixed = [contents[0]]
        for msg in contents[1:]:
            if msg["role"] == fixed[-1]["role"]:
                # Merge with previous message of same role
                fixed[-1]["parts"].extend(msg["parts"])
            else:
                fixed.append(msg)
        # Must start with 'user'
        if fixed and fixed[0]["role"] != "user":
            fixed = fixed[1:]
        return fixed

    async def quick_screen(self, text: str, context: str = None) -> Dict[str, any]:
        """
        Perform ultra-fast risk assessment on text.

        Args:
            text: Message text to analyze
            context: Optional conversation context

        Returns:
            Dictionary with:
            - risk_level: "low", "medium", or "high"
            - confidence: Confidence score (0.0-1.0)
            - reasoning: Brief explanation
            - scam_indicators: List of detected patterns
            - should_deep_analyze: Whether to use Claude
        """
        if not self.enabled:
            logger.warning("Gemini service not enabled. Using fallback screening.")
            return self._fallback_screening(text)

        try:
            # Build screening prompt
            prompt = self._build_screening_prompt(text, context)

            logger.info("Layer 2: Gemini Flash screening...")

            # Generate response with optimized settings
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.gemini_temperature,
                    max_output_tokens=settings.gemini_max_tokens,
                )
            )

            # Parse response
            result = self._parse_risk_response(response.text)

            logger.info(
                f"Gemini screening complete: risk={result['risk_level']}, "
                f"confidence={result['confidence']:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"Gemini screening error: {str(e)}")
            # Fallback to rule-based on error
            return self._fallback_screening(text)

    def _build_screening_prompt(self, text: str, context: str = None) -> str:
        """Build prompt for Gemini screening."""
        prompt = f"""You are a QUICK scam detection system for India. Analyze this message and respond ONLY with structured assessment.

MESSAGE: "{text}"
"""

        if context:
            prompt += f"\nCONTEXT: {context}\n"

        prompt += """
TASK: Perform ULTRA-FAST initial risk screening (target <200ms)

Analyze for these SCAM INDICATORS (common in India):
1. Urgency/pressure tactics: "urgent", "immediately", "now", "today", "hurry"
2. Threats: "block", "suspend", "freeze", "close account", "locked", "deactivate"
3. Financial requests: "UPI", "bank", "payment", "money", "OTP", "CVV", "PIN"
4. Verification requests: "verify", "confirm", "validate", "authenticate", "KYC"
5. Suspicious links or shortened URLs
6. Reward/prize claims: "won", "lucky", "cashback", "prize", "congratulations"
7. Impersonation: "bank official", "government", "tax department", "police"
8. Request for personal info: "Aadhar", "PAN", "account number", "password"

RESPOND IN THIS EXACT JSON FORMAT (no markdown, no extra text):
{
  "risk_level": "low|medium|high",
  "confidence": 0.0-1.0,
  "indicators": ["list", "of", "detected", "patterns"],
  "reasoning": "one brief sentence explaining the risk level"
}

GUIDELINES:
- LOW: Normal conversation, no scam patterns detected
- MEDIUM: 1-2 suspicious indicators, needs deeper analysis
- HIGH: 3+ indicators or obvious scam patterns (urgent + financial + threat)

IMPORTANT: Response must be valid JSON only. No markdown, no code blocks, no extra text."""

        return prompt

    def _parse_risk_response(self, response_text: str) -> Dict[str, any]:
        """Parse Gemini's response into structured format."""
        try:
            # Clean response - remove markdown if present
            cleaned = response_text.strip()
            if cleaned.startswith('```'):
                # Remove markdown code blocks
                lines = cleaned.split('\n')
                cleaned = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned
                if cleaned.startswith('json'):
                    cleaned = cleaned[4:].strip()

            # Parse JSON
            parsed = json.loads(cleaned)

            # Validate and normalize
            risk_level = parsed.get('risk_level', 'medium').lower()
            if risk_level not in ['low', 'medium', 'high']:
                risk_level = 'medium'

            confidence = float(parsed.get('confidence', 0.5))
            confidence = max(0.0, min(1.0, confidence))

            indicators = parsed.get('indicators', [])
            if not isinstance(indicators, list):
                indicators = []

            reasoning = parsed.get('reasoning', 'Risk assessment completed')

            # Determine if deep analysis is needed
            should_deep_analyze = risk_level in ['medium', 'high']

            return {
                'risk_level': risk_level,
                'confidence': confidence,
                'reasoning': reasoning,
                'scam_indicators': indicators,
                'should_deep_analyze': should_deep_analyze
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {str(e)}")
            logger.debug(f"Raw response: {response_text[:200]}")
            # Return medium risk on parse error to trigger Claude analysis
            return {
                'risk_level': 'medium',
                'confidence': 0.5,
                'reasoning': 'Failed to parse risk assessment',
                'scam_indicators': [],
                'should_deep_analyze': True
            }
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            return {
                'risk_level': 'medium',
                'confidence': 0.5,
                'reasoning': 'Error in risk assessment',
                'scam_indicators': [],
                'should_deep_analyze': True
            }

    def _fallback_screening(self, text: str) -> Dict[str, any]:
        """
        Fallback rule-based screening if Gemini is unavailable.

        Args:
            text: Text to screen

        Returns:
            Screening result dictionary
        """
        text_lower = text.lower()

        # High-risk keywords (common in Indian scams)
        high_risk_keywords = [
            'blocked', 'suspend', 'otp', 'password', 'cvv', 'pin',
            'urgent', 'immediately', 'verify now', 'click here',
            'account blocked', 'expire', 'locked', 'upi', 'paytm',
            'aadhar', 'pan card', 'kyc pending'
        ]

        # Medium-risk keywords
        medium_risk_keywords = [
            'verify', 'confirm', 'update', 'bank', 'payment',
            'refund', 'prize', 'won', 'lucky', 'congratulations',
            'government', 'tax', 'reward'
        ]

        # Count matches
        high_risk_count = sum(1 for kw in high_risk_keywords if kw in text_lower)
        medium_risk_count = sum(1 for kw in medium_risk_keywords if kw in text_lower)

        # Detect URLs
        has_url = 'http://' in text_lower or 'https://' in text_lower or 'bit.ly' in text_lower

        # Determine risk level
        if high_risk_count >= 2 or (high_risk_count >= 1 and has_url):
            risk_level = 'high'
            confidence = 0.8
            reasoning = f'Multiple high-risk keywords detected ({high_risk_count})'
            should_deep_analyze = True
        elif high_risk_count >= 1 or medium_risk_count >= 2:
            risk_level = 'medium'
            confidence = 0.6
            reasoning = 'Suspicious keywords present, needs analysis'
            should_deep_analyze = True
        else:
            risk_level = 'low'
            confidence = 0.5
            reasoning = 'No obvious scam indicators'
            should_deep_analyze = False

        # Extract detected keywords
        detected = []
        for kw in high_risk_keywords + medium_risk_keywords:
            if kw in text_lower:
                detected.append(kw)

        logger.info(
            f"Fallback screening: risk={risk_level}, "
            f"confidence={confidence:.2f}, indicators={len(detected)}"
        )

        return {
            'risk_level': risk_level,
            'confidence': confidence,
            'reasoning': reasoning,
            'scam_indicators': detected[:5],  # Top 5
            'should_deep_analyze': should_deep_analyze
        }

    def is_enabled(self) -> bool:
        """Check if Gemini service is enabled."""
        return self.enabled


# Global Gemini service instance
_gemini_service = None


def get_gemini_service() -> GeminiService:
    """Get or create the global Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
