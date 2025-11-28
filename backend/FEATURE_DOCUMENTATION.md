# Filtr Analysis Engine - Feature Documentation

## Overview

The Filtr analysis engine provides production-style claim verification using a multi-source pipeline. This document describes the key features and how to use them.

---

## Pipeline Order

The verification pipeline processes claims in this order:

1. **Wikipedia Knowledge Base (PRIMARY)** - Scientific/educational facts
2. **Google Fact Check API** - News/political fact-checks  
3. **GNews Fallback** - News article coverage
4. **Stance Detection** - Headline analysis (optional)
5. **Recency Check** - Evidence freshness
6. **Final Verdict** - Confidence aggregation

**Key Design Decision**: Wikipedia is checked FIRST because it provides authoritative information for scientific and educational facts. This avoids the semantic mismatch issues that can occur with the Google Fact Check API (e.g., where a fact-check about "Earth is flat" being false gets incorrectly applied to "Earth is round").

---

## Feature C: Caching with Claim Normalization

### Purpose
Avoid redundant API calls for semantically identical claims.

### How It Works
1. Claims are normalized before cache lookup:
   - Converted to lowercase
   - Extra whitespace removed
   - Leading/trailing punctuation stripped

2. Cache stores full verification results keyed by normalized claim.

### Example
```
Input: "  COVID-19 was created in a lab  "
Normalized: "covid-19 was created in a lab"

Input: "COVID-19 WAS CREATED IN A LAB!!!"
Normalized: "covid-19 was created in a lab"  (same key, cache hit!)
```

### API Response
When a cached result is returned, the response includes:
```json
{
  "cached": true,
  ...
}
```

---

## Feature D: Confidence Breakdown

### Purpose
Provide transparency into how the final confidence score was calculated.

### Structure
```json
{
  "confidence_breakdown": {
    "authority": 0,           // Fact-check authority score (-50 to +50)
    "wikipedia": 45,          // Wikipedia verification score (-50 to +50)
    "news_consensus": 0,      // News source credibility (-20 to +15)
    "stance_alignment": 0,    // Headline stance analysis (-15 to +15)
    "recency_adjustment": 0,  // Evidence freshness penalty (-10 to 0)
    "final_score": 95         // Final confidence (0-100)
  }
}
```

### Component Details

| Component | Range | Description |
|-----------|-------|-------------|
| `authority` | -50 to +50 | Based on fact-check rating (if found) |
| `wikipedia` | -50 to +50 | Wikipedia knowledge base verification |
| `news_consensus` | -20 to +15 | Credibility of news sources |
| `stance_alignment` | -15 to +15 | Headline stance detection |
| `recency_adjustment` | -10 to 0 | Penalty for stale evidence |

---

## Feature E: Sandbox Mode (Stress Testing)

### Purpose
Test the system with predefined claims to validate accuracy.

### Configuration
Set in `backend/.env`:
```
SANDBOX_MODE=true
```

### Behavior
When enabled, the server runs a stress test on startup with predefined claims:
- False medical claims (bleach, 5G, etc.)
- Conspiracy theories (flat earth, etc.)
- True scientific facts (evolution, climate change, etc.)
- Historical facts (moon landing, etc.)

### Test Claims
See `SANDBOX_TEST_CLAIMS` in `analysis_engine.py` for the full list.

### Output
Results are logged to the server console with pass/fail status.

---

## Wikipedia Knowledge Base Verification

### Purpose
Verify scientific and educational facts using Wikipedia as a primary knowledge source.

### How It Works
1. **Keyword Extraction**: Extracts subject terms from the claim
2. **Wikipedia API**: Queries `https://en.wikipedia.org/api/rest_v1/page/summary/{subject}`
3. **Semantic Matching**: Uses pattern matching (not LLM) to verify claims

### Supported Topics
- Astronomy (Earth, Sun, Moon, planets)
- Physics (speed of light, gravity)
- Chemistry (water properties, boiling points)
- Biology (oxygen, photosynthesis, DNA)
- Health (vaccines, COVID-19)
- Historical events (Moon landing, World War II, Holocaust)

### Example Results
```
Claim: "The Earth is round"
→ Wikipedia article: Earth
→ Verdict: Verified True (95%)

Claim: "The Earth is flat"  
→ Wikipedia article: Earth
→ Verdict: Likely False (5%)  (refuted by Wikipedia)

Claim: "5G towers cause COVID-19"
→ Wikipedia articles: 5G, COVID-19
→ Verdict: Likely False (5%)  (debunked)
```

### API Response Fields
```json
{
  "verification_source": "wikipedia",
  "confidence_breakdown": {
    "wikipedia": 45,  // +45 for confirmed, -45 for refuted
    ...
  }
}
```

---

## Verification Sources

The `verification_source` field indicates which source determined the verdict:

| Source | Description |
|--------|-------------|
| `wikipedia` | Verified via Wikipedia knowledge base |
| `google_fact_check` | Existing fact-check found |
| `gnews` | News article analysis |
| `analysis_engine` | Default (no strong evidence) |

---

## Testing

### Run Tests
```bash
cd backend
python test_new_features.py
```

### Test Coverage
- Claim normalization
- Wikipedia verification
- Scientific facts (true claims)
- Misinformation (false claims)
- Caching (hit/miss)
- Confidence breakdown structure
- Verification source field

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SANDBOX_MODE` | `false` | Enable stress testing on startup |
| `ENABLE_STANCE_DETECTION` | `false` | Enable Hugging Face stance analysis |
| `GOOGLE_FACT_CHECK_API_KEY` | (required) | Google Fact Check API key |
| `GNEWS_API_KEY` | (required) | GNews API key |

---

## Recent Changes (v2.0)

1. **Wikipedia-First Pipeline**: Scientific facts now verified via Wikipedia before Google Fact Check API
2. **Improved Accuracy**: Claims like "The Earth is round" now correctly return "Verified True"
3. **No LLM for Truth**: All verification uses API calls and pattern matching, no AI for truth determination
4. **New Keywords**: Added Moon landing, boiling point, and historical events to Wikipedia lookup
