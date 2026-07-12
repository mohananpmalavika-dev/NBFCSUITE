"""
Notification Scheduler

Background jobs for automated notifications:
- Rent due reminders (daily check)
- Lease expiry alerts (weekly check)
- Overdue payment reminders (daily check)
"""

import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.connection import get_db
from backend.shared.database.notification_models import (
    NotificationLog, NotificationTemplate, NotificationPreference,
    NotificationType, NotificationChannel, NotificationStatus
)
from backend.shared.database.property_rent_models import (
    Lease, RentPayment, Property
)
from .notification_service import get_notification_service

logger = logging.getLogger(__name__)

# Scheduler state
_scheduler_running = False
_scheduler_task = None


class NotificationScheduler:
    """
    Background scheduler for automated notifications
    """
    
    def __init__(self):
        self.notification_service = get_notification_service()
        self.running = False
    
    async def start(self):
        """Start all scheduled jobs"""
        self.running = True
        logger.info("🔔 Notification Scheduler started")
        
        # Run jobs in parallel
        await asyncio.gather(
            self._rent_due_reminder_job(),
            self._lease_expiry_alert_job(),
            self._payment_overdue_reminder_job(),
            return_exceptions=True
        )
    
    async def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("🔔 Notification Scheduler stopped")
    
    async def _rent_due_reminder_job(self):
        """
        Daily job: Check for upcoming rent due dates and send reminders
        Runs at 9 AM daily
        """
        while self.running:
            try:
                # Wait until 9 AM
                await self._wait_until_time(hour=9, minute=0)
                
                if not self.running:
                    break
                
                logger.info("📅 Running rent due reminder job...")
                
                async for db in get_db():
                    await self._process_rent_due_reminders(db)
                
                # Wait 24 hours before next run
                await asyncio.sleep(24 * 3600)
                
            except Exception as e:
                logger.error(f"Error in rent due reminder job: {str(e)}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _lease_expiry_alert_job(self):
        """
        Weekly job: Check for expiring leases and send alerts
        Runs every Monday at 10 AM
        """
        while self.running:
            try:
                # Wait until Monday 10 AM
                await self._wait_until_weekday(weekday=0, hour=10, minute=0)
                
                if not self.running:
                    break
                
                logger.info("📅 Running lease expiry alert job...")
                
                async for db in get_db():
                    await self._process_lease_expiry_alerts(db)
                
                # Wait 7 days before next run
                await asyncio.sleep(7 * 24 * 3600)
                
            except Exception as e:
                logger.error(f"Error in lease expiry alert job: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _payment_overdue_reminder_job(self):
        """
        Daily job: Check for overdue payments and send reminders
        Runs at 11 AM daily
        """
        while self.running:
            try:
                # Wait until 11 AM
                await self._wait_until_time(hour=11, minute=0)
                
                if not self.running:
                    break
                
                logger.info("📅 Running payment overdue reminder job...")
                
                async for db in get_db():
                    await self._process_overdue_payment_reminders(db)
                
                # Wait 24 hours before next run
                await asyncio.sleep(24 * 3600)
                
            except Exception as e:
                logger.error(f"Error in payment overdue reminder job: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _process_rent_due_reminders(self, db: AsyncSession):
        """
        Process rent due reminders
        Send reminders 3 days before due date
        """
        try:
            # Get date 3 days from now
            reminder_date = date.today() + timedelta(days=3)
            
            # Find all pending rent payments due in 3 days
            result = await db.execute(
                select(RentPayment, Lease, Property)
                .join(Lease, Lease.id == RentPayment.lease_id)
                .join(Property, Property.id == Lease.property_id)
                .where(
                    and_(
                        RentPayment.due_date == reminder_date,
                        RentPayment.payment_status.in_(['pending', 'partial']),
                        RentPayment.is_deleted == False,
                        Lease.status == 'active'
                    )
                )
            )
            
            payments = result.all()
            logger.info(f"Found {len(payments)} rent payments due in 3 days")
            
            for payment, lease, property_obj in payments:
                # Check if reminder already sent
                existing = await db.execute(
                    select(NotificationLog).where(
                        and_(
                            NotificationLog.rent_payment_id == payment.id,
                            NotificationLog.channel == NotificationChannel.RENT_DUE_REMINDER,
                            NotificationLog.status == NotificationStatus.SENT
                        )
                    )
                )
                
                if existing.scalar_one_or_none():
                    logger.info(f"Reminder already sent for payment {payment.payment_number}")
                    continue
                
                # Get notification template
                template_result = await db.execute(
                    select(NotificationTemplate).where(
                        and_(
                            NotificationTemplate.channel == NotificationChannel.RENT_DUE_REMINDER,
                            NotificationTemplate.is_active == True,
                            NotificationTemplate.is_deleted == False
                        )
                    )
                )
                template = template_result.scalar_one_or_none()
                
                if not template:
                    logger.warning("No active template found for rent due reminders")
                    continue
                
                # Prepare variables
                variables = {
                    'tenant_name': lease.lessee_name,
                    'property_name': property_obj.property_name,
                    'due_date': payment.due_date.strftime('%d %B %Y'),
                    'amount': f"₹{payment.total_amount:,.2f}",
                    'payment_month': payment.payment_month,
                    'lease_number': lease.lease_number
                }
                
                # Send notification
                results = await self.notification_service.send_notification(
                    notification_type=NotificationType.EMAIL.value,
                    recipient_email=lease.lessee_email,
                    recipient_phone=lease.lessee_contact,
                    subject=template.subject,
                    body_template=template.body_template,
                    sms_template=template.sms_template,
                    variables=variables
                )
                
                # Log notification
                for channel, result in results.items():
                    if result:
                        log = NotificationLog(
                            tenant_id=payment.tenant_id,
                            template_id=template.id,
                            channel=NotificationChannel.RENT_DUE_REMINDER,
                            notification_type=NotificationType.EMAIL if channel == 'email' else NotificationType.SMS,
                            recipient_type='tenant',
                            recipient_name=lease.lessee_name,
                            recipient_email=lease.lessee_email if channel == 'email' else None,
                            recipient_phone=lease.lessee_contact if channel == 'sms' else None,
                            subject=template.subject,
                            body=self.notification_service.render_template(template.body_template, variables),
                            property_id=property_obj.id,
                            lease_id=lease.id,
                            rent_payment_id=payment.id,
                            status=NotificationStatus.SENT if result.get('success') else NotificationStatus.FAILED,
                            sent_at=datetime.utcnow() if result.get('success') else None,
                            failed_at=datetime.utcnow() if not result.get('success') else None,
                            error_message=result.get('error'),
                            external_message_id=result.get('message_id'),
                            provider_name=result.get('provider'),
                            variables_used=variables
                        )
                        db.add(log)
                
                logger.info(f"Sent rent due reminder for payment {payment.payment_number}")
            
            await db.commit()
            logger.info(f"Rent due reminder job completed: {len(payments)} reminders processed")
            
        except Exception as e:
            logger.error(f"Error processing rent due reminders: {str(e)}")
            await db.rollback()
    
    async def _process_lease_expiry_alerts(self, db: AsyncSession):
        """
        Process lease expiry alerts
        Send alerts 60 days before expiry
        """
        try:
            # Get date 60 days from now
            expiry_date = date.today() + timedelta(days=60)
            
            # Find all active leases expiring in 60 days
            result = await db.execute(
                select(Lease, Property)
                .join(Property, Property.id == Lease.property_id)
                .where(
                    and_(
                        Lease.lease_end_date == expiry_date,
                        Lease.status == 'active',
                        Lease.is_deleted == False
                    )
                )
            )
            
            leases = result.all()
            logger.info(f"Found {len(leases)} leases expiring in 60 days")
            
            for lease, property_obj in leases:
                # Check if alert already sent
                existing = await db.execute(
                    select(NotificationLog).where(
                        and_(
                            NotificationLog.lease_id == lease.id,
                            NotificationLog.channel == NotificationChannel.LEASE_EXPIRY_ALERT,
                            NotificationLog.status == NotificationStatus.SENT
                        )
                    )
                )
                
                if existing.scalar_one_or_none():
                    logger.info(f"Alert already sent for lease {lease.lease_number}")
                    continue
                
                # Get notification template
                template_result = await db.execute(
                    select(NotificationTemplate).where(
                        and_(
                            NotificationTemplate.channel == NotificationChannel.LEASE_EXPIRY_ALERT,
                            NotificationTemplate.is_active == True,
                            NotificationTemplate.is_deleted == False
                        )
                    )
                )
                template = template_result.scalar_one_or_none()
                
                if not template:
                    logger.warning("No active template found for lease expiry alerts")
                    continue
                
                # Prepare variables
                variables = {
                    'tenant_name': lease.lessee_name,
                    'property_name': property_obj.property_name,
                    'expiry_date': lease.lease_end_date.strftime('%d %B %Y'),
                    'lease_number': lease.lease_number,
                    'monthly_rent': f"₹{lease.monthly_rent:,.2f}",
                    'days_remaining': '60'
                }
                
                # Send notification
                results = await self.notification_service.send_notification(
                    notification_type=NotificationType.EMAIL.value,
                    recipient_email=lease.lessee_email,
                    recipient_phone=lease.lessee_contact,
                    subject=template.subject,
                    body_template=template.body_template,
                    sms_template=template.sms_template,
                    variables=variables
                )
                
                # Log notification
                for channel, result in results.items():
                    if result:
                        log = NotificationLog(
                            tenant_id=lease.tenant_id,
                            template_id=template.id,
                            channel=NotificationChannel.LEASE_EXPIRY_ALERT,
                            notification_type=NotificationType.EMAIL if channel == 'email' else NotificationType.SMS,
                            recipient_type='tenant',
                            recipient_name=lease.lessee_name,
                            recipient_email=lease.lessee_email if channel == 'email' else None,
                            recipient_phone=lease.lessee_contact if channel == 'sms' else None,
                            subject=template.subject,
                            body=self.notification_service.render_template(template.body_template, variables),
                            property_id=property_obj.id,
                            lease_id=lease.id,
                            status=NotificationStatus.SENT if result.get('success') else NotificationStatus.FAILED,
                            sent_at=datetime.utcnow() if result.get('success') else None,
                            failed_at=datetime.utcnow() if not result.get('success') else None,
                            error_message=result.get('error'),
                            external_message_id=result.get('message_id'),
                            provider_name=result.get('provider'),
                            variables_used=variables
                        )
                        db.add(log)
                
                logger.info(f"Sent lease expiry alert for lease {lease.lease_number}")
            
            await db.commit()
            logger.info(f"Lease expiry alert job completed: {len(leases)} alerts processed")
            
        except Exception as e:
            logger.error(f"Error processing lease expiry alerts: {str(e)}")
            await db.rollback()
    
    async def _process_overdue_payment_reminders(self, db: AsyncSession):
        """
        Process overdue payment reminders
        Send reminders for payments overdue by more than 7 days
        """
        try:
            # Get date 7 days ago
            overdue_date = date.today() - timedelta(days=7)
            
            # Find all overdue payments
            result = await db.execute(
                select(RentPayment, Lease, Property)
                .join(Lease, Lease.id == RentPayment.lease_id)
                .join(Property, Property.id == Lease.property_id)
                .where(
                    and_(
                        RentPayment.due_date <= overdue_date,
                        RentPayment.payment_status.in_(['pending', 'partial']),
                        RentPayment.is_deleted == False,
                        Lease.status == 'active'
                    )
                )
            )
            
            payments = result.all()
            logger.info(f"Found {len(payments)} overdue payments")
            
            for payment, lease, property_obj in payments:
                # Check if sent reminder in last 7 days
                seven_days_ago = datetime.utcnow() - timedelta(days=7)
                existing = await db.execute(
                    select(NotificationLog).where(
                        and_(
                            NotificationLog.rent_payment_id == payment.id,
                            NotificationLog.channel == NotificationChannel.PAYMENT_OVERDUE,
                            NotificationLog.status == NotificationStatus.SENT,
                            NotificationLog.sent_at >= seven_days_ago
                        )
                    )
                )
                
                if existing.scalar_one_or_none():
                    logger.info(f"Overdue reminder already sent recently for {payment.payment_number}")
                    continue
                
                # Get notification template
                template_result = await db.execute(
                    select(NotificationTemplate).where(
                        and_(
                            NotificationTemplate.channel == NotificationChannel.PAYMENT_OVERDUE,
                            NotificationTemplate.is_active == True,
                            NotificationTemplate.is_deleted == False
                        )
                    )
                )
                template = template_result.scalar_one_or_none()
                
                if not template:
                    logger.warning("No active template found for overdue payment reminders")
                    continue
                
                # Prepare variables
                variables = {
                    'tenant_name': lease.lessee_name,
                    'property_name': property_obj.property_name,
                    'due_date': payment.due_date.strftime('%d %B %Y'),
                    'amount': f"₹{payment.outstanding_amount:,.2f}",
                    'payment_month': payment.payment_month,
                    'lease_number': lease.lease_number,
                    'days_overdue': str(payment.days_overdue)
                }
                
                # Send notification
                results = await self.notification_service.send_notification(
                    notification_type=NotificationType.EMAIL.value,
                    recipient_email=lease.lessee_email,
                    recipient_phone=lease.lessee_contact,
                    subject=template.subject,
                    body_template=template.body_template,
                    sms_template=template.sms_template,
                    variables=variables
                )
                
                # Log notification
                for channel, result in results.items():
                    if result:
                        log = NotificationLog(
                            tenant_id=payment.tenant_id,
                            template_id=template.id,
                            channel=NotificationChannel.PAYMENT_OVERDUE,
                            notification_type=NotificationType.EMAIL if channel == 'email' else NotificationType.SMS,
                            recipient_type='tenant',
                            recipient_name=lease.lessee_name,
                            recipient_email=lease.lessee_email if channel == 'email' else None,
                            recipient_phone=lease.lessee_contact if channel == 'sms' else None,
                            subject=template.subject,
                            body=self.notification_service.render_template(template.body_template, variables),
                            property_id=property_obj.id,
                            lease_id=lease.id,
                            rent_payment_id=payment.id,
                            status=NotificationStatus.SENT if result.get('success') else NotificationStatus.FAILED,
                            sent_at=datetime.utcnow() if result.get('success') else None,
                            failed_at=datetime.utcnow() if not result.get('success') else None,
                            error_message=result.get('error'),
                            external_message_id=result.get('message_id'),
                            provider_name=result.get('provider'),
                            variables_used=variables
                        )
                        db.add(log)
                
                logger.info(f"Sent overdue reminder for payment {payment.payment_number}")
            
            await db.commit()
            logger.info(f"Overdue payment reminder job completed: {len(payments)} reminders processed")
            
        except Exception as e:
            logger.error(f"Error processing overdue payment reminders: {str(e)}")
            await db.rollback()
    
    async def _wait_until_time(self, hour: int, minute: int = 0):
        """Wait until specific time of day"""
        now = datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if target <= now:
            # If time has passed today, wait until tomorrow
            target = target + timedelta(days=1)
        
        wait_seconds = (target - now).total_seconds()
        await asyncio.sleep(wait_seconds)
    
    async def _wait_until_weekday(self, weekday: int, hour: int, minute: int = 0):
        """Wait until specific weekday and time (0=Monday, 6=Sunday)"""
        now = datetime.now()
        days_ahead = weekday - now.weekday()
        
        if days_ahead < 0 or (days_ahead == 0 and now.hour >= hour):
            # Target day has passed this week, wait until next week
            days_ahead += 7
        
        target = now + timedelta(days=days_ahead)
        target = target.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        wait_seconds = (target - now).total_seconds()
        await asyncio.sleep(wait_seconds)


# Module-level functions
async def start_notification_scheduler():
    """Start the notification scheduler"""
    global _scheduler_running, _scheduler_task
    
    if _scheduler_running:
        logger.warning("Notification scheduler already running")
        return
    
    _scheduler_running = True
    scheduler = NotificationScheduler()
    _scheduler_task = asyncio.create_task(scheduler.start())
    logger.info("Notification scheduler started")


async def stop_notification_scheduler():
    """Stop the notification scheduler"""
    global _scheduler_running, _scheduler_task
    
    if not _scheduler_running:
        return
    
    _scheduler_running = False
    
    if _scheduler_task:
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
    
    logger.info("Notification scheduler stopped")
