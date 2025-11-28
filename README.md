# 🛡️ Filtr — AI-Powered Fact Checking System

**Filtr** (formerly Aletheia Sentinel) is a comprehensive fact-checking platform that combines multiple verification sources to provide accurate, confidence-scored verdicts on claims. Built with React + Vite frontend and FastAPI backend.

---

## 🚀 Quick Start

**New to the project?** Start here:
1. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete installation instructions
2. **[.env.example](.env.example)** - Configuration template
3. **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - Pre-deployment verification

---

## ✨ Features

### 🔍 Multi-Source Verification
- **Google Fact Check API** - Primary verification source for existing fact-checks
- **Wikipedia Integration** - Validates scientific and educational claims
- **GNews API** - Real-time news article verification with credibility scoring
- **Smart Query Extraction** - Optimizes searches by extracting key entities from long claims

### 🧠 Advanced AI Analysis
- **Google Gemini AI** - Sophisticated claim analysis and reasoning
- **Multi-Source Confidence Scoring** - Aggregates evidence from multiple sources
- **Claim Type Classification** - Routes to appropriate verification method (scientific, news, political)
- **Stance Detection** (Optional) - Analyzes article agreement with claims
- **Recency Scoring** - Adjusts confidence based on source freshness

### 📊 Transparent Results
- **0-100% Confidence Scores** - Clear, quantified verification strength
- **Detailed Explanations** - Step-by-step reasoning breakdown
- **Source Attribution** - Full citation of verification sources
- **Confidence Breakdown** - Individual scoring components displayed
- **Verification Path Tracking** - Shows which APIs were consulted

---

## 📁 Project Structure

```
Filtr/
├── src/                      # React + Vite Frontend
│   ├── components/           # UI components
│   │   ├── analysis/         # Claim analysis components
│   │   ├── dashboard/        # Dashboard widgets
│   │   └── global/           # Shared components
│   ├── pages/                # Route pages
│   ├── services/             # API clients
│   └── hooks/                # Custom React hooks
│
├── backend/                  # FastAPI Backend
│   └── app/
│       ├── routers/          # API endpoints
│       ├── services/         # Core logic
│       │   ├── analysis_engine.py    # Main verification pipeline
│       │   ├── fact_checker.py       # Google Fact Check integration
│       │   ├── gnews_service.py      # News article search
│       │   ├── llm_agent.py          # Gemini AI integration
│       │   └── vector_store.py       # (Optional) Pinecone integration
│       └── main.py           # FastAPI app
│
├── .env.example              # Environment template (root)
├── backend/.env.example      # Backend environment template
├── SETUP_GUIDE.md            # Complete setup instructions
├── PRODUCTION_CHECKLIST.md   # Deployment readiness checklist
└── AUDIT_SUMMARY.md          # Latest code review summary
```

---

## ⚙️ Technology Stack

### Frontend
- **React 19** - UI framework
- **Vite** - Build tool and dev server
- **TailwindCSS** - Styling
- **Recharts** - Data visualization
- **Lucide React** - Icons

### Backend
- **FastAPI** - Web framework
- **Python 3.11+** - Runtime
- **Google Gemini** - LLM analysis
- **httpx** - Async HTTP client
- **SQLAlchemy** - Database ORM (optional)

### APIs & Services
- **Google Fact Check Tools API** - Fact verification
- **GNews API** - News article search
- **Google Gemini API** - AI analysis
- **Wikipedia** - Knowledge base (via direct HTTP)
- **Pinecone** (Optional) - Vector search
- **Neo4j** (Optional) - Graph database

---

## 🔧 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Quick Setup
```bash
# 1. Clone repository
git clone <repo-url>
cd Filtr_Working_Without_Logs

# 2. Configure environment
cp .env.example .env
# Edit .env and add your API keys

# 3. Install backend dependencies
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r backend/requirements.txt

# 4. Install frontend dependencies
npm install
```

### Required API Keys
Get these API keys before running:
1. **Google Fact Check API** - https://console.cloud.google.com/apis/credentials
2. **GNews API** - https://gnews.io/
3. **Google Gemini API** - https://makersuite.google.com/app/apikey

Add them to `.env`:
```env
GOOGLE_FACT_CHECK_API_KEY=your_key_here
GNEWS_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

**For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

---

## 🚀 Running the Application

### Development Mode

**Backend:**
```bash
# Activate virtual environment first
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Start backend server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend runs at: http://localhost:8000

**Frontend:**
```bash
# In a new terminal
npm run dev
```
Frontend runs at: http://localhost:5173

### Production Build
```bash
# Build frontend
npm run build

# Serve static files from dist/
# Deploy backend with: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

---

## 📡 API Endpoints

### Main Analysis Endpoint
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "claim": "The Earth is round"
}
```

