# Watcher Agent - Continuous Misinformation Monitoring System

## Overview

The Watcher Agent is a sophisticated background service that continuously monitors breaking news from multiple sources to detect emerging misinformation trends related to crises, politics, health, and viral topics.

## Features

### ✅ Implemented Features

#### 1. **Multi-Source Data Collection**
- **Primary APIs**: GNews API, NewsAPI (with automatic fallback)
- **RSS Fallback**: BBC, Reuters, The Hindu, ANI (when API limits reached)
- **Smart Rotation**: Automatic source switching based on availability

#### 2. **Intelligent Keyword Tracking**
Categories monitored:
- **Health**: COVID, vaccine, outbreak, WHO, pandemic, disease
- **Politics**: election, riot, protest, vote fraud, corruption
- **Disasters**: earthquake, cyclone, flood, tsunami, wildfire
- **Technology**: AI, hacking, data leak, cyber attack, privacy breach
- **Finance**: stock crash, bank collapse, scam, fraud, crypto crash

#### 3. **Automated Analysis Pipeline**
- Integrates with existing `analysis_engine.py`
- Normalizes headlines
- Runs verification checks
- Stores results with confidence scores
- Tracks credibility flags (high_risk, medium_risk, low_risk)

#### 4. **Advanced Trend Detection**
Triggers alerts when:
- Same false narrative appears 3+ times
- Keywords cluster across 5+ sources
- Spike in claims (5+ articles) within 1 hour
- High-risk patterns emerge

#### 5. **Rate Limiting & API Safety**
- Daily limit: 100 API calls (90 safe threshold)
- Automatic daily reset at midnight
- Backoff strategy on rate limit (429) errors
- Graceful fallback to RSS feeds
- Request counter with usage tracking

#### 6. **Background Execution**
- APScheduler for reliable scheduling
- Runs every 30 minutes
- Heartbeat logging every 5 minutes
- Auto-restart on crash (up to 5 errors)
- Memory-safe batch processing (10 articles per cycle)

#### 7. **Database Storage**

**WatcherEvent Table**:
```python
- id: Primary key
- keyword_group: Category (health, politics, etc.)
- headline: Article headline
- source: News source name
- url: Article URL
- verdict: Analysis result
- confidence: Confidence score (0-100)
- category: Same as keyword_group
- credibility_flag: high_risk | medium_risk | low_risk
- first_seen: First detection timestamp
- times_seen: Counter for repeated occurrences
- last_seen: Last detection timestamp
- analysis_data: Full JSON analysis result
```

**WatcherLog Table**:
```python
- id: Primary key
- cycle_timestamp: When cycle ran
- api_source: gnews | newsapi | rss
- keyword_group: Which category was monitored
- articles_fetched: Number of articles retrieved
- articles_analyzed: Number successfully analyzed
- api_calls_used: API quota consumed
- status: success | rate_limit | error
- error_message: Error details if failed
- execution_time_seconds: Performance metric
```

## API Endpoints

### 1. GET `/api/v1/watcher-dashboard`
**Returns comprehensive monitoring dashboard data**

Response:
```json
{
  "status": "success",
  "trends": [
    {
      "type": "repeated_narrative|keyword_cluster|spike_alert",
      "description": "...",
      "risk_level": "high|medium|low",
      "occurrences": 5,
      "sources": ["BBC", "Reuters"],
      "keyword": "...",
      "category": "health"
    }
  ],
  "latest_alerts": [
    {
      "headline": "...",
      "source": "...",
      "verdict": "Likely False",
      "confidence": 85,
      "category": "health",
      "timestamp": "2025-11-29T10:30:00",
      "url": "...",
      "times_seen": 3
    }
  ],
  "risky_claims": [
    {
      "headline": "...",
      "source": "...",
      "verdict": "...",
      "confidence": 75,
      "category": "politics",
      "times_seen": 5,
      "credibility_flag": "high_risk"
    }
  ],
  "risk_level": "high|medium|low",
  "last_updated": "2025-11-29T10:30:00.000Z",
  "monitoring_status": {
    "api_calls_remaining": 45,
    "last_cycle": "2025-11-29T10:00:00",
    "last_status": "success"
  }
}
```

### 2. GET `/api/v1/watcher-status`
**Get scheduler health and status**

Response:
```json
{
  "status": "success",
  "is_running": true,
  "last_heartbeat": "2025-11-29T10:25:00",
  "error_count": 0,
  "jobs": [
    {
      "id": "watcher_monitoring_cycle",
      "name": "Watcher Agent Monitoring Cycle",
      "next_run": "2025-11-29T10:30:00"
    },
    {
      "id": "watcher_heartbeat",
      "name": "Watcher Agent Heartbeat",
      "next_run": "2025-11-29T10:30:00"
    }
  ]
}
```

### 3. POST `/api/v1/watcher-trigger`
**Manually trigger a monitoring cycle**

Response:
```json
{
  "status": "success",
  "message": "Monitoring cycle completed",
  "cycle_timestamp": "2025-11-29T10:30:00",
  "keyword_group": "health",
  "articles_fetched": 15,
  "articles_analyzed": 10,
  "api_calls_remaining": 44,
  "execution_time": 12.5
}
```

## Installation & Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `APScheduler` - Background task scheduling
- `feedparser` - RSS feed parsing

### 2. Run Database Migration
```bash
cd backend
python migrate_watcher.py
```

This creates:
- `watcher_events` table
- `watcher_logs` table

