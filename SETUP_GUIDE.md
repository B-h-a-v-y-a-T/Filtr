# 🚀 Filtr - Complete Setup Guide

This document provides complete setup instructions for the Filtr fact-checking application.

## 📋 Prerequisites

### Required Software
- **Python 3.11+** (with pip)
- **Node.js 18+** (with npm)
- **Git** (for cloning repository)

### Required API Keys
You need to obtain the following API keys before running the application:

1. **Google Fact Check API Key** (Required)
   - Get it at: https://console.cloud.google.com/apis/credentials
   - Enable the Fact Check Tools API

2. **GNews API Key** (Required)
   - Get it at: https://gnews.io/
   - Free tier: 100 requests/day

3. **Google Gemini API Key** (Required)
   - Get it at: https://makersuite.google.com/app/apikey
   - Used for AI-powered verification

### Optional Dependencies
- **Transformers + PyTorch** (for advanced stance detection)
- **Pinecone** (for vector search)
- **Neo4j** (for knowledge graph features)

---

## 🔧 Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Filtr_Working_Without_Logs
```

### 2. Backend Setup

#### Create Python Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### Install Python Dependencies
```bash
pip install -r backend/requirements.txt
```

#### Optional: Install Transformers (for stance detection)
```bash
# This adds ~2GB of dependencies
pip install transformers torch sentencepiece
```

### 3. Frontend Setup

#### Install Node Dependencies
```bash
npm install
```

### 4. Environment Configuration

#### Create Root .env File
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API keys
notepad .env  # Windows
nano .env     # macOS/Linux
```

**Required Configuration in .env:**
```env
# Required API Keys
GOOGLE_FACT_CHECK_API_KEY=your_actual_google_api_key
GNEWS_API_KEY=your_actual_gnews_api_key
GEMINI_API_KEY=your_actual_gemini_api_key

# Frontend URLs (defaults are fine for local development)
VITE_API_URL=http://localhost:8000/api/v1
VITE_API_BASE=http://localhost:8000
VITE_API_WS=ws://localhost:8000/ws/threats
```

#### Optional: Create Backend .env (if needed)
```bash
cp backend/.env.example backend/.env
# Add the same API keys to backend/.env
```

---

## 🚀 Running the Application

### Start Backend Server
```bash
# Make sure virtual environment is activated
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# Run backend
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### Start Frontend Development Server
```bash
# In a new terminal window
npm run dev
```

Frontend will be available at: http://localhost:5173

---

## 🧪 Testing the Application

### 1. Health Check
Visit: http://localhost:8000/health

Should return: `{"status":"ok"}`

### 2. Test Analysis
1. Open: http://localhost:5173/analyze
2. Enter a claim: "The Earth is round"
3. Click "Analyze"
4. You should see a verification result with confidence score

### 3. Test Different Claim Types

#### Scientific Claim (Wikipedia verification)
```
"Water boils at 100 degrees Celsius at sea level"
```

#### News Claim (GNews + Fact Check)
```
"New climate agreement signed at COP28"
```

#### False Claim (Fact Check debunking)
```
"5G towers cause coronavirus"
```

---

## 🔍 Troubleshooting

### Backend Won't Start

**Error: "transformers" could not be resolved**
- This is a warning, not an error. The app will work fine without transformers.
- To fix: `pip install transformers torch` (optional, adds 2GB)

**Error: API key not configured**
- Check that your .env file exists in the root directory
- Verify API keys are not wrapped in quotes
- Restart the backend server after changing .env

### Frontend Won't Connect to Backend

**Error: Failed to fetch**
- Ensure backend is running on port 8000
- Check firewall settings
- Verify VITE_API_URL in .env matches backend URL

### GNews API Quota Exhausted

**Error: 403 Forbidden from GNews**
- GNews free tier: 100 requests/day
- Wait 24 hours for quota reset
- OR upgrade to paid plan at https://gnews.io/
- System will fall back to Google Fact Check only

### Low Confidence Scores

**Claims returning ~50% confidence**
- GNews quota may be exhausted (no news articles found)
- Try scientific claims (Wikipedia-based) instead
- Check that claim is newsworthy and recent

---

## 📦 Production Deployment

### Build Frontend
```bash
npm run build
```

This creates optimized static files in `dist/` directory.

### Environment Variables for Production
```env
# Use production URLs
VITE_API_URL=https://your-api-domain.com/api/v1
VITE_API_BASE=https://your-api-domain.com
VITE_API_WS=wss://your-api-domain.com/ws/threats

