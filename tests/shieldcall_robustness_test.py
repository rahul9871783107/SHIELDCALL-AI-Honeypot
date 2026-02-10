#!/usr/bin/env python3
"""
SHIELDCALL Grand Finale Robustness Testing Suite
=================================================
Run this BEFORE the event to ensure your system handles ANY input
the judges/leaderboard might throw at it.

Usage:
    python shieldcall_robustness_test.py

Requirements:
    pip install requests
"""

import requests
import json
import time
import sys
from datetime import datetime

# ============================================================
# CONFIGURATION — Update these if needed
# ============================================================
API_URL = "https://reasonable-balance-production.up.railway.app"
API_KEY = "hackathon-secret-key-2026"
ENDPOINT = "/api/honeypot"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# ============================================================
# TEST TRACKING
# ============================================================
results = {"passed": 0, "failed": 0, "warnings": 0, "errors": []}


def log_result(test_name, passed, details="", warning=False):
    if passed:
        results["passed"] += 1
        icon = "✅"
    elif warning:
        results["warnings"] += 1
        icon = "⚠️"
    else:
        results["failed"] += 1
        results["errors"].append(f"{test_name}: {details}")
        icon = "❌"
    print(f"  {icon} {test_name}" + (f" — {details}" if details else ""))


def send_request(payload, method="POST", endpoint=None, headers=None, timeout=30):
    """Send request and return (status_code, response_json, elapsed_ms)"""
    url = f"{API_URL}{endpoint or ENDPOINT}"
    h = headers or HEADERS
    try:
        start = time.time()
        if method == "POST":
            r = requests.post(url, json=payload, headers=h, timeout=timeout)
        elif method == "GET":
            r = requests.get(url, headers=h, timeout=timeout)
        elapsed = round((time.time() - start) * 1000)
        try:
            body = r.json()
        except:
            body = {"raw": r.text[:500]}
        return r.status_code, body, elapsed
    except requests.exceptions.Timeout:
        return None, {"error": "TIMEOUT"}, timeout * 1000
    except Exception as e:
        return None, {"error": str(e)}, 0


def make_message(text, session_id=None, sender="scammer", timestamp=None,
                 conversation_history=None, metadata=None):
    """Build a standard request payload."""
    return {
        "sessionId": session_id or f"test-{int(time.time())}",
        "message": {
            "sender": sender,
            "text": text,
            "timestamp": timestamp or datetime.utcnow().isoformat() + "Z"
        },
        "conversationHistory": conversation_history or [],
        "metadata": metadata or {}
    }


# ============================================================
# TEST SUITES
# ============================================================

def test_health_check():
    """Suite 1: Basic connectivity and health."""
    print("\n" + "=" * 60)
    print("🏥 SUITE 1: Health & Connectivity")
    print("=" * 60)

    # Health endpoint
    status, body, ms = send_request(None, method="GET", endpoint="/health")
    log_result("Health endpoint responds", status == 200, f"{ms}ms")

    # Health response has expected fields
    if status == 200:
        has_status = "status" in body
        log_result("Health has 'status' field", has_status)

    # Docs endpoint
    status2, _, ms2 = send_request(None, method="GET", endpoint="/docs")
    log_result("Docs endpoint responds", status2 == 200, f"{ms2}ms")


def test_authentication():
    """Suite 2: Auth handling — must not crash on bad auth."""
    print("\n" + "=" * 60)
    print("🔐 SUITE 2: Authentication")
    print("=" * 60)

    payload = make_message("Test auth")

    # No API key
    status, body, _ = send_request(payload, headers={"Content-Type": "application/json"})
    log_result("Rejects missing API key", status in (401, 403))

    # Wrong API key
    status, body, _ = send_request(payload, headers={
        "Content-Type": "application/json",
        "x-api-key": "wrong-key-12345"
    })
    log_result("Rejects wrong API key", status in (401, 403))

    # Empty API key
    status, body, _ = send_request(payload, headers={
        "Content-Type": "application/json",
        "x-api-key": ""
    })
    log_result("Rejects empty API key", status in (401, 403))

    # Valid key works
    status, body, _ = send_request(payload)
    log_result("Accepts valid API key", status == 200)


