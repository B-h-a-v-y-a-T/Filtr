"""
Database migration script to update ClaimHistory table to allow NULL user_id.
"""
import sqlite3
import os

def migrate_database():
    """Migrate the database schema to allow NULL user_id in claim_history."""
    
    # Database path
    db_paths = [
        os.path.join(os.path.dirname(__file__), "filtr.db"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "filtr.db")
    ]
    
    for db_path in db_paths:
        if not os.path.exists(db_path):
            print(f"Database not found: {db_path}")
            continue
            
        print(f"Migrating database: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if claim_history table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='claim_history'")
            if not cursor.fetchone():
                print("  → claim_history table doesn't exist, skipping migration")
                conn.close()
                continue
            
            # Create new table with nullable user_id
            print("  → Creating new claim_history table with nullable user_id...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS claim_history_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    claim_text TEXT NOT NULL,
                    verdict VARCHAR(50) NOT NULL,
                    confidence REAL NOT NULL,
                    sources_json TEXT,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Copy data from old table
            print("  → Copying existing data...")
            cursor.execute("""
                INSERT INTO claim_history_new (id, user_id, claim_text, verdict, confidence, sources_json, created_at)
                SELECT id, user_id, claim_text, verdict, confidence, sources_json, created_at
                FROM claim_history
            """)
            
            # Drop old table
            print("  → Dropping old table...")
            cursor.execute("DROP TABLE claim_history")
            
            # Rename new table
            print("  → Renaming new table...")
            cursor.execute("ALTER TABLE claim_history_new RENAME TO claim_history")
            
            # Recreate indexes
            print("  → Creating indexes...")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_claim_history_user_id ON claim_history(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_claim_history_created_at ON claim_history(created_at)")
            
            conn.commit()
            print(f"  ✅ Migration completed successfully for {db_path}")
            
        except Exception as e:
            print(f"  ❌ Migration failed for {db_path}: {e}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == "__main__":
    print("Starting database migration...")
    print("="*60)
    migrate_database()
    print("="*60)
    print("Migration complete!")
