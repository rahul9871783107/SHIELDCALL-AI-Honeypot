"""
Complete Flow Tests - End-to-End Testing
Tests realistic scam scenarios through the entire pipeline.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# API key for testing
API_KEY = "hackathon-secret-key-2026"


def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "SHIELDCALL" in data["service"]


def test_root_endpoint():
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "SHIELDCALL" in data["service"]
    assert "architecture" in data


def test_authentication_required():
    """Test that endpoints require authentication."""
    response = client.post("/api/message", json={
        "sessionId": "test",
        "message": {"sender": "scammer", "text": "test", "timestamp": "2026-01-21T10:15:30Z"},
        "conversationHistory": [],
        "metadata": {}
    })
    assert response.status_code == 401


def test_authentication_invalid_key():
    """Test invalid API key is rejected."""
    response = client.post(
        "/api/message",
        headers={"x-api-key": "wrong-key"},
        json={
            "sessionId": "test",
            "message": {"sender": "scammer", "text": "test", "timestamp": "2026-01-21T10:15:30Z"},
            "conversationHistory": [],
            "metadata": {}
        }
    )
    assert response.status_code == 401


def test_low_risk_message():
    """Test low-risk message processing."""
    response = client.post(
        "/api/message",
        headers={"x-api-key": API_KEY},
        json={
            "sessionId": "low-risk-test",
            "message": {
                "sender": "scammer",
                "text": "Hello, how are you today?",
                "timestamp": "2026-01-21T10:15:30Z"
            },
            "conversationHistory": [],
            "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "reply" in data
    assert len(data["reply"]) > 0


def test_high_risk_scam_detection():
    """Test high-risk scam message detection."""
    response = client.post(
        "/api/message",
        headers={"x-api-key": API_KEY},
        json={
            "sessionId": "high-risk-test",
            "message": {
                "sender": "scammer",
                "text": "URGENT! Your bank account will be BLOCKED! Verify OTP immediately at http://fake-bank.com",
                "timestamp": "2026-01-21T10:15:30Z"
            },
            "conversationHistory": [],
            "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["reply"]) > 0


def test_intelligence_extraction():
    """Test intelligence extraction from scam message."""
    response = client.post(
        "/api/message",
        headers={"x-api-key": API_KEY},
        json={
            "sessionId": "intel-test",
            "message": {
                "sender": "scammer",
                "text": "Send payment to 9876543210 or UPI verify@paytm. Account: 123456789012",
                "timestamp": "2026-01-21T10:15:30Z"
            },
            "conversationHistory": [],
            "metadata": {}
        }
    )

    assert response.status_code == 200

    # Check stats for intelligence
    stats_response = client.get("/api/stats", headers={"x-api-key": API_KEY})
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["total_intelligence_extracted"] > 0


def test_multi_turn_conversation():
    """Test multi-turn conversation handling."""
    session_id = "multi-turn-test"

    # First message
    response1 = client.post(
        "/api/message",
        headers={"x-api-key": API_KEY},
        json={
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": "Your account is blocked!",
                "timestamp": "2026-01-21T10:15:30Z"
            },
            "conversationHistory": [],
            "metadata": {}
        }
    )
    assert response1.status_code == 200

    # Second message with history
    response2 = client.post(
        "/api/message",
        headers={"x-api-key": API_KEY},
        json={
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": "Send OTP to verify",
                "timestamp": "2026-01-21T10:16:30Z"
            },
            "conversationHistory": [
                {
                    "sender": "scammer",
                    "text": "Your account is blocked!",
                    "timestamp": "2026-01-21T10:15:30Z"
                },
                {
                    "sender": "user",
                    "text": "What should I do?",
                    "timestamp": "2026-01-21T10:15:45Z"
                }
            ],
            "metadata": {}
        }
    )
    assert response2.status_code == 200


def test_stats_endpoint():
    """Test stats endpoint."""
    response = client.get("/api/stats", headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert "total_sessions" in data
    assert "hybrid_ai_system" in data
    assert data["hybrid_ai_system"]["claude_enabled"] is True
    assert "scam_sessions" in data
    assert "total_intelligence_extracted" in data


def test_stats_requires_auth():
    """Test stats endpoint requires authentication."""
    response = client.get("/api/stats")
    assert response.status_code == 401


def test_cleanup_endpoint():
    """Test cleanup endpoint."""
    response = client.post("/api/cleanup", headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "sessions_removed" in data
    assert "active_sessions" in data


def test_invalid_request_format():
    """Test handling of invalid request format."""
    response = client.post(
        "/api/message",
        headers={"x-api-key": API_KEY},
        json={
            "sessionId": "invalid-test",
            # Missing required 'message' field
            "conversationHistory": []
        }
    )
    assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
