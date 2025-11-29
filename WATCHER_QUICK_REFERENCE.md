# Watcher Agent - Quick Reference

## 🚀 Installation (3 Steps)
```bash
# 1. Install new dependencies
pip install APScheduler feedparser

# 2. Run database migration
python backend/migrate_watcher.py

# 3. Start backend (auto-starts Watcher)
python -m uvicorn app.main:app --reload --port 8000
```

## 📡 API Endpoints

### Dashboard Data
```bash
GET http://localhost:8000/api/v1/watcher-dashboard
```

### Health Check
```bash
GET http://localhost:8000/api/v1/watcher-status
```

### Manual Trigger
```bash
POST http://localhost:8000/api/v1/watcher-trigger
```

## ⚙️ Configuration

### Monitoring Schedule
- **Interval**: Every 30 minutes
- **Heartbeat**: Every 5 minutes
- **Batch Size**: 10 articles per cycle

### API Limits
- **Daily Limit**: 100 calls
- **Safety Stop**: 90 calls
- **Reset**: Midnight automatic

### Data Sources
1. **GNews API** (primary)
2. **NewsAPI** (fallback)
3. **RSS Feeds** (BBC, Reuters, The Hindu, ANI)

## 📊 Keyword Categories

| Category | Keywords |
|----------|----------|
| Health | COVID, vaccine, outbreak, WHO, pandemic |
| Politics | election, riot, protest, vote fraud |
| Disasters | earthquake, cyclone, flood, tsunami |
| Technology | AI, hacking, data leak, cyber attack |
| Finance | crash, bank, scam, fraud, crypto |

## 🚨 Alert Triggers

- **Repeated Narrative**: 3+ occurrences
- **Keyword Cluster**: 5+ mentions
- **Spike Alert**: 5+ articles in 1 hour

## 📁 Database Tables

### watcher_events
Stores detected misinformation articles

### watcher_logs
Tracks monitoring cycles and performance

## 🧪 Testing
```bash
python backend/test_watcher_agent.py
```

## 📖 Full Documentation
See `WATCHER_AGENT_DOCUMENTATION.md`

## ✅ Status
All requirements implemented ✓
Backend-only solution ✓
No frontend changes ✓
Production ready ✓
