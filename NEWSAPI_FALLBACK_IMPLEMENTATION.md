# NewsAPI Fallback Implementation

## Summary
Implemented a robust fallback system where NewsAPI automatically takes over when GNews quota is exceeded, ensuring uninterrupted news verification functionality.

## Changes Made

### 1. New File: `backend/app/services/newsapi_service.py`
**Purpose**: NewsAPI service provider with same interface as GNews

**Key Functions**:
- `search_newsapi(query, max_results=10, language="en")` - Main search function
- `extract_search_query(claim, max_words=5)` - Query optimization (same as GNews)
- `_process_newsapi_response(data, query)` - Converts NewsAPI format to GNews-compatible format

**Features**:
- Same interface as GNews for seamless fallback
- Returns unified format: `{has_articles, articles, summary, total_found}`
- Proper error handling for 429 (rate limit), 401 (auth), 5xx errors
- Query extraction and simplification for better results

**NewsAPI Configuration**:
- Endpoint: `https://newsapi.org/v2/everything`
- Parameters: `q`, `apiKey`, `language=en`, `pageSize=10`, `sortBy=publishedAt`
- Requires `NEWSAPI_KEY` in `.env`

---

### 2. Modified: `backend/app/services/analysis_engine.py`

#### A. New Unified Interface: `get_news_results(query, max_results=10)`
**Purpose**: Automatic failover between GNews and NewsAPI

**Flow**:
```
1. Try GNews (primary)
   ↓ (if 429, 401, 5xx, timeout, empty)
2. Fallback to NewsAPI
   ↓
3. Return unified format
```

**Return Format**:
```python
{
    "has_articles": bool,
    "articles": [...],
    "summary": str,
    "total_found": int,
    "news_provider_used": "gnews" | "newsapi" | "none"  # NEW
}
```

#### B. Updated `analyze_claim()` Function
**Changes**:
1. Added `news_provider = "none"` tracking variable
2. Replaced all `search_gnews()` calls with `get_news_results()`
3. Added provider logging: `"→ Using GNEWS as news provider"` or `"→ Using NEWSAPI as news provider"`
4. Updated verification paths: `"gnews"` → `"news_search"`

**Provider Tracking**:
- Scientific claims: Falls back to news after Wikipedia/Google
- News claims: Uses news as primary after Google fact-check
- Unknown claims: Uses news after Google fact-check
- All paths track which provider succeeded via `news_provider_used`

#### C. Enhanced Error Handling
**When both providers fail**:
```python
confidence = 47  # Slightly below neutral
verdict = "Unverified / Needs More Evidence"
explanation = "News providers temporarily unavailable; cannot verify claim"
news_provider_used = "none"
```

**NOT marked as false** - adheres to requirement F.

#### D. Updated Response Schema
All analysis responses now include:
```python
{
    ...existing fields...,
    "news_provider_used": "gnews" | "newsapi" | "none"  # NEW
}
```

---

### 3. Modified: `.env`
**Added**:
```env
# News API Keys
# GNEWS_API_KEY=your_gnews_api_key_here
# NEWSAPI_KEY=your_newsapi_key_here
```

Users must add their own API keys.

---

## Implementation Details

### Failover Triggers
NewsAPI is used when GNews experiences:
- ✅ 429 (Rate Limit)
- ✅ 401 (Quota/Auth Issue)
- ✅ 5xx Server Errors
- ✅ Empty Response After Retry
- ✅ Timeout

### Unified Article Format
Both providers return:
```python
{
    "title": str,
    "description": str,
    "url": str,
    "source": str,  # Publisher name
    "published_at": str,  # ISO datetime
    "image": str
}
```

### Post-Processing (Part D Compliance)
**Same filtering & scoring applied regardless of provider**:
- ✅ Multi-source consensus rules
- ✅ Entity matching (credible sources)
- ✅ Confidence scaling (3+ sources = 80-85%, 2 sources = 75-80%, etc.)
- ✅ Recency bonus (+5% if <24h, +3% if <48h)
- ✅ Stance detection (if enabled)
- ✅ Brand trust boost (Premium outlets: +5-10%)
- ✅ Confidence ceilings (news: 90%, scientific: 99%, etc.)

**No separate scoring rules created** - all existing logic applies uniformly.

---

## Testing Checklist

### ✅ Manual Testing Required:
1. **GNews Success**: Verify normal operation with valid GNews key
2. **GNews Failure → NewsAPI Success**: 
   - Remove/invalidate GNews key
   - Verify NewsAPI takes over
   - Check `news_provider_used: "newsapi"` in response
3. **Both Fail**: 
   - Remove both keys
   - Verify confidence = 47, verdict = "Unverified"
   - Check `news_provider_used: "none"`
4. **Logging**: Check terminal for `[UnifiedNews]` logs showing failover
5. **UI Transparency**: Verify frontend shows provider info (if implemented)

---

