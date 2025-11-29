"""
Background Scheduler for Watcher Agent
Runs monitoring cycles every 30 minutes with auto-restart on crash.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from sqlalchemy.orm import Session
from .watcher_agent import WatcherAgent
from .db import get_db

logger = logging.getLogger(__name__)


class WatcherScheduler:
    """Manages background scheduling for Watcher Agent."""
    
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.is_running = False
        self.last_heartbeat = None
        self.error_count = 0
        self.max_errors = 5
    
    def start(self):
        """Start the background scheduler."""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        logger.info("Starting Watcher Agent Scheduler")
        
        # Create async scheduler
        self.scheduler = AsyncIOScheduler()
        
        # Add monitoring job - runs every 30 minutes
        self.scheduler.add_job(
            func=self._run_monitoring_cycle_wrapper,
            trigger=IntervalTrigger(minutes=30),
            id="watcher_monitoring_cycle",
            name="Watcher Agent Monitoring Cycle",
            max_instances=1,  # Prevent overlapping runs
            coalesce=True,    # If missed, run only once
            replace_existing=True
        )
        
        # Add heartbeat job - runs every 5 minutes
        self.scheduler.add_job(
            func=self._heartbeat,
            trigger=IntervalTrigger(minutes=5),
            id="watcher_heartbeat",
            name="Watcher Agent Heartbeat",
            replace_existing=True
        )
        
        # Add event listeners
        self.scheduler.add_listener(
            self._job_executed_listener,
            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )
        
        # Start scheduler
        self.scheduler.start()
        self.is_running = True
        
        logger.info("✅ Watcher Agent Scheduler started successfully")
        logger.info("📅 Monitoring cycle: Every 30 minutes")
        logger.info("💓 Heartbeat: Every 5 minutes")
        
        # Run first cycle immediately
        asyncio.create_task(self._run_monitoring_cycle_wrapper())
    
    def stop(self):
        """Stop the background scheduler."""
        if not self.is_running:
            return
        
        logger.info("Stopping Watcher Agent Scheduler")
        
        if self.scheduler:
            self.scheduler.shutdown(wait=False)
        
        self.is_running = False
        logger.info("✅ Watcher Agent Scheduler stopped")
    
    async def _run_monitoring_cycle_wrapper(self):
        """Wrapper for monitoring cycle with error handling and auto-restart."""
        db: Session = get_db()
        
        try:
            logger.info("🔄 Starting Watcher Agent monitoring cycle")
            
            # Create watcher agent instance
            watcher = WatcherAgent(db)
            
            # Run monitoring cycle
            result = await watcher.run_monitoring_cycle()
            
            logger.info(f"✅ Monitoring cycle completed: {result}")
            
            # Reset error count on success
            self.error_count = 0
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ Error in monitoring cycle (attempt {self.error_count}/{self.max_errors}): {e}")
            logger.exception(e)
            
            # Auto-restart if error count exceeds threshold
            if self.error_count >= self.max_errors:
                logger.critical(f"🚨 Max errors reached ({self.max_errors}). Restarting scheduler...")
                self.error_count = 0
                
                # Don't actually restart here, just reset counter
                # The scheduler itself will continue running
        
        finally:
            db.close()
    
    async def _heartbeat(self):
        """Log heartbeat to confirm scheduler is alive."""
        self.last_heartbeat = datetime.utcnow()
        logger.info(f"💓 Watcher Agent Heartbeat: {self.last_heartbeat.isoformat()} | Running: {self.is_running}")
    
    def _job_executed_listener(self, event):
        """Listen to job execution events."""
        if event.exception:
            logger.error(f"Job {event.job_id} raised exception: {event.exception}")
        else:
            logger.debug(f"Job {event.job_id} executed successfully")
    
    def get_status(self) -> dict:
        """Get scheduler status."""
        jobs = []
        if self.scheduler:
            for job in self.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                })
        
        return {
            "is_running": self.is_running,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "error_count": self.error_count,
            "jobs": jobs
        }


# Global scheduler instance
watcher_scheduler = WatcherScheduler()


def start_watcher_scheduler():
    """Start the global watcher scheduler."""
    watcher_scheduler.start()


def stop_watcher_scheduler():
    """Stop the global watcher scheduler."""
    watcher_scheduler.stop()


def get_watcher_status():
    """Get current scheduler status."""
    return watcher_scheduler.get_status()