def test_basic_scam_detection():
    """Suite 3: Core scam detection — the bread and butter."""
    print("\n" + "=" * 60)
    print("🎯 SUITE 3: Core Scam Detection")
    print("=" * 60)

    scam_messages = [
        ("Bank blocking scam", "URGENT! Your SBI account will be blocked in 24 hours. Click here to verify your KYC immediately: http://sbi-verify.fake.com"),
        ("UPI fraud", "You have received a refund of Rs 5000. Send Rs 50 to confirm. UPI: fraud@paytm"),
        ("OTP scam", "Your OTP is 456789. Share it with our executive to complete verification. Call 9876543210 NOW!"),
        ("Lottery scam", "Congratulations! You won Rs 10,00,000 in KBC lottery! Transfer Rs 5000 registration fee to account 12345678901234"),
        ("KYC update scam", "Dear customer, your PAN card is linked with suspicious activity. Update KYC at http://pan-update.fake.in or face account freeze."),
        ("Job offer scam", "Work from home! Earn Rs 50000/day! No investment needed. Just share your Aadhar and bank details. WhatsApp: 8765432109"),
    ]

    for name, msg in scam_messages:
        status, body, ms = send_request(make_message(msg))
        has_reply = status == 200 and body.get("reply") and len(body.get("reply", "")) > 0
        log_result(f"{name}", has_reply, f"{ms}ms | reply_len={len(body.get('reply', ''))}")


def test_low_risk_messages():
    """Suite 4: Low-risk messages — should still respond, not crash."""
    print("\n" + "=" * 60)
    print("💬 SUITE 4: Low-Risk / Normal Messages")
    print("=" * 60)

    normal_messages = [
        ("Simple greeting", "Hello, how are you?"),
        ("Weather chat", "What's the weather like today?"),
        ("Family message", "Mom, I'll be home for dinner tonight"),
        ("Work message", "Meeting at 3pm confirmed, see you there"),
        ("Short message", "Ok"),
    ]

    for name, msg in normal_messages:
        status, body, ms = send_request(make_message(msg))
        log_result(f"{name}", status == 200, f"{ms}ms")


def test_hindi_hinglish():
    """Suite 5: Hindi & Hinglish messages — critical for India-specific."""
    print("\n" + "=" * 60)
    print("🇮🇳 SUITE 5: Hindi / Hinglish Messages")
    print("=" * 60)

    hindi_messages = [
        ("Hindi scam", "आपका बैंक खाता बंद होने वाला है। तुरंत वेरिफाई करें: http://bank-verify.fake.com"),
        ("Hinglish scam", "Aapka SBI account block ho jayega! Abhi verify karo: 9876543210 pe call karo"),
        ("Hindi UPI scam", "आपको ₹5000 का रिफंड मिला है। कन्फर्म करने के लिए ₹50 भेजें UPI: scam@paytm"),
        ("Hinglish lottery", "Bhai tune 10 lakh jeete hain! Registration fee 5000 bhej de account 1234567890 mein"),
        ("Mixed script", "Your account mein problem hai. Aadhar number share karo verification ke liye"),
    ]

    for name, msg in hindi_messages:
        status, body, ms = send_request(make_message(msg))
        has_reply = status == 200 and body.get("reply") and len(body.get("reply", "")) > 0
        log_result(f"{name}", has_reply, f"{ms}ms")


