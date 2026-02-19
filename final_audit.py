"""
SHIELDCALL Final Pre-Competition Audit — Feb 19, 2026
Parts 2, 3, 4, 5, 7 combined into one script.
"""
import requests
import time
import json
import sys
import io
import uuid
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://reasonable-balance-production.up.railway.app/api/honeypot"
API_KEY = "hackathon-secret-key-2026"
HEADERS = {"Content-Type": "application/json", "x-api-key": API_KEY}

total_tests = 0
passed = 0
failed = 0
issues = []

def send(session_id, text, history=None, metadata=None, raw_payload=None):
    """Send a message and return parsed response."""
    if raw_payload:
        resp = requests.post(BASE_URL, json=raw_payload, headers=HEADERS, timeout=30)
    else:
        payload = {
            "sessionId": session_id,
            "message": {"sender": "scammer", "text": text, "timestamp": int(time.time() * 1000)},
            "conversationHistory": history or [],
            "metadata": metadata or {"channel": "SMS", "language": "English", "locale": "IN"}
        }
        resp = requests.post(BASE_URL, json=payload, headers=HEADERS, timeout=30)
    return resp

def check(label, condition, detail=""):
    global total_tests, passed, failed, issues
    total_tests += 1
    if condition:
        passed += 1
        return True
    else:
        failed += 1
        issues.append(f"FAIL: {label} — {detail}")
        print(f"    FAIL: {label} — {detail}")
        return False


# ============================================================
# PART 2: ADVERSARIAL INTELLIGENCE EXTRACTION TEST
# ============================================================
print("\n" + "="*70)
print("PART 2: ADVERSARIAL INTELLIGENCE EXTRACTION TEST (20 messages)")
print("="*70)

EXTRACTION_TESTS = [
    {
        "msg": "Your account 12345678901234 has been flagged. Call +919876543210",
        "expect": {"phone": ["9876543210"], "bank": ["12345678901234"], "upi": [], "url": [], "email": []}
    },
    {
        "msg": "Send Rs500 to verify@paytm for verification",
        "expect": {"phone": [], "bank": [], "upi": ["verify@paytm"], "url": [], "email": []}
    },
    {
        "msg": "Transfer to A/C No. 9876543210123456, IFSC SBIN0001234",
        "expect": {"phone": [], "bank": ["9876543210123456"], "upi": [], "url": [], "email": []}
    },
    {
        "msg": "Contact us at +91-98765-43210 or email help@fraud-bank.com",
        "expect": {"phone": ["9876543210"], "bank": [], "upi": [], "url": [], "email": ["help@fraud-bank.com"]}
    },
    {
        "msg": "Click https://sbi-netbanking.fake.co.in/login?ref=abc to verify",
        "expect": {"phone": [], "bank": [], "upi": [], "url": ["https://sbi-netbanking.fake.co.in/login?ref=abc"], "email": []}
    },
    {
        "msg": "UPI: scam.payment@ybl. Phone: (91) 8877665544",
        "expect": {"phone": ["8877665544"], "bank": [], "upi": ["scam.payment@ybl"], "url": [], "email": []}
    },
    {
        "msg": "Visit www.income-tax-refund.fake.in/claim and enter PAN",
        "expect": {"phone": [], "bank": [], "upi": [], "url": ["www.income-tax-refund.fake.in/claim"], "email": []}
    },
    {
        "msg": "Bank account: 1234-5678-9012-3456. UPI: refund@oksbi",
        "expect": {"phone": [], "bank": ["1234567890123456"], "upi": ["refund@oksbi"], "url": [], "email": []}
    },
    {
        "msg": "Whatsapp us at +91 87654 32109 or scan QR at http://bit.ly/fakescam",
        "expect": {"phone": ["8765432109"], "bank": [], "upi": [], "url": ["http://bit.ly/fakescam"], "email": []}
    },
    {
        "msg": "Email your Aadhaar to kyc.update@fake-govt.org. Account: 50100987654321",
        "expect": {"phone": [], "bank": ["50100987654321"], "upi": [], "url": [], "email": ["kyc.update@fake-govt.org"]}
    },
    {
        "msg": "Our officer will call from 08012345678. Transfer to premium.loan@fakebank",
        "expect": {"phone": ["8012345678"], "bank": [], "upi": ["premium.loan@fakebank"], "url": [], "email": []}
    },
    {
        "msg": "Send money to 9988776655@paytm and get cashback at https://cashback.fraud.com/claim?id=789",
        "expect": {"phone": [], "bank": [], "upi": ["9988776655@paytm"], "url": ["https://cashback.fraud.com/claim?id=789"], "email": []}
    },
    {
        "msg": "Your LIC policy payout: visit https://lic-maturity.fake.co.in. Call 1800-FAKE-LIC",
        "expect": {"phone": [], "bank": [], "upi": [], "url": ["https://lic-maturity.fake.co.in"], "email": []}
    },
    {
        "msg": "Customs duty payment: UPI customs.duty@fakegov, amount Rs3500",
        "expect": {"phone": [], "bank": [], "upi": ["customs.duty@fakegov"], "url": [], "email": []}
    },
    {
        "msg": "Job registration fee: transfer to HR@amazon-jobs-fake.com, a/c 11223344556677",
        "expect": {"phone": [], "bank": ["11223344556677"], "upi": [], "url": [], "email": ["HR@amazon-jobs-fake.com"]}
    },
    {
        "msg": "Bitcoin wallet: send to invest@crypto-gains.fake.io, call +91.9876.543.210",
        "expect": {"phone": ["9876543210"], "bank": [], "upi": [], "url": [], "email": ["invest@crypto-gains.fake.io"]}
    },
    {
        "msg": "Insurance claim: visit www.claim-insurance.fake.in/verify?policy=ABC123",
        "expect": {"phone": [], "bank": [], "upi": [], "url": ["www.claim-insurance.fake.in/verify?policy=ABC123"], "email": []}
    },
    {
        "msg": "Electricity bill overdue! Pay at mseb.bill@fakeutil or https://mseb-pay.fake.online/bill",
        "expect": {"phone": [], "bank": [], "upi": ["mseb.bill@fakeutil"], "url": ["https://mseb-pay.fake.online/bill"], "email": []}
    },
    {
        "msg": "Tax refund: email itr.refund@fake-incometax.gov.in, phone 9876 543 210",
        "expect": {"phone": ["9876543210"], "bank": [], "upi": [], "url": [], "email": ["itr.refund@fake-incometax.gov.in"]}
    },
    {
        "msg": "Subsidy transfer to 9871234567@okicici. Visit https://pm-kisan.fake.gov.in/apply",
        "expect": {"phone": [], "bank": [], "upi": ["9871234567@okicici"], "url": ["https://pm-kisan.fake.gov.in/apply"], "email": []}
    },
]

