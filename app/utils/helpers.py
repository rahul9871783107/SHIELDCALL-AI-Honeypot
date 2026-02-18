"""
Helper Utility Functions
Common functions used across the application.
"""
import re
from typing import List, Dict
from datetime import datetime
from app.config import INTELLIGENCE_PATTERNS


def extract_patterns(text: str, pattern: str) -> List[str]:
    """
    Extract all matches of a regex pattern from text.

    Args:
        text: Input text to search
        pattern: Regex pattern to match

    Returns:
        List of unique matches
    """
    matches = re.findall(pattern, text, re.IGNORECASE)
    # Handle tuples from groups (like phone numbers)
    if matches and isinstance(matches[0], tuple):
        matches = [''.join(match) for match in matches]
    return list(set(matches))


def extract_upi_ids(text: str) -> List[str]:
    """Extract UPI IDs from text."""
    pattern = INTELLIGENCE_PATTERNS["upi_id"]
    upi_ids = extract_patterns(text, pattern)
    # Email-like domains to exclude (these are emails, not UPI IDs)
    email_tlds = ('.com', '.org', '.net', '.co.in', '.edu', '.gov', '.in', '.io')
    cleaned = []
    for upi in upi_ids:
        upi = upi.rstrip('.')  # Strip trailing periods from sentence endings
        if '@' in upi and not any(upi.endswith(tld) for tld in email_tlds) and upi not in cleaned:
            cleaned.append(upi)
    return cleaned


def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text."""
    pattern = INTELLIGENCE_PATTERNS["phone_number"]
    numbers = extract_patterns(text, pattern)
    # Normalize: strip internal spaces/dashes for clean output
    normalized = []
    for num in numbers:
        clean = re.sub(r'[\s\-]', '', num)
        if clean not in normalized:
            normalized.append(clean)
    return normalized


def extract_bank_accounts(text: str) -> List[str]:
    """Extract potential bank account numbers from text."""
    pattern = INTELLIGENCE_PATTERNS["bank_account"]
    accounts = extract_patterns(text, pattern)
    # Get phone digits to filter false positives (e.g. 9876543210 from +91-9876543210)
    phone_pattern = INTELLIGENCE_PATTERNS["phone_number"]
    phone_matches = re.findall(phone_pattern, text, re.IGNORECASE)
    phone_digit_strings = []
    for p in phone_matches:
        if isinstance(p, tuple):
            p = ''.join(p)
        phone_digit_strings.append(re.sub(r'[^\d]', '', p))
    # Filter: 9-18 digits AND not a substring of any phone number's digits
    def is_phone_fragment(acc):
        return any(acc in pd for pd in phone_digit_strings)
    return [acc for acc in accounts if 9 <= len(acc) <= 18 and not is_phone_fragment(acc)]


def extract_urls(text: str) -> List[str]:
    """Extract URLs (http/https and www.) from text."""
    pattern = INTELLIGENCE_PATTERNS["url"]
    urls = extract_patterns(text, pattern)
    # Also extract www. URLs without http prefix
    www_pattern = INTELLIGENCE_PATTERNS["url_www"]
    www_urls = extract_patterns(text, www_pattern)
    all_urls = list(set(urls + www_urls))
    # Strip trailing punctuation that gets caught by regex
    return [url.rstrip('.,;:!?)') for url in all_urls]


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text."""
    pattern = INTELLIGENCE_PATTERNS["email"]
    return extract_patterns(text, pattern)


def is_suspicious_url(url: str) -> bool:
    """
    Check if a URL looks suspicious/phishing.

    Args:
        url: URL to check

    Returns:
        True if URL appears suspicious
    """
    suspicious_indicators = [
        'bit.ly', 'tinyurl', 'short.link',  # URL shorteners
        'secure-bank', 'verify-account', 'update-kyc',  # Fake banking
        '.tk', '.ml', '.ga', '.cf',  # Suspicious TLDs
        'login', 'signin', 'verify', 'update',  # Phishing keywords
    ]

    url_lower = url.lower()
    return any(indicator in url_lower for indicator in suspicious_indicators)


def count_scam_keywords(text: str, keyword_dict: Dict[str, List[str]]) -> Dict[str, int]:
    """
    Count occurrences of scam keywords by category.

    Args:
        text: Text to analyze
        keyword_dict: Dictionary of keyword categories

    Returns:
        Dictionary with counts per category
    """
    text_lower = text.lower()
    counts = {}

    for category, keywords in keyword_dict.items():
        count = sum(1 for keyword in keywords if keyword in text_lower)
        counts[category] = count

    return counts


def get_detected_keywords(text: str, keyword_dict: Dict[str, List[str]]) -> List[str]:
    """
    Get list of detected scam keywords from text.

    Args:
        text: Text to analyze
        keyword_dict: Dictionary of keyword categories

    Returns:
        List of detected keywords
    """
    text_lower = text.lower()
    detected = set()

    for category, keywords in keyword_dict.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected.add(keyword)

    return list(detected)


def format_timestamp(dt: datetime = None) -> str:
    """
    Format datetime to ISO-8601 string.

    Args:
        dt: Datetime object (uses current time if None)

    Returns:
        ISO-8601 formatted timestamp
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