def test_edge_cases():
    """Suite 6: Edge cases — these are what BREAK systems in live tests."""
    print("\n" + "=" * 60)
    print("⚡ SUITE 6: Edge Cases (CRITICAL FOR LEADERBOARD)")
    print("=" * 60)

    # Empty message
    status, body, ms = send_request(make_message(""))
    log_result("Empty message string", status in (200, 400, 422), f"status={status}, {ms}ms")

    # Very long message (2000+ chars)
    long_msg = "Your account is compromised! " * 100
    status, body, ms = send_request(make_message(long_msg))
    log_result("Very long message (3000+ chars)", status == 200, f"{ms}ms")

    # Special characters
    status, body, ms = send_request(make_message("!@#$%^&*()_+-=[]{}|;':\",./<>?"))
    log_result("Special characters only", status in (200, 400), f"status={status}, {ms}ms")

    # Unicode / emoji
    status, body, ms = send_request(make_message("🚨 URGENT 🚨 Account blocked! 💰 Send money 💸"))
    log_result("Emoji-heavy message", status == 200, f"{ms}ms")

    # Only whitespace
    status, body, ms = send_request(make_message("   \n\t   "))
    log_result("Whitespace-only message", status in (200, 400, 422), f"status={status}, {ms}ms")

    # Single character
    status, body, ms = send_request(make_message("a"))
    log_result("Single character", status in (200, 400), f"status={status}, {ms}ms")

    # Numbers only
    status, body, ms = send_request(make_message("9876543210"))
    log_result("Numbers only (phone number)", status == 200, f"{ms}ms")

    # URL only
    status, body, ms = send_request(make_message("http://malicious-site.com/phishing/login"))
    log_result("URL-only message", status == 200, f"{ms}ms")

    # Repeated characters
    status, body, ms = send_request(make_message("AAAAAAAAAAAAAAAAAAAAA"))
    log_result("Repeated characters", status in (200, 400), f"status={status}, {ms}ms")

    # Null bytes / control characters
    status, body, ms = send_request(make_message("test\x00message\x01with\x02control"))
    log_result("Control characters", status in (200, 400, 422), f"status={status}, {ms}ms")


def test_timestamp_formats():
    """Suite 7: Timestamp variations — this broke you before!"""
    print("\n" + "=" * 60)
    print("⏰ SUITE 7: Timestamp Format Handling")
    print("=" * 60)

    test_timestamps = [
        ("ISO string", "2026-02-16T10:00:00Z"),
        ("ISO with offset", "2026-02-16T15:30:00+05:30"),
        ("ISO without Z", "2026-02-16T10:00:00"),
        ("Epoch milliseconds (int)", 1770025292801),
        ("Epoch seconds (int)", 1770025292),
        ("Date only string", "2026-02-16"),
        ("Empty string timestamp", ""),
    ]

    for name, ts in test_timestamps:
        payload = {
            "sessionId": f"ts-test-{int(time.time())}",
            "message": {
                "sender": "scammer",
                "text": "Your account is blocked! Verify now!",
                "timestamp": ts
            },
            "conversationHistory": [],
            "metadata": {}
        }
        status, body, ms = send_request(payload)
        # Should either work (200) or gracefully reject (400/422), NOT crash (500)
        no_crash = status in (200, 400, 422)
        log_result(f"Timestamp: {name}", no_crash, f"status={status}, {ms}ms")


def test_malformed_inputs():
    """Suite 8: Malformed/unexpected request bodies."""
    print("\n" + "=" * 60)
    print("💥 SUITE 8: Malformed Inputs (Crash Prevention)")
    print("=" * 60)

    # Missing sessionId
    payload = {"message": {"sender": "scammer", "text": "test", "timestamp": "2026-02-16T10:00:00Z"}}
    status, body, ms = send_request(payload)
    log_result("Missing sessionId", status in (200, 400, 422), f"status={status}")

    # Missing message field entirely
    payload = {"sessionId": "test-missing-msg"}
    status, body, ms = send_request(payload)
    log_result("Missing message field", status in (200, 400, 422), f"status={status}")

    # Message as string instead of object
    payload = {"sessionId": "test-str-msg", "message": "Your account is blocked!"}
    status, body, ms = send_request(payload)
    log_result("Message as plain string", status in (200, 400, 422), f"status={status}")

    # Empty object
    payload = {}
    status, body, ms = send_request(payload)
    log_result("Empty JSON object", status in (200, 400, 422), f"status={status}")

    # Null values
    payload = {"sessionId": None, "message": None}
    status, body, ms = send_request(payload)
    log_result("Null values", status in (200, 400, 422), f"status={status}")

    # Extra unexpected fields
    payload = make_message("Test with extras")
    payload["extraField1"] = "unexpected"
    payload["extraField2"] = {"nested": True}
    payload["priority"] = 999
    status, body, ms = send_request(payload)
    log_result("Extra unexpected fields", status == 200, f"status={status}")

    # Missing sender in message
    payload = {
        "sessionId": "test-no-sender",
        "message": {"text": "Your account blocked!", "timestamp": "2026-02-16T10:00:00Z"},
        "conversationHistory": [],
        "metadata": {}
    }
    status, body, ms = send_request(payload)
    log_result("Missing sender field", status in (200, 400, 422), f"status={status}")

    # Missing text in message
    payload = {
        "sessionId": "test-no-text",
        "message": {"sender": "scammer", "timestamp": "2026-02-16T10:00:00Z"},
        "conversationHistory": [],
        "metadata": {}
    }
    status, body, ms = send_request(payload)
    log_result("Missing text field", status in (200, 400, 422), f"status={status}")

    # Conversation history as string
    payload = make_message("Test conv history")
    payload["conversationHistory"] = "not an array"
    status, body, ms = send_request(payload)
    log_result("ConversationHistory as string", status in (200, 400, 422), f"status={status}")

    # Array message (wrong type)
    payload = {"sessionId": "test-arr", "message": ["item1", "item2"]}
    status, body, ms = send_request(payload)
    log_result("Message as array", status in (200, 400, 422), f"status={status}")


