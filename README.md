Here is a complete, polished **README.md** for your GitHub repository — structured clearly, professional, and competition-ready.

---

# 📌 Filtr – AI-Driven Misinformation & News Verification Engine

Filtr is an intelligent misinformation-detection system designed to analyze claims, verify news authenticity, flag false information, and provide evidence-based breakdowns using automated fact-checking pipelines.
This project aims to reduce confusion during high-information events such as pandemics, elections, climate crises or viral online rumors — empowering users to quickly judge credibility with clarity.

---

## 🔥 Key Functionalities

| Feature                                        | Description                                                                                      |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| 🧠 Claim Verification Engine                   | Classifies input into *News / Scientific / Unknown* and runs domain-specific verification routes |
| 🌍 Multi-Source News Cross-Check               | GNews → NewsAPI fallback with confidence scoring based on publisher credibility + recency        |
| 📚 Wikipedia-Based Scientific Validation       | Semantic match system verifies or refutes science claims without an LLM                          |
| 🏛 Google Fact-Check Integration               | Detects published fact-checks, ratings & verdicts from global fact-checking organizations        |
| 📊 Confidence Breakdown Scoring                | Transparent score justification: authority, consensus, recency, alignment & more                 |
| 📈 Strategy Intelligence Module                | Provides pattern signals & misinformation threat assessment                                      |
| 📰 Web-Scraper + Daily Summary (Branch merged) | Headlines scraper + summarized daily updates                                                     |
| 💾 12-Hour Smart Cache                         | Storage layer improving speed & avoiding repeated API load                                       |
| 🔐 2-Factor Login Auth Support                 | (From param3 branch)                                                                             |

---

## 🏗 Architecture Overview

```
Filtr
 ├── Claim Analyzer (Core Engine)
 │    ├── Google Fact Check
 │    ├── Wikipedia Knowledge Base
 │    ├── GNews → NewsAPI fallback
 │    ├── Consensus Confidence Ranking System
 │    └── Verdict Engine
 ├── Frontend + UI Dashboard
 ├── Strategy Tab (Signal & Pattern Insights)
 ├── Web-Scraper + Daily Briefings
 └── Caching + DB Results Store
```

---

## 🚀 How To Run

### 1. Clone Repository

```bash
git clone https://github.com/yourrepo/filtr.git
cd filtr
```

### 2. Setup Backend

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### 3. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 📡 API Endpoints

| Method               | Route                                       | Purpose |
| -------------------- | ------------------------------------------- | ------- |
| `POST /verify`       | Analyzes claim & returns truthfulness score |         |
| `GET /daily-summary` | Returns summary from scraper module         |         |
| `GET /history`       | Cached verification logs                    |         |

Sample request:

```json
{
  "claim": "India launched a new lunar rover in 2025"
}
```

---

## 📊 Output Response Example

```json
{
  "verdict": "Likely True",
  "confidence": 82,
  "sources": ["Reuters", "The Hindu", "BBC"],
  "explanation": [
    "Multiple independent outlets confirm the event",
    "Evidence is recent",
    "Premium credibility score boost applied"
  ]
}
```

---

## 🧩 Branch Merge Summary

| Branch                | Adopted Components                                  |
| --------------------- | --------------------------------------------------- |
| **Bhavya**            | Analysis engine + verification system               |
| **param3**            | Web-scraper + 2FA + daily summary                   |
| **Vedant**            | Strategy tab backend + UI only for strategy section |
| **integration-final** | All core systems combined cleanly                   |

---

## 🎯 Project Goal Alignment

Filtr directly addresses misinformation outbreaks by:

✔ Scanning multiple news sources
✔ Comparing cross-publisher evidence
✔ Detecting false or unsupported claims
✔ Presenting digestible, non-technical verdicts

Designed specifically for high-noise situations where citizens struggle to trust information — exactly fitting the misinformation problem statement.

---

## 🤝 Contributors

| Name   | Roles                               |
| ------ | ----------------------------------- |
| Vedant | Strategy Engine + Core Integrations |
| Bhavya | Core Analysis + UI                  |
| Param  | Web Scraper + 2FA + Summary Feeds   |

---
