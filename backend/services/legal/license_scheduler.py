"""
License Management Scheduler
Background tasks for automated reminder processing
"""

import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.connection import AsyncSessionLocal
from .license_reminder_service import LicenseReminderService

logger = logging.getLogger(__name__)


class LicenseScheduler:
    """Scheduler for license-related background tasks"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    async def check_license_reminders_task(self):
        """Task to check and send license reminders"""
        logger.info("Starting license reminder check...")
        
        async with AsyncSessionLocal() as db:
            try:
                stats = await LicenseReminderService.check_and_send_reminders(db)
                logger.info(f"License reminder check completed: {stats}")
                
                if stats.get('errors'):
                    logger.error(f"Errors during reminder check: {stats['errors']}")
                    
            except Exception as e:
                logger.error(f"Error in license reminder task: {e}")
                await db.rollback()

    async def process_pending_reminders_task(self):
        """Task to process pending reminders"""
        logger.info("Processing pending reminders...")
        
        async with AsyncSessionLocal() as db:
            try:
                pending_reminders = await LicenseReminderService.get_pending_reminders(db)
                logger.info(f"Found {len(pending_reminders)} pending reminders")
                
                for reminder in pending_reminders:
                    try:
                        # TODO: Integrate with actual email/SMS service
                        # For now, just mark as sent
                        await LicenseReminderService.mark_reminder_sent(
                            db, 
                            reminder.id, 
                            success=True
                        )
                        logger.info(f"Processed reminder {reminder.id}")
                        
                    except Exception as e:
                        logger.error(f"Error processing reminder {reminder.id}: {e}")
                        await LicenseReminderService.mark_reminder_sent(
                            db, 
                            reminder.id, 
                            success=False,
                            error_message=str(e)
                        )
                        
            except Exception as e:
                logger.error(f"Error in process reminders task: {e}")
                await db.rollback()

    async def generate_daily_report_task(self):
        """Task to generate daily reminder report"""
        logger.info("Generating daily reminder report...")
        
        async with AsyncSessionLocal() as db:
            try:
                report = await LicenseReminderService.generate_reminder_report(db, days=1)
                logger.info(f"Daily reminder report: {report}")
                
                # TODO: Send report to administrators
                
            except Exception as e:
                logger.error(f"Error generating daily report: {e}")

    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        # Schedule reminder check - runs daily at 9 AM
        self.scheduler.add_job(
            self.check_license_reminders_task,
            CronTrigger(hour=9, minute=0),
            id='license_reminder_check',
            name='Check License Reminders',
            replace_existing=True
        )

        # Schedule pending reminder processing - runs every hour
        self.scheduler.add_job(
            self.process_pending_reminders_task,
            CronTrigger(minute=0),
            id='process_pending_reminders',
            name='Process Pending Reminders',
            replace_existing=True
        )

        # Schedule daily report - runs at 6 PM
        self.scheduler.add_job(
            self.generate_daily_report_task,
            CronTrigger(hour=18, minute=0),
            id='daily_reminder_report',
            name='Daily Reminder Report',
            replace_existing=True
        )

        self.scheduler.start()
        self.is_running = True
        logger.info("License scheduler started successfully")

    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return

        self.scheduler.shutdown()
        self.is_running = False
        logger.info("License scheduler stopped")

    def get_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduler.get_jobs()


# Global scheduler instance
license_scheduler = LicenseScheduler()


# API endpoint helpers
async def trigger_reminder_check_now():
    """Manually trigger reminder check"""
    logger.info("Manual reminder check triggered")
    async with AsyncSessionLocal() as db:
        return await LicenseReminderService.check_and_send_reminders(db)


async def get_reminder_statistics(days: int = 30):
    """Get reminder statistics"""
    async with AsyncSessionLocal() as db:
        return await LicenseReminderService.generate_reminder_report(db, days)