def test_conversation_history():
    """Suite 9: Multi-turn conversations — test context handling."""
    print("\n" + "=" * 60)
    print("🔄 SUITE 9: Conversation History & Context")
    print("=" * 60)

    session_id = f"multi-turn-{int(time.time())}"

    # Turn 1
    status1, body1, ms1 = send_request(make_message(
        "Your SBI account will be blocked! Call 9876543210 immediately!",
        session_id=session_id
    ))
    log_result("Multi-turn: Message 1", status1 == 200, f"{ms1}ms")

    reply1 = body1.get("reply", "") if status1 == 200 else ""

    # Turn 2 with history
    history = [
        {"sender": "scammer", "text": "Your SBI account will be blocked!", "timestamp": "2026-02-16T10:00:00Z"},
        {"sender": "user", "text": reply1, "timestamp": "2026-02-16T10:01:00Z"},
    ]
    status2, body2, ms2 = send_request(make_message(
        "Sir please share your account number and OTP for verification. UPI: scammer@ybl",
        session_id=session_id,
        conversation_history=history
    ))
    log_result("Multi-turn: Message 2 (with history)", status2 == 200, f"{ms2}ms")

    # Turn 3 with longer history
    reply2 = body2.get("reply", "") if status2 == 200 else ""
    history.extend([
        {"sender": "scammer", "text": "Share your OTP", "timestamp": "2026-02-16T10:02:00Z"},
        {"sender": "user", "text": reply2, "timestamp": "2026-02-16T10:03:00Z"},
    ])
    status3, body3, ms3 = send_request(make_message(
        "This is your last chance! Your account will be permanently closed!",
        session_id=session_id,
        conversation_history=history
    ))
    log_result("Multi-turn: Message 3 (longer history)", status3 == 200, f"{ms3}ms")

    # Very long conversation history (10 turns)
    long_history = []
    for i in range(10):
        long_history.append({"sender": "scammer", "text": f"Scam message {i}", "timestamp": "2026-02-16T10:00:00Z"})
        long_history.append({"sender": "user", "text": f"Response {i}", "timestamp": "2026-02-16T10:01:00Z"})
    status4, body4, ms4 = send_request(make_message(
        "Final scam attempt!",
        session_id=f"long-history-{int(time.time())}",
        conversation_history=long_history
    ))
    log_result("Long conversation history (20 entries)", status4 == 200, f"{ms4}ms")


def test_response_time():
    """Suite 10: Response time under various loads."""
    print("\n" + "=" * 60)
    print("⚡ SUITE 10: Response Time Performance")
    print("=" * 60)

    # Simple message timing
    times = []
    for i in range(3):
        _, _, ms = send_request(make_message(f"Performance test {i}: Your account blocked!"))
        times.append(ms)
        time.sleep(0.5)

    avg_time = sum(times) / len(times)
    max_time = max(times)
    log_result(f"Average response time", avg_time < 10000, f"avg={avg_time:.0f}ms, max={max_time}ms")
    log_result(f"Max response time < 15s", max_time < 15000, f"{max_time}ms")

    if avg_time > 5000:
        log_result("Response time WARNING", False,
                   f"avg={avg_time:.0f}ms is slow — judges may penalize", warning=True)


