"""
Gemini Service - Layer 2: Quick Risk Screening
Uses Google Gemini Flash for ultra-fast scam detection (<200ms).
Cost: ~$0.00001 per request (extremely cheap!)
"""
from typing import Dict, Literal
import google.generativeai as genai
from app.config import settings
from app.utils.logger import app_logger as logger
import json

RiskLevel = Literal["low", "medium", "high"]


class GeminiService:
    """
    Layer 2: Gemini Flash for quick risk screening.

    Features:
    - Ultra-fast initial risk check (<200ms)
    - Pattern matching against known scams
    - Returns: risk_level (low/medium/high)
    - Cost: Very cheap (~$0.00001 per request)
    """

    def __init__(self):
        """Initialize Gemini service."""
        if settings.google_api_key and settings.google_api_key != "your-google-key-here":
            try:
                genai.configure(api_key=settings.google_api_key)
                self.model = genai.GenerativeModel(settings.gemini_model)
                self.enabled = True
                logger.info(f"GeminiService initialized with model: {settings.gemini_model}")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {str(e)}")
                self.model = None
                self.enabled = False
        else:
            self.model = None
            self.enabled = False
            logger.warning("Google API key not set. Gemini service disabled (using fallback).")

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