for i, tc in enumerate(EXTRACTION_TESTS, 1):
    sid = f"audit-extract-{i}-{uuid.uuid4().hex[:6]}"
    resp = send(sid, tc["msg"])

    if resp.status_code != 200:
        check(f"Msg {i}: HTTP 200", False, f"Got {resp.status_code}")
        print(f"  Msg {i:2d}: HTTP {resp.status_code} ERROR")
        continue

    data = resp.json()
    intel = data.get("extractedIntelligence", {})

    got_phone = set(intel.get("phoneNumbers", []))
    got_bank = set(intel.get("bankAccounts", []))
    got_upi = set(intel.get("upiIds", []))
    got_url = set(intel.get("phishingLinks", []) + intel.get("suspiciousLinks", []))
    got_email = set(intel.get("emailAddresses", []))

    exp = tc["expect"]
    missing = []

    for exp_p in exp["phone"]:
        if not any(exp_p in g for g in got_phone):
            missing.append(f"phone:{exp_p}")
    for exp_b in exp["bank"]:
        if not any(exp_b in g for g in got_bank):
            missing.append(f"bank:{exp_b}")
    for exp_u in exp["upi"]:
        if not any(exp_u.lower() in g.lower() for g in got_upi):
            missing.append(f"upi:{exp_u}")
    for exp_l in exp["url"]:
        if not any(exp_l.lower() in g.lower() for g in got_url):
            missing.append(f"url:{exp_l}")
    for exp_e in exp["email"]:
        if not any(exp_e.lower() in g.lower() for g in got_email):
            missing.append(f"email:{exp_e}")

    if missing:
        check(f"Msg {i}: extraction", False, f"MISSING: {missing}")
        print(f"  Msg {i:2d}: FAIL | missing={missing}")
        print(f"          got: phone={got_phone} bank={got_bank} upi={got_upi} url={got_url} email={got_email}")
    else:
        check(f"Msg {i}: extraction", True)
        print(f"  Msg {i:2d}: PASS | phone={got_phone} bank={got_bank} upi={got_upi} url={len(got_url)} email={got_email}")


