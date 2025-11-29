"""
Database migration script to add Watcher Agent tables.
Run this to update the database schema with WatcherEvent and WatcherLog tables.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, inspect
from app.models import Base, WatcherEvent, WatcherLog
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = "sqlite:///./filtr.db"


def migrate_watcher_tables():
    """Add WatcherEvent and WatcherLog tables to existing database."""
    
    logger.info("Starting Watcher Agent database migration...")
    
    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)
    
    # Check existing tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    logger.info(f"Existing tables: {existing_tables}")
    
    # Create only the new tables
    tables_to_create = []
    
    if "watcher_events" not in existing_tables:
        tables_to_create.append(WatcherEvent.__table__)
        logger.info("Will create table: watcher_events")
    else:
        logger.info("Table watcher_events already exists")
    
    if "watcher_logs" not in existing_tables:
        tables_to_create.append(WatcherLog.__table__)
        logger.info("Will create table: watcher_logs")
    else:
        logger.info("Table watcher_logs already exists")
    
    if tables_to_create:
        logger.info(f"Creating {len(tables_to_create)} new table(s)...")
        Base.metadata.create_all(engine, tables=tables_to_create)
        logger.info("✅ Migration completed successfully!")
    else:
        logger.info("✅ All tables already exist. No migration needed.")


if __name__ == "__main__":
    migrate_watcher_tables()