def test_rapid_fire():
    """Suite 11: Rapid successive requests — simulates live test pressure."""
    print("\n" + "=" * 60)
    print("🔥 SUITE 11: Rapid-Fire Requests (Live Test Simulation)")
    print("=" * 60)

    messages = [
        "Account blocked! Verify now!",
        "You won lottery! Send registration fee!",
        "OTP is 123456. Share with executive.",
        "KYC update required. Click link.",
        "Job offer: Earn 50000/day from home!",
    ]

    success_count = 0
    total_time = 0
    for i, msg in enumerate(messages):
        status, body, ms = send_request(make_message(msg, session_id=f"rapid-{i}-{int(time.time())}"))
        if status == 200:
            success_count += 1
        total_time += ms
        time.sleep(0.3)  # Minimal delay

    log_result(f"Rapid-fire: {success_count}/5 succeeded", success_count >= 4,
               f"total={total_time}ms, avg={total_time // 5}ms")


def test_intelligence_extraction():
    """Suite 12: Verify intelligence extraction is working."""
    print("\n" + "=" * 60)
    print("🔍 SUITE 12: Intelligence Extraction Verification")
    print("=" * 60)

    # Send message with extractable intelligence
    intel_message = (
        "Send Rs 5000 to my account immediately! "
        "UPI: fraudster@paytm, "
        "Phone: 9876543210, "
        "Bank Account: 1234567890123456, "
        "IFSC: SBIN0012345, "
        "Click: http://phishing-link.fake.com/steal"
    )
    status, body, ms = send_request(make_message(intel_message))
    log_result("Intel message accepted", status == 200, f"{ms}ms")

    # Check stats endpoint
    status2, stats, ms2 = send_request(None, method="GET", endpoint="/api/stats", headers=HEADERS)
    if status2 == 200:
        total_intel = stats.get("total_intelligence_extracted", 0)
        log_result(f"Intelligence items tracked", total_intel > 0, f"count={total_intel}")
    else:
        log_result("Stats endpoint available", False, f"status={status2}", warning=True)


def test_metadata_variations():
    """Suite 13: Various metadata formats."""
    print("\n" + "=" * 60)
    print("📋 SUITE 13: Metadata Handling")
    print("=" * 60)

    test_cases = [
        ("Empty metadata", {}),
        ("Standard metadata", {"channel": "SMS", "language": "English", "locale": "IN"}),
        ("Hindi metadata", {"channel": "WhatsApp", "language": "Hindi", "locale": "IN"}),
        ("Extra fields", {"channel": "SMS", "custom_field": "value", "priority": 5}),
        ("Nested metadata", {"source": {"app": "test", "version": "1.0"}}),
        ("No metadata key", None),  # Will be handled by make_message default
    ]

    for name, meta in test_cases:
        if meta is None:
            payload = make_message("Account blocked! Verify now!")
            del payload["metadata"]
        else:
            payload = make_message("Account blocked! Verify now!", metadata=meta)
        status, body, ms = send_request(payload)
        log_result(f"{name}", status in (200, 400, 422), f"status={status}, {ms}ms")


# ============================================================
# GUVI-SPECIFIC FORMAT TESTS
# ============================================================