# ============================================================
# PART 3: MULTI-TURN CONVERSATION HISTORY TEST
# ============================================================
print("\n" + "="*70)
print("PART 3: MULTI-TURN CONVERSATION HISTORY TEST")
print("="*70)

mt_sid = f"audit-multiturn-{uuid.uuid4().hex[:6]}"
mt_history = []
mt_planted = {
    1: {"sender": "scammer", "text": "Hello sir, I am calling from SBI. Call me back at +919876543210."},
    2: {"sender": "user", "text": "Oh really? What happened to my account?"},
    3: {"sender": "scammer", "text": "Your account is compromised. Send Rs 500 to verify@fakepaytm to verify."},
    4: {"sender": "user", "text": "Oh no! What should I do?"},
    5: {"sender": "scammer", "text": "Transfer your savings to safe account 12345678901234. Do it now!"},
    6: {"sender": "user", "text": "Okay, I am worried. How?"},
    7: {"sender": "scammer", "text": "Visit https://sbi-secure.fake.com/transfer to complete the process."},
    8: {"sender": "user", "text": "I am opening the link..."},
    9: {"sender": "scammer", "text": "Also email your ID proof to kyc@sbi-fake-dept.com for verification."},
}

# Build history up to turn 9
for turn in range(1, 10):
    mt_history.append(mt_planted[turn])

# Turn 10: send "hurry up" with full history
resp = send(mt_sid, "Hurry up! Time is running out! Send everything NOW!", history=mt_history)
data = resp.json()
intel = data.get("extractedIntelligence", {})

print(f"  Session: {mt_sid}")
print(f"  History turns sent: {len(mt_history)}")
print(f"  Intel extracted: {json.dumps(intel, indent=4)}")

mt_phone = set(intel.get("phoneNumbers", []))
mt_upi = set(intel.get("upiIds", []))
mt_bank = set(intel.get("bankAccounts", []))
mt_url = set(intel.get("phishingLinks", []) + intel.get("suspiciousLinks", []))
mt_email = set(intel.get("emailAddresses", []))

check("Multi-turn: phone from turn 1", any("9876543210" in p for p in mt_phone), f"got {mt_phone}")
check("Multi-turn: UPI from turn 3", any("verify@fakepaytm" in u.lower() for u in mt_upi), f"got {mt_upi}")
check("Multi-turn: bank from turn 5", any("12345678901234" in b for b in mt_bank), f"got {mt_bank}")
check("Multi-turn: URL from turn 7", any("sbi-secure.fake.com" in u.lower() for u in mt_url), f"got {mt_url}")
check("Multi-turn: email from turn 9", any("kyc@sbi-fake-dept.com" in e.lower() for e in mt_email), f"got {mt_email}")


# ============================================================
# PART 4: RESPONSE FORMAT PERFECTION TEST
# ============================================================
print("\n" + "="*70)
print("PART 4: RESPONSE FORMAT PERFECTION TEST")
print("="*70)

# Use the first extraction test response to check format
fmt_sid = f"audit-format-{uuid.uuid4().hex[:6]}"
resp = send(fmt_sid, "URGENT: Your SBI account compromised! Share OTP now! Call +919876543210.")
data = resp.json()
print(f"  Full response keys: {list(data.keys())}")
print(f"  Response: {json.dumps(data, indent=2, ensure_ascii=False)[:800]}")

# Required fields (15 pts)
check("Format: status=success", data.get("status") == "success", f"got {data.get('status')}")
check("Format: scamDetected present", "scamDetected" in data, f"keys={list(data.keys())}")
check("Format: scamDetected=true", data.get("scamDetected") == True, f"got {data.get('scamDetected')}")
check("Format: extractedIntelligence present", "extractedIntelligence" in data, f"keys={list(data.keys())}")

intel = data.get("extractedIntelligence", {})
check("Format: intel.phoneNumbers", "phoneNumbers" in intel, f"keys={list(intel.keys())}")
check("Format: intel.bankAccounts", "bankAccounts" in intel, f"keys={list(intel.keys())}")
check("Format: intel.upiIds", "upiIds" in intel, f"keys={list(intel.keys())}")
check("Format: intel.phishingLinks or suspiciousLinks",
      "phishingLinks" in intel or "suspiciousLinks" in intel, f"keys={list(intel.keys())}")
