"""
SQLAlchemy models for SQLite database.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    otp_codes = relationship("OTPCode", back_populates="user", cascade="all, delete-orphan")
    claim_history = relationship("ClaimHistory", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("Settings", back_populates="user", uselist=False, cascade="all, delete-orphan")


class OTPCode(Base):
    __tablename__ = "otp_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    otp_code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="otp_codes")


class ClaimHistory(Base):
    __tablename__ = "claim_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Nullable for system cache
    claim_text = Column(Text, nullable=False)
    verdict = Column(String(50), nullable=False)  # "Likely True", "Likely False", "Uncertain"
    confidence = Column(Float, nullable=False)
    sources_json = Column(Text, nullable=True)  # JSON string of sources
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="claim_history")


class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    daily_summary_enabled = Column(Boolean, default=False, nullable=False)
    notification_email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="settings")


class DailySummary(Base):
    __tablename__ = "daily_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class WatcherEvent(Base):
    __tablename__ = "watcher_events"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword_group = Column(String(100), nullable=False, index=True)  # Health, Politics, etc.
    headline = Column(Text, nullable=False)
    source = Column(String(255), nullable=False)
    url = Column(Text, nullable=True)
    verdict = Column(String(50), nullable=False)  # "Verified True", "Likely False", etc.
    confidence = Column(Float, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    credibility_flag = Column(String(50), nullable=False)  # "high_risk", "medium_risk", "low_risk"
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    times_seen = Column(Integer, default=1, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    analysis_data = Column(Text, nullable=True)  # JSON string with full analysis details


class WatcherLog(Base):
    __tablename__ = "watcher_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    cycle_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    api_source = Column(String(50), nullable=False)  # "gnews", "newsapi", "rss"
    keyword_group = Column(String(100), nullable=False)
    articles_fetched = Column(Integer, default=0, nullable=False)
    articles_analyzed = Column(Integer, default=0, nullable=False)
    api_calls_used = Column(Integer, default=0, nullable=False)
    status = Column(String(50), nullable=False)  # "success", "rate_limit", "error"
    error_message = Column(Text, nullable=True)
    execution_time_seconds = Column(Float, nullable=True)
