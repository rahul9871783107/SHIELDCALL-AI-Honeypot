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
    # Normalize: strip all non-digits except leading +
    normalized = []
    for num in numbers:
        clean = re.sub(r'[\s.\-\(\)]', '', num)
        # Strip leading country code / STD prefix to get 10-digit number
        if clean.startswith('+91'):
            clean = clean[3:]
        elif clean.startswith('91') and len(clean) == 12:
            clean = clean[2:]
        elif clean.startswith('0') and len(clean) == 11:
            clean = clean[1:]
        if len(clean) == 10 and clean not in normalized:
            normalized.append(clean)
    return normalized


def extract_bank_accounts(text: str) -> List[str]:
    """Extract potential bank account numbers from text."""
    accounts = set()

    # 1. Plain 9-18 digit numbers
    plain_pattern = INTELLIGENCE_PATTERNS["bank_account"]
    plain_matches = extract_patterns(text, plain_pattern)
    accounts.update(plain_matches)

    # 2. Formatted: 1234-5678-9012-3456 or 1234 5678 9012 3456
    fmt_pattern = INTELLIGENCE_PATTERNS["bank_account_formatted"]
    fmt_matches = re.findall(fmt_pattern, text, re.IGNORECASE)
    for m in fmt_matches:
        digits = re.sub(r'[^\d]', '', m)
        accounts.add(digits)

    # 3. Prefixed: "a/c no: 50100123456789" or "account: 1234567890"
    pfx_pattern = INTELLIGENCE_PATTERNS["bank_account_prefixed"]
    pfx_matches = re.findall(pfx_pattern, text, re.IGNORECASE)
    accounts.update(pfx_matches)

    # Get phone digits to filter false positives
    phone_numbers = extract_phone_numbers(text)
    phone_digit_set = set(phone_numbers)
    # Also get raw phone digits with country code
    raw_phone_pattern = INTELLIGENCE_PATTERNS["phone_number"]
    raw_phones = re.findall(raw_phone_pattern, text, re.IGNORECASE)
    for p in raw_phones:
        if isinstance(p, tuple):
            p = ''.join(p)
        phone_digit_set.add(re.sub(r'[^\d]', '', p))

    # Get IFSC codes to exclude
    ifsc_pattern = INTELLIGENCE_PATTERNS["ifsc"]
    ifsc_matches = re.findall(ifsc_pattern, text)

    def should_exclude(acc):
        # Must be 9-18 digits
        if not (9 <= len(acc) <= 18):
            return True
        # Exclude phone numbers and their fragments
        if acc in phone_digit_set:
            return True
        if any(acc in pd or pd in acc for pd in phone_digit_set):
            return True
        # Exclude epoch timestamps (13 digits starting with 17)
        if len(acc) == 13 and acc.startswith('17'):
            return True
        # Exclude IFSC-adjacent numbers (the digits in IFSC codes)
        for ifsc in ifsc_matches:
            digits = re.sub(r'[^\d]', '', ifsc)
            if digits and acc == digits:
                return True
        return False

    return [acc for acc in accounts if not should_exclude(acc)]


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


def extract_case_ids(text: str) -> List[str]:
    """Extract case/reference/complaint/ticket IDs from text."""
    pattern = INTELLIGENCE_PATTERNS["case_id"]
    return extract_patterns(text, pattern)


def extract_policy_numbers(text: str) -> List[str]:
    """Extract policy numbers from text."""
    pattern = INTELLIGENCE_PATTERNS["policy_number"]
    return extract_patterns(text, pattern)


def extract_order_numbers(text: str) -> List[str]:
    """Extract order numbers from text."""
    pattern = INTELLIGENCE_PATTERNS["order_number"]
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