check("Format: intel.emailAddresses", "emailAddresses" in intel, f"keys={list(intel.keys())}")

# Optional fields (5 pts)
check("Format: engagementMetrics present", "engagementMetrics" in data, f"keys={list(data.keys())}")
metrics = data.get("engagementMetrics", {})
check("Format: totalMessagesExchanged", "totalMessagesExchanged" in metrics or "totalMessages" in metrics,
      f"metrics keys={list(metrics.keys())}")
check("Format: engagementDurationSeconds", "engagementDurationSeconds" in metrics or "engagementDuration" in metrics,
      f"metrics keys={list(metrics.keys())}")
check("Format: agentNotes present", "agentNotes" in data, f"keys={list(data.keys())}")
check("Format: reply present", "reply" in data and len(data.get("reply", "")) > 0, f"reply={data.get('reply', '')[:50]}")


# ============================================================
# PART 5: EDGE CASE STRESS TEST
# ============================================================
print("\n" + "="*70)
print("PART 5: EDGE CASE STRESS TEST (10 cases)")
print("="*70)

edge_tests = [
    {
        "name": "Empty message text",
        "payload": {"sessionId": f"edge1-{uuid.uuid4().hex[:6]}", "message": {"sender": "scammer", "text": "", "timestamp": 1234567890000}, "conversationHistory": [], "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}}
    },
    {
        "name": "Very long message (2000 chars)",
        "payload": {"sessionId": f"edge2-{uuid.uuid4().hex[:6]}", "message": {"sender": "scammer", "text": "URGENT: Your account has been compromised! " * 50, "timestamp": 1234567890000}, "conversationHistory": [], "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}}
    },
    {
        "name": "Unicode/emoji message",
        "payload": {"sessionId": f"edge3-{uuid.uuid4().hex[:6]}", "message": {"sender": "scammer", "text": "\U0001f6a8 URGENT! \u0906\u092a\u0915\u093e account block \u0939\u094b \u0917\u092f\u093e \u0939\u0948! \U0001f4de Call \u0915\u0930\u0947\u0902 +919876543210", "timestamp": 1234567890000}, "conversationHistory": [], "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}}
    },
    {
        "name": "Missing metadata field",
        "payload": {"sessionId": f"edge4-{uuid.uuid4().hex[:6]}", "message": {"sender": "scammer", "text": "Your account is blocked. Call now.", "timestamp": 1234567890000}, "conversationHistory": []}
    },
    {
        "name": "Timestamp as ISO string",
        "payload": {"sessionId": f"edge5-{uuid.uuid4().hex[:6]}", "message": {"sender": "scammer", "text": "Send money to fraud@paytm now.", "timestamp": "2025-02-11T10:00:00Z"}, "conversationHistory": [], "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}}
    },
    {
        "name": "Timestamp as epoch seconds",
        "payload": {"sessionId": f"edge6-{uuid.uuid4().hex[:6]}", "message": {"sender": "scammer", "text": "Your KYC expired. Update at https://fake-kyc.com", "timestamp": 1234567890}, "conversationHistory": [], "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}}
    },
    {
        "name": "Large conversationHistory (20 msgs)",
        "payload": {"sessionId": f"edge7-{uuid.uuid4().hex[:6]}", "message": {"sender": "scammer", "text": "Hurry up!", "timestamp": 1234567890000},
                    "conversationHistory": [{"sender": "scammer" if i%2==0 else "user", "text": f"Message {i}", "timestamp": 1234567890000+i*1000} for i in range(20)],
                    "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}}
    },
    {
        "name": "sessionId as integer",
        "payload": {"sessionId": 99999, "message": {"sender": "scammer", "text": "Pay Rs 5000 to scam@upi", "timestamp": 1234567890000}, "conversationHistory": [], "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}}
    },
    {
        "name": "Extra unexpected fields",
        "payload": {"sessionId": f"edge9-{uuid.uuid4().hex[:6]}", "message": {"sender": "scammer", "text": "Send OTP now!", "timestamp": 1234567890000}, "conversationHistory": [], "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}, "extraField": "should be ignored", "anotherField": 12345}
    },
    {
        "name": "Duplicate sessionId (reuse)",
        "payload": {"sessionId": fmt_sid, "message": {"sender": "scammer", "text": "I told you to send the OTP! Do it now!", "timestamp": 1234567890000}, "conversationHistory": [], "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}}
    },
]

for i, et in enumerate(edge_tests, 1):
    try:
        resp = requests.post(BASE_URL, json=et["payload"], headers=HEADERS, timeout=30)
        is_200 = resp.status_code == 200
        try:
            data = resp.json()
            is_json = True
            has_status = "status" in data
            has_reply = "reply" in data
        except:
            is_json = False
            has_status = False
            has_reply = False

        ok = is_200 and is_json and has_status and has_reply
        check(f"Edge {i}: {et['name']}", ok, f"HTTP {resp.status_code}, json={is_json}, status={has_status}, reply={has_reply}")
        status_icon = "PASS" if ok else "FAIL"
        print(f"  Edge {i:2d}: {status_icon} | {et['name']} | HTTP {resp.status_code}")
        if not ok:
            print(f"           Response: {resp.text[:200]}")
    except Exception as e:
        check(f"Edge {i}: {et['name']}", False, f"Exception: {e}")
        print(f"  Edge {i:2d}: EXCEPTION | {et['name']} | {str(e)[:80]}")


# ============================================================
# PART 7: ENGAGEMENT QUALITY VERIFICATION
# ============================================================
print("\n" + "="*70)
print("PART 7: ENGAGEMENT QUALITY VERIFICATION")
print("="*70)

eq_sid = f"audit-engagement-{uuid.uuid4().hex[:6]}"
eq_history = []
base_ts = 1771478000000  # epoch ms

# Build 9 turns of history spread over 2+ minutes
turns_data = [
    {"sender": "scammer", "text": "Your bank account has been compromised! Call +919876543210", "timestamp": base_ts},
    {"sender": "user", "text": "Oh no! What happened?", "timestamp": base_ts + 15000},
    {"sender": "scammer", "text": "Send Rs 500 to verify@paytm to secure your account", "timestamp": base_ts + 30000},
    {"sender": "user", "text": "Rs 500? Why?", "timestamp": base_ts + 45000},
    {"sender": "scammer", "text": "Transfer to account 12345678901234 immediately!", "timestamp": base_ts + 60000},
    {"sender": "user", "text": "I am scared! What account?", "timestamp": base_ts + 75000},
    {"sender": "scammer", "text": "Click https://sbi-fake.com/verify to complete", "timestamp": base_ts + 90000},
    {"sender": "user", "text": "Okay opening...", "timestamp": base_ts + 105000},
    {"sender": "scammer", "text": "Email ID proof to kyc@fake.com now! Time is running out!", "timestamp": base_ts + 130000},
]

for t in turns_data:
    eq_history.append(t)

# Turn 10
resp = send(eq_sid, "HURRY! Your account will be BLOCKED in 5 minutes!", history=eq_history,
            metadata={"channel": "SMS", "language": "English", "locale": "IN"})
data = resp.json()

print(f"  Session: {eq_sid}")
print(f"  History turns: {len(eq_history)}")
print(f"  Full response engagementMetrics: {json.dumps(data.get('engagementMetrics', {}), indent=4)}")

metrics = data.get("engagementMetrics", {})
duration = metrics.get("engagementDurationSeconds", metrics.get("engagementDuration", 0))
total_msgs = metrics.get("totalMessagesExchanged", metrics.get("totalMessages", 0))

print(f"  engagementDurationSeconds = {duration}")
print(f"  totalMessagesExchanged = {total_msgs}")

check("Engagement: duration > 0", duration > 0, f"got {duration}")
check("Engagement: duration > 60", duration > 60, f"got {duration}")
check("Engagement: totalMessages > 0", total_msgs > 0, f"got {total_msgs}")
check("Engagement: totalMessages >= 5", total_msgs >= 5, f"got {total_msgs}")


# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "="*70)
print("AUDIT SUMMARY (Parts 2, 3, 4, 5, 7)")
print("="*70)
print(f"Total tests: {total_tests}")
print(f"Passed:      {passed}")
print(f"Failed:      {failed}")
if issues:
    print(f"\nISSUES FOUND:")
    for iss in issues:
        print(f"  - {iss}")
else:
    print(f"\nNO ISSUES FOUND")
print("="*70)