### 3. Start the Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The Watcher Agent automatically starts on application startup and runs every 30 minutes.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Watcher Agent System                     │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
    ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
    │  Scheduler   │ │  Agent    │ │   Trend     │
    │ (30 minutes) │ │  Core     │ │  Detector   │
    └───────┬──────┘ └─────┬─────┘ └──────┬──────┘
            │               │               │
            │      ┌────────▼────────┐      │
            │      │   Data Sources   │      │
            │      │  - GNews API     │      │
            │      │  - NewsAPI       │      │
            │      │  - RSS Feeds     │      │
            │      └────────┬────────┘      │
            │               │               │
            │      ┌────────▼────────┐      │
            │      │  Rate Limiter   │      │
            │      │  (100/day max)  │      │
            │      └────────┬────────┘      │
            │               │               │
            │      ┌────────▼────────┐      │
            │      │  Keyword Mgr    │      │
            │      │  (5 categories) │      │
            │      └────────┬────────┘      │
            │               │               │
            └──────────────►│◄──────────────┘
                            │
                   ┌────────▼────────┐
                   │ Analysis Engine │
                   │  (Existing)     │
                   └────────┬────────┘
                            │
                   ┌────────▼────────┐
                   │    Database     │
                   │  - WatcherEvent │
                   │  - WatcherLog   │
                   └─────────────────┘
```

## How It Works

### Monitoring Cycle Flow

1. **Scheduler Triggers** (every 30 minutes)
   - Check API quota remaining
   - Select next keyword group (rotating)

2. **Data Collection**
   - Try GNews API (if quota available)
   - Fallback to NewsAPI (if needed)
   - Fallback to RSS feeds (if APIs exhausted)

3. **Article Processing**
   - Limit to 10 articles per cycle (memory safety)
   - Normalize headlines
   - Check for duplicates (by headline hash)

4. **Analysis**
   - Run through existing `analysis_engine`
   - Extract verdict and confidence
   - Determine credibility flag

5. **Storage**
   - Store new events in `watcher_events`
   - Update existing events (increment `times_seen`)
   - Log cycle details in `watcher_logs`

6. **Trend Detection**
   - Analyze patterns across last 24 hours
   - Detect repeated narratives (3+ occurrences)
   - Find keyword clusters (5+ mentions)
   - Identify time-based spikes (1-hour window)

### Rate Limiting Strategy

- **Daily Limit**: 100 API calls
- **Safety Buffer**: Stop at 90 calls (10-call buffer)
- **Reset**: Automatic at midnight
- **Backoff**: 10-minute sleep on 429 errors (built into services)
- **Fallback**: Switch to RSS when API exhausted

### Keyword Rotation

The agent rotates through 5 keyword groups:
1. Health → 2. Politics → 3. Disasters → 4. Technology → 5. Finance → (repeat)

Each cycle monitors one group, ensuring balanced coverage.

## Trend Alert Types

### 1. Repeated Narrative
- **Trigger**: Same headline appears 3+ times
- **Risk**: High
- **Action**: Investigate coordinated misinformation campaign

### 2. Keyword Cluster
- **Trigger**: Keyword appears in 5+ articles
- **Risk**: Medium
- **Action**: Monitor topic for developing story

### 3. Spike Alert
- **Trigger**: 5+ articles in same category within 1 hour
- **Risk**: High
- **Action**: Possible breaking misinformation event

## Logging

The system logs:
- Cycle start/end timestamps
- Articles fetched vs analyzed
- API quota usage
- Errors and exceptions
- Heartbeat every 5 minutes

View logs:
```bash
# In application logs
tail -f backend.log | grep "Watcher"
```

## Troubleshooting

### Issue: Scheduler Not Starting
**Check**: Application logs for startup errors
**Fix**: Ensure APScheduler is installed
```bash
pip install APScheduler
```

### Issue: No Articles Being Fetched
**Check**: API keys in `.env` file
**Fix**: Verify `GNEWS_API_KEY` and `NEWSAPI_KEY` are set

### Issue: Database Errors
**Check**: Migration ran successfully
**Fix**: Run migration script
```bash
python backend/migrate_watcher.py
```

### Issue: Rate Limit Reached
**Check**: Current quota via `/api/v1/watcher-status`
**Action**: Wait for midnight reset or use RSS fallback

## Performance

- **Memory**: ~50MB per cycle
- **Processing**: ~10-15 seconds per cycle
- **Database**: Efficient indexing on timestamps and flags
- **Network**: Minimal bandwidth (JSON APIs + RSS)

## Security

- ✅ No login-based scraping
- ✅ Only public RSS feeds
- ✅ No JavaScript-heavy site scraping
- ✅ Rate limiting prevents abuse
- ✅ All API keys in environment variables

## Future Enhancements

Potential additions:
- [ ] Email alerts for high-risk trends
- [ ] Machine learning for better trend detection
- [ ] Multi-language support
- [ ] Custom keyword configuration via UI
- [ ] Historical trend analysis graphs
- [ ] Export reports to PDF/CSV

## Testing

### Manual Trigger
Test the watcher immediately:
```bash
curl -X POST http://localhost:8000/api/v1/watcher-trigger
```

### View Dashboard
```bash
curl http://localhost:8000/api/v1/watcher-dashboard
```

### Check Status
```bash
curl http://localhost:8000/api/v1/watcher-status
```

## Integration with Existing Features

The Watcher Agent:
- ✅ Uses existing `analysis_engine.py` for verification
- ✅ Integrates with existing database models
- ✅ No frontend changes required
- ✅ Exposes RESTful API endpoints
- ✅ Compatible with current authentication system

## Support

For issues or questions:
1. Check application logs
2. Review database for stored events
3. Test API endpoints manually
4. Verify environment variables

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: November 29, 2025
