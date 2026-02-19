"""
SHIELDCALL Evaluation Simulator
Simulates 15 scam scenarios × 10 turns = 150 API calls.
Measures total time and checks for errors.
"""
import requests
import time
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://reasonable-balance-production.up.railway.app/api/honeypot"
API_KEY = "hackathon-secret-key-2026"
HEADERS = {"Content-Type": "application/json", "x-api-key": API_KEY}

# 15 scam scenarios matching evaluator types
SCENARIOS = [
    {"id": "bank_fraud", "msg": "URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately. Call +91-9876543210."},
    {"id": "upi_fraud", "msg": "Congratulations! You won Rs 50,000 Google Pay cashback! Send Rs 500 to verify@gpay to claim. Contact 8765432109 now."},
    {"id": "phishing_link", "msg": "Dear HDFC customer, your net banking is suspended. Reactivate at https://hdfc-secure-login.tk/verify or email support@hdfc-help.com"},
    {"id": "kyc_fraud", "msg": "Your Paytm KYC is expired. Update immediately or your wallet will be blocked. Send Aadhaar to kyc@paytm-update. Call 7654321098."},
    {"id": "job_scam", "msg": "Work from home! Earn Rs 50,000/month. No experience needed. Pay Rs 2,000 registration to jobs@quickhire. WhatsApp 6543210987."},
    {"id": "lottery_scam", "msg": "You won Rs 25 Lakhs in international lottery! Claim at www.lottery-claims.tk. Pay processing fee of Rs 10,000 to lottery@claim. Ref: 1234567890123."},
    {"id": "electricity_bill", "msg": "Your electricity bill is overdue Rs 5,432. Connection will be cut today. Pay now via UPI to ebill@bses or call 9871234567."},
    {"id": "govt_scheme", "msg": "PM Kisan Yojana: You are eligible for Rs 6,000. Register at https://pm-kisan-register.ml with bank account 12345678901234. Helpline 8901234567."},
    {"id": "crypto_invest", "msg": "Bitcoin investment opportunity! 300% returns guaranteed. Invest minimum Rs 25,000. Transfer to crypto@invest. Manager: Raj, call 7890123456."},
    {"id": "customs_parcel", "msg": "Your international parcel is held at customs. Pay Rs 3,500 duty to release. UPI: customs@duty. Tracking: 9876543210123456. Call 6789012345."},
    {"id": "tech_support", "msg": "Microsoft alert: Your computer has virus! Call tech support immediately at 9012345678. Visit www.ms-support-fix.ga to download security patch."},
    {"id": "loan_approval", "msg": "Pre-approved personal loan of Rs 5 Lakhs at 0% interest! Process now by sending docs to loan@quickbank. Processing fee Rs 1,999 to UPI: loan@process. Call 8123456789."},
    {"id": "income_tax", "msg": "Income Tax Department: Refund of Rs 15,600 pending. Verify bank account 98765432101234 at https://incometax-refund.cf/claim. Helpline 7012345678."},
    {"id": "refund_scam", "msg": "Your Amazon order refund of Rs 2,499 failed. Click https://amazon-refund.tk/process to retry. Send bank details to refund@amazon-help. Call 9123456780."},
    {"id": "insurance", "msg": "LIC policy maturity amount Rs 8,50,000 ready. Submit nomination to insurance@lic-claim. Pay stamp duty Rs 5,000 to lic@payment. Agent: 8234567890."},
]

def run_simulation():
    total_start = time.time()
    results = []
    errors = 0

    for scenario in SCENARIOS:
        session_id = f"eval-sim-{scenario['id']}"
        conversation_history = []

        print(f"\n{'='*60}")
        print(f"Scenario: {scenario['id']}")

        for turn in range(1, 11):
            # For turns > 1, use follow-up messages
            if turn == 1:
                msg_text = scenario["msg"]
            elif turn % 3 == 0:
                msg_text = "Please do it quickly, time is running out. Send the money to the account I gave you."
            elif turn % 3 == 1:
                msg_text = "Sir, this is very urgent. Your account/service will be blocked. Please cooperate."
            else:
                msg_text = "Yes yes, just follow my instructions. I am from the official department. Trust me."

            payload = {
                "sessionId": session_id,
                "message": {
                    "sender": "scammer",
                    "text": msg_text,
                    "timestamp": f"2025-02-11T10:{turn:02d}:00Z"
                },
                "conversationHistory": conversation_history,
                "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
            }

            turn_start = time.time()
            try:
                resp = requests.post(BASE_URL, json=payload, headers=HEADERS, timeout=30)
                turn_time = time.time() - turn_start

                if resp.status_code == 200:
                    data = resp.json()
                    reply = data.get("reply", "")
                    scam_detected = data.get("scamDetected", False)
                    intel = data.get("extractedIntelligence", {})
                    intel_count = sum(len(v) for k, v in intel.items() if k != "suspiciousKeywords")

                    agent_notes = data.get("agentNotes", "")
                    model = "gemini" if "gemini" in agent_notes.lower() else "haiku"

                    print(f"  Turn {turn:2d}: {turn_time:.1f}s | {model} | scam={scam_detected} | intel={intel_count} | reply={reply[:55]}...")

                    # Add to conversation history for next turn
                    conversation_history.append({"sender": "scammer", "text": msg_text})
                    conversation_history.append({"sender": "user", "text": reply})

                    results.append({"scenario": scenario["id"], "turn": turn, "time": turn_time, "status": "ok", "model": model})
                else:
                    print(f"  Turn {turn:2d}: ERROR {resp.status_code} in {turn_time:.1f}s")
                    errors += 1
                    results.append({"scenario": scenario["id"], "turn": turn, "time": turn_time, "status": f"error_{resp.status_code}"})

            except Exception as e:
                turn_time = time.time() - turn_start
                print(f"  Turn {turn:2d}: EXCEPTION {str(e)[:50]} in {turn_time:.1f}s")
                errors += 1
                results.append({"scenario": scenario["id"], "turn": turn, "time": turn_time, "status": "exception"})

    total_time = time.time() - total_start

    # Summary
    times = [r["time"] for r in results if r["status"] == "ok"]
    print(f"\n{'='*60}")
    print(f"SIMULATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total calls: {len(results)}")
    print(f"Successful: {len(times)}")
    print(f"Errors: {errors}")
    print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    print(f"Avg per turn: {sum(times)/len(times):.2f}s" if times else "N/A")
    print(f"Min turn: {min(times):.2f}s" if times else "N/A")
    print(f"Max turn: {max(times):.2f}s" if times else "N/A")
    print(f"Estimated 150 turns: {(sum(times)/len(times))*150/60:.1f} minutes" if times else "N/A")

    # Model breakdown
    gemini_count = sum(1 for r in results if r.get("model") == "gemini")
    haiku_count = sum(1 for r in results if r.get("model") == "haiku")
    print(f"\nModel breakdown:")
    print(f"  Gemini 2.0 Flash: {gemini_count}/{len(results)} ({gemini_count/len(results)*100:.0f}%)")
    print(f"  Claude Haiku fallback: {haiku_count}/{len(results)} ({haiku_count/len(results)*100:.0f}%)")

if __name__ == "__main__":
    run_simulation()
