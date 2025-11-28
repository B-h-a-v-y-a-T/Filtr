import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from ..models import Base, User, OTPCode, ClaimHistory, Settings


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./filtr.db")
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(plain_password) == hashed_password


# User management functions

def create_user(db: Session, name: str, email: str, password: str) -> User:
    """Create a new user."""
    hashed_pw = hash_password(password)
    user = User(name=name, email=email, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create default settings for the user
    settings = Settings(user_id=user.id)
    db.add(settings)
    db.commit()
    
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def verify_login(db: Session, email: str, password: str) -> Optional[User]:
    """Verify user login credentials."""
    user = get_user_by_email(db, email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None


# OTP/2FA functions

def save_otp_code(db: Session, user_id: int, otp_code: str, expires_in_minutes: int = 10) -> OTPCode:
    """Save OTP code for 2FA."""
    expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    otp = OTPCode(user_id=user_id, otp_code=otp_code, expires_at=expires_at)
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp


def validate_otp_code(db: Session, user_id: int, otp_code: str) -> bool:
    """Validate OTP code for 2FA."""
    otp = db.query(OTPCode).filter(
        OTPCode.user_id == user_id,
        OTPCode.otp_code == otp_code,
        OTPCode.expires_at > datetime.utcnow()
    ).first()
    
    if otp:
        # Delete used OTP
        db.delete(otp)
        db.commit()
        return True
    return False


def cleanup_expired_otps(db: Session) -> None:
    """Delete expired OTP codes."""
    db.query(OTPCode).filter(OTPCode.expires_at <= datetime.utcnow()).delete()
    db.commit()


# Claim history functions

def save_claim_to_history(
    db: Session,
    user_id: int,
    claim_text: str,
    verdict: str,
    confidence: float,
    sources: List[str]
) -> ClaimHistory:
    """Save claim verification to user's history."""
    sources_json = json.dumps(sources)
    claim = ClaimHistory(
        user_id=user_id,
        claim_text=claim_text,
        verdict=verdict,
        confidence=confidence,
        sources_json=sources_json
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def get_user_history(db: Session, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Get user's claim verification history."""
    claims = db.query(ClaimHistory).filter(
        ClaimHistory.user_id == user_id
    ).order_by(ClaimHistory.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": claim.id,
            "claim_text": claim.claim_text,
            "verdict": claim.verdict,
            "confidence": claim.confidence,
            "sources": json.loads(claim.sources_json) if claim.sources_json else [],
            "created_at": claim.created_at.isoformat()
        }
        for claim in claims
    ]


# Settings functions

def update_user_settings(
    db: Session,
    user_id: int,
    daily_summary_enabled: Optional[bool] = None,
    notification_email: Optional[str] = None
) -> Settings:
    """Update user settings."""
    settings = db.query(Settings).filter(Settings.user_id == user_id).first()
    
    if not settings:
        settings = Settings(user_id=user_id)
        db.add(settings)
    
    if daily_summary_enabled is not None:
        settings.daily_summary_enabled = daily_summary_enabled
    if notification_email is not None:
        settings.notification_email = notification_email
    
    db.commit()
    db.refresh(settings)
    return settings


def get_user_settings(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    """Get user settings."""
    settings = db.query(Settings).filter(Settings.user_id == user_id).first()
    
    if not settings:
        return None
    
    return {
        "daily_summary_enabled": settings.daily_summary_enabled,
        "notification_email": settings.notification_email,
        "created_at": settings.created_at.isoformat()
    }







