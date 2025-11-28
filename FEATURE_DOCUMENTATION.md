# New Features Documentation

## Overview

Three new features have been added to the Filtr analysis engine to improve reliability, explainability, and testability:

1. **Caching + Claim Normalization** - Reduces API calls and improves response time
2. **Confidence Breakdown** - Provides transparency into scoring for UI display
3. **Sandbox Mode** - Stress testing for quality assurance

---

## Feature C: Caching + Claim Normalization

### What It Does

- **Normalizes claims** before lookup to handle minor variations (case, spacing, punctuation)
- **Caches verification results** in memory to avoid redundant API calls
- **Returns cached results instantly** for repeated or similar claims

### How It Works

1. When a claim is received, it is normalized:
   - Converted to lowercase
   - Extra whitespace removed
   - Leading/trailing punctuation stripped

2. The normalized claim is used as a cache key
3. If found in cache → return immediately
4. If not found → run full verification pipeline → store in cache

### Benefits

- **Faster responses** for repeated claims
- **Reduced API usage** (Google Fact Check, GNews)
- **Consistent results** for equivalent claims

### Example

```python
# These all hit the same cache entry:
"COVID-19 was created in a lab"
"  COVID-19 was created in a lab  "
"COVID-19 WAS CREATED IN A LAB!!!"
```

### Cache Information

- **Storage**: In-memory dictionary (no external dependencies)
- **Persistence**: Lost on server restart (by design)
- **Size**: Unbounded (consider adding TTL or size limit for production)

---

## Feature D: Confidence Breakdown

### What It Does

Exposes the **internal scoring components** so users can understand how the confidence score was calculated.

### API Response Structure

Each verification result now includes a `confidence_breakdown` field:

```json
{
  "claim": "Example claim",
  "verdict": "Likely True",
  "confidence": 73,
  "confidence_breakdown": {
    "authority": 20,
    "news_consensus": 15,
    "stance_alignment": 5,
    "recency_adjustment": -5,
    "final_score": 73
  },
  "explanation": [...],
  "sources": [...]
}
```

### Breakdown Components

| Field | Description | Range |
|-------|-------------|-------|
| `authority` | Score from Google Fact Check API ratings | -50 to +50 |
| `news_consensus` | Score from credible news source analysis | -20 to +15 |
| `stance_alignment` | Score from headline stance detection | -15 to +15 |
| `recency_adjustment` | Penalty for stale evidence | -10 to 0 |
| `final_score` | Total confidence (clamped 0-100) | 0 to 100 |

### UI Integration

The breakdown is **designed for frontend display** behind an info icon (ⓘ):

- Show as a tooltip or modal
- Format as positive/negative deltas
- Display in a clean, user-friendly format (see Zepto-style fee breakdowns)

**Note**: The backend only provides the data - frontend implementation is not included.

---

## Feature E: Sandbox Mode (Stress Testing)

### What It Does

Runs **automated stress tests** on the verification engine to validate scoring logic and reliability.

### How to Enable

1. Set environment variable in `backend/.env`:
   ```
   SANDBOX_MODE=true
   ```

2. Restart the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Check server logs for test results

### Test Scenarios

The sandbox runs these claim types:

1. **False Medical Claims**
   - "Drinking bleach cures COVID-19"
   - "5G towers cause coronavirus infections"

2. **Political Rumors**
   - "The 2020 US election was stolen through massive fraud"

3. **Real News** (should score high)
   - "NASA successfully launched the James Webb Space Telescope in 2021"
   - "The COVID-19 pandemic began in late 2019"

4. **Conspiracy Theories**
   - "Bill Gates wants to microchip everyone through vaccines"

5. **Viral Misinformation**
   - "Sharks are immune to cancer"

### Output

Sandbox logs include:

- ✓ PASS or ✗ FAIL for each test
- Expected vs actual verdict
- Confidence score
- Explanation steps
- Source count

Example:
```
--- Testing: False Medical Claim ---
Claim: Drinking bleach cures COVID-19
Expected: Likely False
Actual: Likely False (10%) ✓ PASS
Sources: 5 found
```

### Important Notes

