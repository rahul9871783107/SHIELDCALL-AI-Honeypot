"""Test regex patterns against edge case strings."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')

from app.utils.helpers import (
    extract_upi_ids, extract_phone_numbers, extract_bank_accounts,
    extract_urls, extract_emails
)

test_cases = [
    {
        "input": "Send ₹5000 to fraud.payment@ybl immediately",
        "expect": {"upi": ["fraud.payment@ybl"], "phone": [], "bank": [], "url": [], "email": []},
    },
    {
        "input": "My account number is 1234-5678-9012-3456",
        "expect": {"upi": [], "phone": [], "bank": ["1234567890123456"], "url": [], "email": []},
    },
    {
        "input": "Call me at (91) 98765-43210 or +91.9876.543.210",
        "expect": {"upi": [], "phone": ["9876543210"], "bank": [], "url": [], "email": []},
    },
    {
        "input": "Visit https://sbi-kyc-update.fake.in/verify?token=abc123&ref=xyz",
        "expect": {"upi": [], "phone": [], "bank": [], "url": ["https://sbi-kyc-update.fake.in/verify?token=abc123&ref=xyz"], "email": []},
    },
    {
        "input": "Transfer to a/c no: 50100123456789 IFSC: HDFC0001234",
        "expect": {"upi": [], "phone": [], "bank": ["50100123456789"], "url": [], "email": []},
    },
    {
        "input": "UPI: Cashback.Claim@FakeUPI",
        "expect": {"upi": ["Cashback.Claim@FakeUPI"], "phone": [], "bank": [], "url": [], "email": []},
    },
    {
        "input": "Check www.pm-yojana-subsidy.fake.com/apply",
        "expect": {"upi": [], "phone": [], "bank": [], "url": ["www.pm-yojana-subsidy.fake.com/apply"], "email": []},
    },
    {
        "input": "Email us at support@mail.insurance-claims.co.in",
        "expect": {"upi": [], "phone": [], "bank": [], "url": [], "email": ["support@mail.insurance-claims.co.in"]},
    },
    {
        "input": "Your policy number 8877665544 call +91 88776 65544",
        "expect": {"upi": [], "phone": ["8877665544"], "bank": [], "url": [], "email": []},
    },
    {
        "input": "Send to 9876543210@paytm or gpay-refund@oksbi",
        "expect": {"upi": ["9876543210@paytm", "gpay-refund@oksbi"], "phone": [], "bank": [], "url": [], "email": []},
    },
]

passed = 0
failed = 0

for i, tc in enumerate(test_cases, 1):
    text = tc["input"]
    expect = tc["expect"]

    upi = extract_upi_ids(text)
    phone = extract_phone_numbers(text)
    bank = extract_bank_accounts(text)
    url = extract_urls(text)
    email = extract_emails(text)

    results = {"upi": upi, "phone": phone, "bank": bank, "url": url, "email": email}

    all_ok = True
    issues = []

    for key in expect:
        expected_set = set(expect[key])
        actual_set = set(results[key])
        # Check all expected items are found
        missing = expected_set - actual_set
        if missing:
            all_ok = False
            issues.append(f"  MISSING {key}: {missing}")

    if all_ok:
        print(f"TEST {i}: PASS - {text[:60]}...")
        passed += 1
    else:
        print(f"TEST {i}: FAIL - {text[:60]}...")
        for issue in issues:
            print(issue)
        print(f"  Got: upi={upi} phone={phone} bank={bank} url={url} email={email}")
        failed += 1

print(f"\n{'='*60}")
print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)}")