**Response:**
```json
{
  "status": "completed",
  "claim": "The Earth is round",
  "verdict": "Verified True",
  "final_verdict": "Verified True",
  "confidence": 95,
  "claim_type": "scientific",
  "explanation": ["Step 1...", "Step 2..."],
  "sources": ["https://en.wikipedia.org/wiki/Earth"],
  "publisher": ["Wikipedia"],
  "published_dates": [],
  "verification_path": ["wikipedia", "google_fact_check"],
  "confidence_breakdown": {
    "authority": 45,
    "wikipedia": 50,
    "news_consensus": 0,
    "stance_alignment": 0,
    "recency_adjustment": 0,
    "final_score": 95
  },
  "last_checked": "2025-11-27T..."
}
```

### Other Endpoints
- `GET /health` - Health check
- `POST /api/v1/fact-check` - Direct Google Fact Check query
- `POST /api/v1/clear-cache` - Clear verification cache
- `WS /ws/threats` - Real-time threat alerts (demo)

---

## 🧪 Testing

### Manual Tests
```bash
# Test with curl
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"claim":"Earth is round"}'

# Health check
curl http://localhost:8000/health
```

### Test Cases
1. **Scientific Claim:** "Water boils at 100°C" → Should return 80-95% confidence
2. **News Claim:** "Recent election results" → Should find articles (if GNews quota available)
3. **False Claim:** "5G causes COVID-19" → Should return low confidence with debunking sources
4. **Ambiguous:** "Politicians are corrupt" → Should return ~50% with nuanced explanation

---

## 🔒 Security

- ✅ **No hardcoded API keys** - All secrets in environment variables
- ✅ **CORS configured** - Update for production domain
- ✅ **Input validation** - Pydantic schemas validate requests
- ✅ **Error handling** - Graceful failures, no data leaks
- ⚠️ **Rate limiting** - Not implemented (add for production)

**Before deploying:** Review [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)

---

## 📊 Confidence Scoring System

### Scoring Components
- **Authority Score** (0-50): Google Fact Check rating
- **Wikipedia Score** (0-50): Scientific claim verification
- **News Consensus** (0-50): Multi-source agreement (3+ sources = 80-85%)
- **Stance Alignment** (0-50): Article-claim agreement
- **Recency** (-10 to +10): Source freshness adjustment

### Verdict Thresholds
- **85-100%**: Verified True
- **70-84%**: Likely True  
- **40-69%**: Unverified / Needs More Evidence
- **0-39%**: Likely False

---

## 🌐 Deployment

### Backend (Render/Railway/Fly.io)
```bash
# Docker deployment
docker build -t filtr-backend -f backend/Dockerfile .
docker run -p 8000:8000 --env-file .env filtr-backend
```

### Frontend (Vercel/Netlify)
```bash
npm run build
# Deploy dist/ directory
```

**Environment Variables for Production:**
```env
# Frontend
VITE_API_URL=https://your-api-domain.com/api/v1
VITE_API_BASE=https://your-api-domain.com
VITE_API_WS=wss://your-api-domain.com/ws/threats

# Backend (same API keys as development)
GOOGLE_FACT_CHECK_API_KEY=prod_key
GNEWS_API_KEY=prod_key
GEMINI_API_KEY=prod_key
```

---

## ⚠️ Known Limitations

1. **GNews Free Tier**: 100 requests/day
   - When exhausted, news claims default to 50% confidence
   - Google Fact Check and Wikipedia still work
   
2. **Transformers Optional**: Stance detection requires ~2GB library
   - Install with: `pip install transformers torch`
   - Improves accuracy by 5-15%

3. **No Rate Limiting**: Backend accepts unlimited requests
   - Add rate limiting for production deployment

---

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete installation and configuration
- **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - Pre-deployment verification
- **[AUDIT_SUMMARY.md](AUDIT_SUMMARY.md)** - Latest code review findings
- **[.env.example](.env.example)** - Configuration template
- **[DEPLOYMENT_READY.md](DEPLOYMENT_READY.md)** - Deployment notes (if exists)

---

## 🤝 Contributing

This is a hackathon prototype. For production use:
1. Review PRODUCTION_CHECKLIST.md
2. Add comprehensive tests
3. Implement rate limiting
4. Add monitoring/analytics
5. Set up CI/CD pipeline

---

## 📝 License

[Add your license here]

---

## 👥 Team

**Made by OptiMl**

- Project Type: Hackathon Prototype
- Status: Production-Ready (with proper configuration)
- Last Updated: November 27, 2025

---

## 🙏 Acknowledgments

- Google Fact Check Tools API
- GNews API
- Google Gemini
- Wikipedia
- React, FastAPI, and the open-source community

---

**For support and setup help, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