- **Internal use only** - not exposed to frontend
- **Runs on server startup** if enabled
- **Does not block server** - runs as background task
- **Logs to console** - use for manual QA

---

## Testing

### Test Script

A comprehensive test script is included: `backend/test_new_features.py`

Run it with:
```bash
cd backend
python test_new_features.py
```

### Test Coverage

1. **Claim Normalization** - Verifies various input formats normalize correctly
2. **Caching** - Confirms cache hits/misses work as expected
3. **Confidence Breakdown** - Validates JSON structure
4. **API Compatibility** - Ensures no breaking changes

### Expected Output

All tests should show **✓ PASS**:
```
✓ PASS - Caching works correctly!
✓ PASS - Confidence breakdown structure correct
✓ PASS - All required fields present
```

---

## Implementation Details

### Files Modified

1. **`backend/app/services/analysis_engine.py`**
   - Added cache functions (`normalize_claim`, `get_cached_result`, `cache_result`)
   - Added confidence breakdown tracking in `analyze_claim()`
   - Added sandbox mode tests and test claims
   - Updated `verify_claim()` to check cache first

2. **`backend/app/main.py`**
   - Added sandbox test runner on startup

3. **`backend/.env`**
   - Added `SANDBOX_MODE=false` (default off)
   - Added `ENABLE_STANCE_DETECTION=true` (for existing feature)

### No Breaking Changes

- All existing API fields remain unchanged
- Only **added** new `confidence_breakdown` field
- Backward compatible with existing frontend

---

## Configuration

### Environment Variables

Add to `backend/.env`:

```bash
# Enable stance detection (for confidence breakdown)
ENABLE_STANCE_DETECTION=true

# Enable sandbox stress testing (development only)
SANDBOX_MODE=false
```

### Recommended Settings

**Development**:
```
ENABLE_STANCE_DETECTION=true
SANDBOX_MODE=true
```

**Production**:
```
ENABLE_STANCE_DETECTION=true
SANDBOX_MODE=false
```

---

## Future Enhancements

### Caching

- Add TTL (time-to-live) for cache entries
- Implement cache size limits
- Add cache statistics endpoint
- Consider Redis for distributed caching

### Confidence Breakdown

- Add more granular sub-scores
- Track individual source contributions
- Add confidence intervals/ranges

### Sandbox Mode

- Add custom test scenario API
- Generate test reports in JSON/HTML
- Add performance benchmarks
- Compare results over time

---

## API Examples

### Basic Verification with Breakdown

**Request**:
```bash
POST /api/v1/analyze
Content-Type: application/json

{
  "claim": "The Moon landing was faked"
}
```

**Response**:
```json
{
  "status": "completed",
  "claim": "The Moon landing was faked",
  "verdict": "Likely False",
  "confidence": 5,
  "confidence_breakdown": {
    "authority": -35,
    "news_consensus": 0,
    "stance_alignment": 0,
    "recency_adjustment": -10,
    "final_score": 5
  },
  "explanation": [
    "✓ Found existing fact-check(s) for this claim",
    "  → PolitiFact rated: 'Pants on Fire' (confidence: 5%)",
    "  → Using fact-check as primary source (no GNews fallback needed)",
    "→ Newest evidence is 120 days old → -10% confidence (stale)",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "Final confidence: 5%",
    "Verdict: Likely False"
  ],
  "sources": ["https://www.politifact.com/..."],
  "publisher": ["PolitiFact"],
  "published_dates": ["2024-07-20"],
  "last_checked": "2025-11-26T12:34:56.789Z"
}
```

### Cached Response

Second call with same claim returns cached result with `"cached": true`:

```json
{
  "status": "completed",
  "cached": true,
  "claim": "The Moon landing was faked",
  "verdict": "Likely False",
  "confidence": 5,
  ...
}
```

---

## Summary

✅ **Caching** reduces API load and improves speed  
✅ **Confidence Breakdown** provides transparency for users  
✅ **Sandbox Mode** validates engine reliability  
✅ **Backward Compatible** - no breaking changes  
✅ **Tested** - all features verified working  

All features are production-ready and integrated into the Bhavya branch.