## Compliance with Requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| **A. When to Use NewsAPI** | ✅ | 429, 401, 5xx, empty, timeout all trigger fallback |
| **B. Implement NewsAPI Service** | ✅ | `newsapi_service.py` with correct endpoint & params |
| **C. Unified Interface** | ✅ | `get_news_results()` wraps both providers |
| **D. Reuse Same Filtering** | ✅ | All existing scoring logic applies uniformly |
| **E. Output Transparency** | ✅ | `news_provider_used` field added to responses |
| **F. Error Handling** | ✅ | Both fail → Unverified, confidence 45-50, not false |
| **G. Strict Rules** | ✅ | No UI changes, no hardcoded keys, no threshold changes |

---

## Configuration Steps

### 1. Get NewsAPI Key
1. Visit https://newsapi.org/
2. Sign up for free account (100 requests/day)
3. Copy API key from dashboard

### 2. Update `.env`
```env
GNEWS_API_KEY=your_gnews_key_here
NEWSAPI_KEY=your_newsapi_key_here
```

### 3. Restart Backend
```bash
cd backend
uvicorn app.main:app --reload
```

---

## Logging Examples

### Successful GNews:
```
[UnifiedNews] Fetching news for query: Is climate change real?
[UnifiedNews] ✓ GNews returned 15 articles
```

### Fallback to NewsAPI:
```
[UnifiedNews] Fetching news for query: Is climate change real?
[UnifiedNews] GNews returned no articles: Rate limit exceeded
[UnifiedNews] Falling back to NewsAPI...
[NewsAPI] Searching for: climate change real
[UnifiedNews] ✓ NewsAPI returned 10 articles (fallback)
```

### Both Failed:
```
[UnifiedNews] Fetching news for query: Is climate change real?
[UnifiedNews] GNews failed with exception: Invalid API key
[UnifiedNews] Falling back to NewsAPI...
[NewsAPI] API error: Authentication failed
[UnifiedNews] NewsAPI also failed: NewsAPI authentication failed
```

---

## API Response Examples

### With GNews:
```json
{
  "claim": "Is climate change real?",
  "verdict": "Verified True",
  "confidence": 85,
  "sources": ["https://reuters.com/...", "https://bbc.com/..."],
  "publisher": ["Reuters", "BBC News"],
  "verification_source": "gnews",
  "news_provider_used": "gnews",
  "explanation": [
    "→ Using GNEWS as news provider",
    "→ Multi-source verification: 3 independent source(s) = STRONG (3+ sources)",
    "→ 2 premium outlet(s): +5%"
  ]
}
```

### With NewsAPI Fallback:
```json
{
  "claim": "Is climate change real?",
  "verdict": "Verified True",
  "confidence": 82,
  "sources": ["https://cnn.com/...", "https://guardian.com/..."],
  "publisher": ["CNN", "The Guardian"],
  "verification_source": "newsapi",
  "news_provider_used": "newsapi",
  "explanation": [
    "→ Using NEWSAPI as news provider",
    "→ Multi-source verification: 2 independent source(s) = MODERATE (2 sources)",
    "→ 2 premium outlet(s): +5%"
  ]
}
```

### Both Failed:
```json
{
  "claim": "Is climate change real?",
  "verdict": "Unverified / Needs More Evidence",
  "confidence": 47,
  "sources": [],
  "publisher": [],
  "verification_source": "analysis_engine",
  "news_provider_used": "none",
  "explanation": [
    "→ News providers temporarily unavailable; cannot verify claim"
  ]
}
```

---

## Future Enhancements (Optional)

1. **UI Badge**: Show "Powered by GNews" or "Powered by NewsAPI" in frontend
2. **Retry Logic**: Exponential backoff for temporary failures
3. **Cache Provider Info**: Store which provider was used in cache
4. **Metrics**: Track failover frequency for monitoring
5. **Provider Preference**: Allow users to choose preferred provider

---

## Files Modified
1. ✅ `backend/app/services/newsapi_service.py` (NEW)
2. ✅ `backend/app/services/analysis_engine.py` (MODIFIED)
3. ✅ `.env` (MODIFIED - added NEWSAPI_KEY placeholder)

---

## Notes
- **No frontend changes required** - all changes are backend-only
- **No database migrations needed** - uses existing cache structure
- **Backward compatible** - works without NewsAPI key (falls back to "none")
- **GNews remains primary** - NewsAPI only used on failure
- **Silent failover** - users never see errors, just alternate provider
- **Same UX** - identical scoring, filtering, and response format

---

## Troubleshooting

### Issue: "NewsAPI key not configured"
**Solution**: Add `NEWSAPI_KEY=...` to `.env` file

### Issue: "Both providers failed"
**Solution**: Check both API keys are valid and have quota remaining

### Issue: No failover happening
**Solution**: Check logs for `[UnifiedNews]` messages showing provider attempts

### Issue: Different confidence scores
**Solution**: Normal - different articles from different providers, but same scoring rules

---

## End of Implementation
System now survives API failures without breaking verification.  
GNews stays primary. NewsAPI is silent backup. User never sees failure.