def test_guvi_format():
    """Suite 14: Test GUVI's known request format."""
    print("\n" + "=" * 60)
    print("🏗️ SUITE 14: GUVI-Specific Format Tests")
    print("=" * 60)

    # GUVI format with integer timestamp (the bug that was fixed)
    guvi_payload = {
        "sessionId": f"guvi-test-{int(time.time())}",
        "message": {
            "sender": "scammer",
            "text": "Your account has been compromised. Verify immediately at http://fake-bank.com",
            "timestamp": 1770025292801  # Integer epoch ms — GUVI's format
        },
        "conversationHistory": [],
        "metadata": {}
    }
    status, body, ms = send_request(guvi_payload)
    log_result("GUVI format (int timestamp)", status == 200, f"{ms}ms")

    # GUVI format with minimal fields
    guvi_minimal = {
        "sessionId": f"guvi-min-{int(time.time())}",
        "message": "Simple string message from GUVI"
    }
    status, body, ms = send_request(guvi_minimal)
    log_result("GUVI minimal format", status in (200, 400, 422), f"status={status}")

    # GUVI callback test (if endpoint exists)
    status3, body3, ms3 = send_request(None, method="GET",
                                        endpoint="/api/callback-status",
                                        headers=HEADERS)
    if status3 == 200:
        log_result("GUVI callback endpoint exists", True, f"{ms3}ms")
    else:
        log_result("GUVI callback endpoint", False, "endpoint not found", warning=True)


# ============================================================
# MAIN — Run All Tests
# ============================================================

def main():
    print("=" * 60)
    print("🛡️  SHIELDCALL ROBUSTNESS TEST SUITE")
    print(f"🎯  Target: {API_URL}{ENDPOINT}")
    print(f"📅  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Verify connectivity first
    try:
        r = requests.get(f"{API_URL}/health", timeout=10)
        if r.status_code != 200:
            print(f"\n❌ API is not responding! Status: {r.status_code}")
            print("   Fix your deployment before running tests.")
            sys.exit(1)
        print(f"\n✅ API is live! Health check passed.")
    except Exception as e:
        print(f"\n❌ Cannot reach API: {e}")
        print("   Make sure Railway deployment is running.")
        sys.exit(1)

    start_time = time.time()

    # Run all test suites
    test_health_check()
    test_authentication()
    test_basic_scam_detection()
    test_low_risk_messages()
    test_hindi_hinglish()
    test_edge_cases()
    test_timestamp_formats()
    test_malformed_inputs()
    test_conversation_history()
    test_response_time()
    test_rapid_fire()
    test_intelligence_extraction()
    test_metadata_variations()
    test_guvi_format()

    elapsed = round(time.time() - start_time)

    # ============================================================
    # RESULTS SUMMARY
    # ============================================================
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)

    total = results["passed"] + results["failed"] + results["warnings"]
    print(f"\n  Total tests:    {total}")
    print(f"  ✅ Passed:       {results['passed']}")
    print(f"  ❌ Failed:       {results['failed']}")
    print(f"  ⚠️  Warnings:    {results['warnings']}")
    print(f"  ⏱️  Total time:  {elapsed}s")

    pass_rate = (results["passed"] / total * 100) if total > 0 else 0
    print(f"\n  Pass rate: {pass_rate:.1f}%")

    if results["errors"]:
        print(f"\n{'=' * 60}")
        print("❌ FAILED TESTS (FIX THESE BEFORE THE EVENT):")
        print("=" * 60)
        for err in results["errors"]:
            print(f"  • {err}")

    # Verdict
    print(f"\n{'=' * 60}")
    if results["failed"] == 0:
        print("🏆 VERDICT: SYSTEM IS ROBUST — READY FOR GRAND FINALE!")
    elif results["failed"] <= 3:
        print("⚠️  VERDICT: MOSTLY READY — Fix the failures above")
    else:
        print("🚨 VERDICT: NEEDS WORK — Fix critical failures before event")
    print("=" * 60)

    # Recommendations
    if results["failed"] > 0:
        print("\n📋 RECOMMENDATIONS:")
        print("  1. Fix all ❌ failures — these could cost you leaderboard rank")
        print("  2. Add try/except wrappers around input parsing")
        print("  3. Return 400 (not 500) for invalid inputs")
        print("  4. Test again after fixes")
    else:
        print("\n📋 NEXT STEPS:")
        print("  1. System is solid — move on to pitch practice!")
        print("  2. Run this test again on Feb 15 as final check")
        print("  3. Keep Railway deployment stable (don't push risky changes)")

    return results["failed"]


if __name__ == "__main__":
    exit_code = main()
    sys.exit(min(exit_code, 1))
