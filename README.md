# 🛡️ SHIELDCALL - AI-Powered Scam Detection Honeypot

> **India AI Impact Buildathon 2026** | Category: Agentic Honey-Pot

AI-powered honeypot system with 3-layer hybrid architecture that detects scams, engages scammers with dynamic personas, and extracts actionable intelligence.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![Railway](https://img.shields.io/badge/Deployed-Railway-blueviolet)](https://railway.app/)
[![Status](https://img.shields.io/badge/Status-Production-success)](https://reasonable-balance-production.up.railway.app/health)

## 🎯 Live Demo

**Production Endpoint:** https://reasonable-balance-production.up.railway.app/api/honeypot
**API Documentation:** https://reasonable-balance-production.up.railway.app/docs
**Health Check:** https://reasonable-balance-production.up.railway.app/health

## 🏆 Key Features

### 💡 3-Layer Hybrid AI Architecture (60-70% Cost Savings)
- **Layer 1:** OpenAI Whisper (Audio transcription)
- **Layer 2:** Google Gemini Flash (Quick risk screening - filters 60% of messages)
- **Layer 3:** Claude Sonnet 4 (Deep engagement with dynamic personas)

### 🎭 Dynamic Persona-Based Engagement
- **Elderly Person:** Confused, asks for verification, concerned about savings
- **Busy Professional:** Limited time, questions urgency, asks for official channels
- **Tech-Savvy Youth:** Questions authenticity, requests proof, security-conscious

### 📊 Real-Time Intelligence Extraction
- ✅ UPI IDs (`scammer@paytm`, `fraud@bank`)
- ✅ Phone numbers (+91-XXXXXXXXXX)
- ✅ Bank account numbers (9-18 digits)
- ✅ Phishing links
- ✅ Email addresses

### 🇮🇳 India-Specific Features
- Hindi/Hinglish language support
- UPI fraud pattern detection
- Banking scam recognition
- Local social engineering tactics

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| **Scam Detection Accuracy** | 90%+ |
| **Response Time** | <1s for 60% of messages |
| **Deep Analysis Time** | 5-7s (Claude) |
| **Cost Optimization** | 60-70% savings |
| **Intelligence Items Extracted** | 68+ (proven in production) |
| **GUVI Callbacks Sent** | 13 |
| **Sessions Processed** | 15+ |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Incoming Message                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Layer 1: Whisper    │ (Audio → Text if needed)
         │   Audio Transcription │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Layer 2: Gemini Flash│ (Quick Screening)
         │   Risk Assessment     │
         └───────────┬───────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
    ┌─────────┐          ┌─────────────┐
    │  LOW    │          │ MEDIUM/HIGH │
    │  RISK   │          │    RISK     │
    └────┬────┘          └──────┬──────┘
         │                      │
         ▼                      ▼
   ┌─────────────┐    ┌─────────────────────┐
   │   Neutral   │    │ Layer 3: Claude     │
   │   Response  │    │ Persona Engagement  │
   └─────────────┘    └──────────┬──────────┘
                                 │
                                 ▼
                   ┌──────────────────────────┐
                   │ Intelligence Extraction  │
                   │ + GUVI Callback          │
                   └──────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- API Keys: OpenAI, Anthropic Claude, Google Gemini

### Installation
```bash
# Clone repository
git clone https://github.com/rahul9871783107/SHIELDCALL-AI-Honeypot.git
cd SHIELDCALL-AI-Honeypot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
python -m uvicorn app.main:app --reload --port 8000
```

### Docker Deployment
```bash
# Build image
docker build -t shieldcall .

# Run container
docker run -p 8000:8000 --env-file .env shieldcall
```

## 📡 API Usage

### Test Scam Message
```bash
curl -X POST "https://reasonable-balance-production.up.railway.app/api/honeypot" \
  -H "x-api-key: hackathon-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-123",
    "message": {
      "sender": "scammer",
      "text": "URGENT: Your bank account compromised! Share OTP now!",
      "timestamp": 1770000000000
    }
  }'
```

### Response Example
```json
{
  "status": "success",
  "reply": "Oh my goodness, this is very concerning! I've been banking with SBI for over 30 years. Could you tell me which branch you're calling from and provide your employee ID number? I just want to be extra careful since this involves my life savings."
}
```

## 🧪 Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## 🔧 Tech Stack

- **Backend:** FastAPI 0.115
- **AI Models:**
  - OpenAI Whisper (audio transcription)
  - Google Gemini Flash 2.0 (screening)
  - Anthropic Claude Sonnet 4 (engagement)
- **Deployment:** Railway (Docker)
- **Testing:** Pytest
- **Documentation:** OpenAPI/Swagger

## 📊 Cost Optimization Strategy

**Traditional Approach (Single AI Model):**
- Every message → Claude Sonnet 4
- Cost: 100% of API calls at premium rates

**SHIELDCALL Hybrid Approach:**
- 60% filtered by Gemini Flash (low cost)
- 40% escalated to Claude Sonnet 4 (premium)
- **Result: 60-70% cost reduction while maintaining 90%+ accuracy**

## 🎓 Intelligence Extraction

Automatically detects and extracts:
```python
{
  "upiIds": ["scammer@paytm", "fraud@bank"],
  "phoneNumbers": ["+91-9876543210"],
  "bankAccounts": ["1234567890123456"],
  "phishingLinks": ["http://fake-bank.com"],
  "emails": ["help@scammer.com"]
}
```

**Automatically sends to GUVI when:**
- 2+ intelligence items extracted
- OR 15+ conversation turns completed

## 🏅 Hackathon Compliance

✅ GUVI endpoint validation: **PASSED**
✅ Authentication: API key based
✅ Response format: `{"status": "success", "reply": "..."}`
✅ Dynamic engagement: Claude-powered personas
✅ Intelligence extraction: Automatic callbacks
✅ Production deployment: Railway

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

## 👨‍💻 Author

**Rahul**
India AI Impact Buildathon 2026
Contact: rahul9871783107@gmail.com

## 🙏 Acknowledgments

- Anthropic Claude API
- Google Gemini API
- OpenAI Whisper
- GUVI & HCL for organizing the hackathon

---

**Built with ❤️ for India AI Impact Buildathon 2026**
