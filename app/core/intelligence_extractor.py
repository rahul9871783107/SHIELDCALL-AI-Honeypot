"""
Intelligence Extractor - Extract Scammer Information
Extracts UPI IDs, phone numbers, bank accounts, URLs from messages.
"""
from typing import List, Dict
from app.models.response_models import ExtractedIntelligence
from app.utils.helpers import (
    extract_upi_ids,
    extract_phone_numbers,
    extract_bank_accounts,
    extract_urls,
    is_suspicious_url,
    get_detected_keywords
)
from app.config import SCAM_KEYWORDS
from app.utils.logger import app_logger as logger


class IntelligenceExtractor:
    """
    Extracts intelligence from scammer messages.
    Accumulates findings over conversation.
    """

    def __init__(self):
        """Initialize intelligence extractor."""
        self.intelligence = ExtractedIntelligence()

    def extract_from_message(self, text: str) -> ExtractedIntelligence:
        """
        Extract all intelligence from a single message.

        Args:
            text: Message text to analyze

        Returns:
            ExtractedIntelligence with findings
        """
        # Extract UPI IDs
        upi_ids = extract_upi_ids(text)
        if upi_ids:
            logger.info(f"Found {len(upi_ids)} UPI ID(s): {upi_ids}")
            self.intelligence.upiIds.extend(upi_ids)

        # Extract phone numbers
        phone_numbers = extract_phone_numbers(text)
        if phone_numbers:
            logger.info(f"Found {len(phone_numbers)} phone number(s): {phone_numbers}")
            self.intelligence.phoneNumbers.extend(phone_numbers)

        # Extract bank accounts
        bank_accounts = extract_bank_accounts(text)
        if bank_accounts:
            logger.info(f"Found {len(bank_accounts)} bank account(s): {bank_accounts}")
            self.intelligence.bankAccounts.extend(bank_accounts)

        # Extract URLs and check if suspicious
        urls = extract_urls(text)
        if urls:
            suspicious_urls = [url for url in urls if is_suspicious_url(url)]
            if suspicious_urls:
                logger.warning(f"Found {len(suspicious_urls)} suspicious URL(s): {suspicious_urls}")
                self.intelligence.phishingLinks.extend(suspicious_urls)
            else:
                logger.info(f"Found {len(urls)} URL(s): {urls}")
                self.intelligence.phishingLinks.extend(urls)

        # Extract scam keywords
        keywords = get_detected_keywords(text, SCAM_KEYWORDS)
        if keywords:
            logger.debug(f"Detected keywords: {keywords}")
            self.intelligence.suspiciousKeywords.extend(keywords)

        # Remove duplicates from all lists
        self.intelligence.upiIds = list(set(self.intelligence.upiIds))
        self.intelligence.phoneNumbers = list(set(self.intelligence.phoneNumbers))
        self.intelligence.bankAccounts = list(set(self.intelligence.bankAccounts))
        self.intelligence.phishingLinks = list(set(self.intelligence.phishingLinks))
        self.intelligence.suspiciousKeywords = list(set(self.intelligence.suspiciousKeywords))

        return self.intelligence

    def get_summary(self) -> str:
        """
        Get summary of extracted intelligence.

        Returns:
            Human-readable summary
        """
        if not self.intelligence.has_intelligence():
            return "No intelligence extracted yet."

        summary_parts = []

        if self.intelligence.upiIds:
            summary_parts.append(f"UPI IDs: {', '.join(self.intelligence.upiIds)}")

        if self.intelligence.phoneNumbers:
            summary_parts.append(f"Phone Numbers: {', '.join(self.intelligence.phoneNumbers)}")

        if self.intelligence.bankAccounts:
            summary_parts.append(f"Bank Accounts: {', '.join(self.intelligence.bankAccounts)}")

        if self.intelligence.phishingLinks:
            summary_parts.append(f"Phishing Links: {', '.join(self.intelligence.phishingLinks[:3])}")

        if self.intelligence.suspiciousKeywords:
            top_keywords = self.intelligence.suspiciousKeywords[:5]
            summary_parts.append(f"Keywords: {', '.join(top_keywords)}")

        return " | ".join(summary_parts)

    def get_intelligence(self) -> ExtractedIntelligence:
        """Get current intelligence object."""
        return self.intelligence