# Backend .env should have production API keys
GOOGLE_FACT_CHECK_API_KEY=prod_key
GNEWS_API_KEY=prod_key
GEMINI_API_KEY=prod_key

# Disable debug features
SANDBOX_MODE=false
ENABLE_STANCE_DETECTION=false
```

### Security Checklist
- [ ] Never commit .env files to version control
- [ ] Use environment variables for all API keys
- [ ] Enable HTTPS for production
- [ ] Set proper CORS origins in backend
- [ ] Rate limit API endpoints
- [ ] Monitor API usage and costs

---

## 🎯 Feature Configuration

### Enable Advanced Stance Detection
Requires ~2GB of ML models. Provides +5-15% confidence improvement.

```env
ENABLE_STANCE_DETECTION=true
```

```bash
pip install transformers torch sentencepiece
```

### Enable Vector Search (Pinecone)
For semantic similarity search across claims.

```env
ENABLE_PINECONE=true
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=aletheia
```

### Enable Knowledge Graph (Neo4j)
For entity relationship tracking.

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

---

## 📚 API Documentation

### Analyze Endpoint
```
POST /api/v1/analyze
Content-Type: application/json

{
  "claim": "string - The claim to verify"
}
```

**Response:**
```json
{
  "status": "completed",
  "claim": "string",
  "verdict": "Verified True|Likely True|Unverified|Likely False",
  "final_verdict": "same as verdict",
  "confidence": 0-100,
  "claim_type": "scientific|news|political|unknown",
  "explanation": ["array", "of", "reasoning", "steps"],
  "sources": ["url1", "url2"],
  "publisher": ["Source 1", "Source 2"],
  "published_dates": ["ISO timestamp"],
  "verification_path": ["google_fact_check", "wikipedia", "gnews"],
  "confidence_breakdown": {
    "authority": 0-50,
    "wikipedia": 0-50,
    "news_consensus": 0-50,
    "stance_alignment": 0-50,
    "recency_adjustment": -10 to +10,
    "final_score": 0-100
  },
  "last_checked": "ISO timestamp"
}
```

### Clear Cache Endpoint
```
POST /api/v1/clear-cache
```

Clears the in-memory verification cache. Useful for testing.

---

## 🐛 Known Issues

### Issue: GNews Rate Limiting
**Symptom:** News claims return 50% confidence
**Cause:** GNews free tier limited to 100 requests/day
**Fix:** Wait for quota reset or upgrade plan

### Issue: Transformers Import Error
**Symptom:** Warning about "transformers" module
**Cause:** Optional dependency not installed
**Fix:** Install with `pip install transformers torch` OR ignore (non-critical)

### Issue: Backend Shuts Down on Request
**Symptom:** Backend stops after API call
**Cause:** Usually environment or dependency issue
**Fix:** Check logs, verify all dependencies installed

---

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review backend logs for error messages
3. Check browser console for frontend errors
4. Verify all API keys are valid and have quota
5. Ensure all dependencies are installed

---

## 🎉 Success Indicators

Your setup is working correctly if:
- ✅ Backend health check returns `{"status":"ok"}`
- ✅ Scientific claims (e.g., "Earth is round") return 80-95% confidence
- ✅ News claims return articles with sources (when GNews quota available)
- ✅ False claims are correctly flagged with low confidence
- ✅ Frontend displays confidence scores and explanations
- ✅ Radar chart shows dynamic values (not hardcoded)

---

Made by OptiMl
