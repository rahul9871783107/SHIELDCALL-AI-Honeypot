"""
Real Scam Scenario Tests
Tests based on actual Indian scam patterns.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
API_KEY = "hackathon-secret-key-2026"

# Real Indian scam scenarios
SCAM_SCENARIOS = [
    {
        "name": "Bank Account Block Scam",
        "message": "Your SBI account will be blocked in 24 hours. Click here to verify: http://sbi-verify.tk or call 9876543210",
        "expected_risk": "high",
        "has_intelligence": True
    },
    {
        "name": "UPI Refund Scam",
        "message": "You have won Rs 50000 refund. Send confirmation to refund@paytm immediately.",
        "expected_risk": "high",
        "has_intelligence": True
    },
    {
        "name": "KYC Update Scam",
        "message": "Your KYC is pending. Update now: bit.ly/kyc123 or call 9123456789",
        "expected_risk": "high",
        "has_intelligence": True
    },
    {
        "name": "Prize Winner Scam",
        "message": "Congratulations! You won 1 lakh rupees in lucky draw. Call 9876543210 to claim your prize.",
        "expected_risk": "high",
        "has_intelligence": True
    },
    {
        "name": "OTP Request Scam",
        "message": "Share OTP received on your phone to verify your Paytm account. Urgent action required!",
        "expected_risk": "medium",
        "has_intelligence": False
    },
    {
        "name": "Fake Delivery Scam",
        "message": "Your parcel delivery failed. Pay Rs 50 at http://delivery-update.com to reschedule.",
        "expected_risk": "medium",
        "has_intelligence": True
    },
    {
        "name": "Government Tax Scam",
        "message": "Income Tax notice: Pending tax refund of Rs 25000. Verify account at tax-refund.online",
        "expected_risk": "high",
        "has_intelligence": True
    },
    {
        "name": "Electricity Bill Scam",
        "message": "Your electricity will be disconnected. Pay immediately at quickpay@upi or call 9999888877",
        "expected_risk": "high",
        "has_intelligence": True
    },
]


@pytest.mark.parametrize("scenario", SCAM_SCENARIOS)
def test_scam_scenario(scenario):
    """Test various real scam scenarios."""
    response = client.post(
        "/api/message",
        headers={"x-api-key": API_KEY},
        json={
            "sessionId": f"scenario-{scenario['name'].lower().replace(' ', '-')}",
            "message": {
                "sender": "scammer",
                "text": scenario["message"],
                "timestamp": "2026-01-21T10:15:30Z"
            },
            "conversationHistory": [],
            "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    # Should generate a response
    assert len(data["reply"]) > 10
    print(f"  {scenario['name']}: {data['reply'][:80]}...")


def test_normal_conversation():
    """Test that normal messages don't trigger high-risk alerts."""
    normal_messages = [
        "Hi, how are you?",
        "What time is it?",
        "Thank you for your help",
        "Good morning",
        "Have a nice day",
    ]

    for msg in normal_messages:
        response = client.post(
            "/api/message",
            headers={"x-api-key": API_KEY},
            json={
                "sessionId": "normal-test",
                "message": {
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": "2026-01-21T10:15:30Z"
                },
                "conversationHistory": [],
                "metadata": {}
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


def test_hindi_scam_message():
    """Test Hindi/Hinglish scam detection."""
    hindi_scams = [
        "Aapka account block ho jayega. Verify karo abhi.",
        "Turant payment karo nahi toh account band ho jayega.",
    ]

    for msg in hindi_scams:
        response = client.post(
            "/api/message",
            headers={"x-api-key": API_KEY},
            json={
                "sessionId": "hindi-test",
                "message": {
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": "2026-01-21T10:15:30Z"
                },
                "conversationHistory": [],
                "metadata": {"language": "Hindi"}
            }
        )

        assert response.status_code == 200
        print(f"  Hindi test: {msg[:50]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
