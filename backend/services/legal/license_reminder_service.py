"""
License Renewal Reminder Service
Automated reminder system for license renewals and compliance checks
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List
from datetime import date, datetime, timedelta
import logging

from .license_models import (
    License,
    LicenseReminder,
    LicenseStatus,
    RenewalStatus,
    ComplianceStatus,
)
from backend.shared.database.notification_models import (
    NotificationTemplate,
    Notification,
)

logger = logging.getLogger(__name__)


class LicenseReminderService:
    """Service for automated license renewal reminders"""

    @staticmethod
    async def check_and_send_reminders(db: AsyncSession) -> dict:
        """
        Check all licenses and send renewal/compliance reminders
        Returns statistics about reminders sent
        """
        stats = {
            'total_checked': 0,
            'renewal_reminders_sent': 0,
            'compliance_reminders_sent': 0,
            'escalations_sent': 0,
            'errors': []
        }

        try:
            # Check for licenses needing renewal reminders
            renewal_stats = await LicenseReminderService._check_renewal_reminders(db)
            stats['renewal_reminders_sent'] = renewal_stats['sent']
            stats['escalations_sent'] += renewal_stats['escalations']

            # Check for licenses needing compliance check reminders
            compliance_stats = await LicenseReminderService._check_compliance_reminders(db)
            stats['compliance_reminders_sent'] = compliance_stats['sent']

            # Update expired licenses status
            await LicenseReminderService._update_expired_licenses(db)

            await db.commit()
            logger.info(f"Reminder check completed: {stats}")

        except Exception as e:
            logger.error(f"Error in reminder check: {e}")
            stats['errors'].append(str(e))
            await db.rollback()

        return stats

    @staticmethod
    async def _check_renewal_reminders(db: AsyncSession) -> dict:
        """Check and send renewal reminders"""
        stats = {'sent': 0, 'escalations': 0}

        today = date.today()

        # Get all active, renewable licenses that are not perpetual
        query = select(License).where(
            and_(
                License.is_deleted == False,
                License.status == LicenseStatus.ACTIVE,
                License.is_renewable == True,
                License.is_perpetual == False,
                License.expiry_date.isnot(None),
                License.expiry_date > today
            )
        )

        result = await db.execute(query)
        licenses = result.scalars().all()

        for license in licenses:
            days_until_expiry = (license.expiry_date - today).days

            # Check if reminder needs to be sent based on configured alert days
            if license.alert_enabled and license.alert_days_before_expiry:
                for alert_days in license.alert_days_before_expiry:
                    if days_until_expiry == alert_days:
                        # Send reminder
                        reminder_sent = await LicenseReminderService._send_renewal_reminder(
                            db, license, days_until_expiry
                        )
                        if reminder_sent:
                            stats['sent'] += 1

                        # Check if escalation is needed
                        if days_until_expiry <= license.renewal_submission_deadline_days:
                            if not license.escalation_triggered:
                                escalation_sent = await LicenseReminderService._send_escalation(
                                    db, license, days_until_expiry
                                )
                                if escalation_sent:
                                    license.escalation_triggered = True
                                    license.escalation_date = datetime.utcnow()
                                    stats['escalations'] += 1

            # Update license status if approaching expiry
            if days_until_expiry <= license.renewal_notice_days:
                if license.renewal_status == RenewalStatus.NOT_REQUIRED:
                    license.renewal_status = RenewalStatus.PENDING
                    license.status = LicenseStatus.PENDING_RENEWAL

        return stats

    @staticmethod
    async def _check_compliance_reminders(db: AsyncSession) -> dict:
        """Check and send compliance check reminders"""
        stats = {'sent': 0}

        today = date.today()

        # Get licenses with upcoming compliance checks
        query = select(License).where(
            and_(
                License.is_deleted == False,
                License.status.in_([LicenseStatus.ACTIVE, LicenseStatus.PENDING_RENEWAL]),
                License.next_compliance_check_date.isnot(None),
                License.next_compliance_check_date <= today + timedelta(days=30)
            )
        )

        result = await db.execute(query)
        licenses = result.scalars().all()

        for license in licenses:
            days_until_check = (license.next_compliance_check_date - today).days

            # Send reminder 30, 15, 7 days before due
            if days_until_check in [30, 15, 7, 0]:
                reminder_sent = await LicenseReminderService._send_compliance_reminder(
                    db, license, days_until_check
                )
                if reminder_sent:
                    stats['sent'] += 1

        return stats

    @staticmethod
    async def _update_expired_licenses(db: AsyncSession):
        """Update status of expired licenses"""
        today = date.today()

        query = select(License).where(
            and_(
                License.is_deleted == False,
                License.is_perpetual == False,
                License.expiry_date.isnot(None),
                License.expiry_date < today,
                License.status != LicenseStatus.EXPIRED
            )
        )

        result = await db.execute(query)
        expired_licenses = result.scalars().all()

        for license in expired_licenses:
            license.status = LicenseStatus.EXPIRED
            logger.info(f"License {license.license_number} marked as expired")

    @staticmethod
    async def _send_renewal_reminder(
        db: AsyncSession,
        license: License,
        days_until_expiry: int
    ) -> bool:
        """Send renewal reminder notification"""
        try:
            # Create reminder record
            reminder = LicenseReminder(
                license_id=license.id,
                reminder_type='renewal',
                reminder_date=datetime.utcnow(),
                days_before_due=days_until_expiry,
                recipients=license.alert_recipients or [],
                subject=f"License Renewal Reminder - {license.license_name}",
                message_body=f"""
Dear Team,

This is a reminder that the following license is expiring soon:

License Name: {license.license_name}
License Number: {license.license_number}
License Type: {license.license_type.value}
Issuing Authority: {license.issuing_authority}
Expiry Date: {license.expiry_date}
Days Until Expiry: {days_until_expiry}

Please initiate the renewal process as soon as possible.

Renewal Fee: {license.renewal_fee} {license.currency}
Renewal Notice Days: {license.renewal_notice_days}

For more details, please log in to the system and view the license details.

Best regards,
License Management System
                """,
                is_sent=False,
            )

            db.add(reminder)

            # Update last alert sent
            license.last_alert_sent = datetime.utcnow()
            license.total_reminders_sent += 1

            # Create notification (if notification system is available)
            await LicenseReminderService._create_notification(
                db,
                license,
                'renewal_reminder',
                reminder.subject,
                reminder.message_body,
                license.alert_recipients
            )

            logger.info(
                f"Renewal reminder created for license {license.license_number}"
            )
            return True

        except Exception as e:
            logger.error(f"Error sending renewal reminder: {e}")
            return False

    @staticmethod
    async def _send_compliance_reminder(
        db: AsyncSession,
        license: License,
        days_until_check: int
    ) -> bool:
        """Send compliance check reminder notification"""
        try:
            # Create reminder record
            reminder = LicenseReminder(
                license_id=license.id,
                reminder_type='compliance',
                reminder_date=datetime.utcnow(),
                days_before_due=days_until_check,
                recipients=license.alert_recipients or [],
                subject=f"Compliance Check Due - {license.license_name}",
                message_body=f"""
Dear Team,

This is a reminder that a compliance check is due for the following license:

License Name: {license.license_name}
License Number: {license.license_number}
License Type: {license.license_type.value}
Next Compliance Check Due: {license.next_compliance_check_date}
Days Until Check: {days_until_check}
Current Compliance Status: {license.compliance_status.value}

Please schedule and conduct the compliance check.

For more details, please log in to the system and view the license details.

Best regards,
License Management System
                """,
                is_sent=False,
            )

            db.add(reminder)

            # Create notification
            await LicenseReminderService._create_notification(
                db,
                license,
                'compliance_reminder',
                reminder.subject,
                reminder.message_body,
                license.alert_recipients
            )

            logger.info(
                f"Compliance reminder created for license {license.license_number}"
            )
            return True

        except Exception as e:
            logger.error(f"Error sending compliance reminder: {e}")
            return False

    @staticmethod
    async def _send_escalation(
        db: AsyncSession,
        license: License,
        days_until_expiry: int
    ) -> bool:
        """Send escalation notification for urgent renewals"""
        try:
            # Create escalation reminder
            reminder = LicenseReminder(
                license_id=license.id,
                reminder_type='escalation',
                reminder_date=datetime.utcnow(),
                days_before_due=days_until_expiry,
                recipients=license.escalation_to or license.alert_recipients or [],
                subject=f"URGENT: License Expiring Soon - {license.license_name}",
                message_body=f"""
URGENT NOTIFICATION

The following license is expiring in {days_until_expiry} days and renewal has not been initiated:

License Name: {license.license_name}
License Number: {license.license_number}
License Type: {license.license_type.value}
Issuing Authority: {license.issuing_authority}
Expiry Date: {license.expiry_date}
Criticality Level: {license.criticality_level}

Business Impact: {license.business_impact}

IMMEDIATE ACTION REQUIRED

Please initiate the renewal process immediately to avoid license expiry.

Renewal Fee: {license.renewal_fee} {license.currency}
Submission Deadline: {license.expiry_date - timedelta(days=license.renewal_submission_deadline_days)}

For more details, please log in to the system and view the license details.

Best regards,
License Management System
                """,
                is_sent=False,
                is_escalated=True,
                escalated_to=license.escalation_to or [],
            )

            db.add(reminder)

            # Create high-priority notification
            await LicenseReminderService._create_notification(
                db,
                license,
                'escalation',
                reminder.subject,
                reminder.message_body,
                reminder.recipients,
                priority='high'
            )

            logger.warning(
                f"Escalation sent for license {license.license_number}"
            )
            return True

        except Exception as e:
            logger.error(f"Error sending escalation: {e}")
            return False

    @staticmethod
    async def _create_notification(
        db: AsyncSession,
        license: License,
        notification_type: str,
        subject: str,
        message: str,
        recipients: List[str],
        priority: str = 'normal'
    ):
        """Create notification record in the notification system"""
        try:
            # This would integrate with your notification system
            # For now, we'll just log it
            logger.info(
                f"Notification created: Type={notification_type}, "
                f"License={license.license_number}, Recipients={len(recipients)}"
            )

            # TODO: Integrate with actual notification service
            # Example:
            # notification = Notification(
            #     tenant_id=license.tenant_id,
            #     notification_type=notification_type,
            #     subject=subject,
            #     message=message,
            #     recipients=recipients,
            #     priority=priority,
            #     related_entity_type='license',
            #     related_entity_id=license.id,
            # )
            # db.add(notification)

        except Exception as e:
            logger.error(f"Error creating notification: {e}")

    @staticmethod
    async def get_pending_reminders(db: AsyncSession) -> List[LicenseReminder]:
        """Get all pending (unsent) reminders"""
        query = select(LicenseReminder).where(
            and_(
                LicenseReminder.is_sent == False,
                LicenseReminder.send_attempts < 3
            )
        ).order_by(LicenseReminder.reminder_date)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def mark_reminder_sent(
        db: AsyncSession,
        reminder_id: str,
        success: bool,
        error_message: str = None
    ):
        """Mark reminder as sent or failed"""
        query = select(LicenseReminder).where(LicenseReminder.id == reminder_id)
        result = await db.execute(query)
        reminder = result.scalar_one_or_none()

        if reminder:
            reminder.send_attempts += 1
            reminder.last_attempt_at = datetime.utcnow()

            if success:
                reminder.is_sent = True
                reminder.sent_at = datetime.utcnow()
                reminder.delivery_status = 'sent'
            else:
                reminder.delivery_status = 'failed'
                reminder.error_message = error_message

            await db.commit()

    @staticmethod
    async def generate_reminder_report(db: AsyncSession, days: int = 30) -> dict:
        """Generate reminder statistics report"""
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get reminder statistics
        query = select(LicenseReminder).where(
            LicenseReminder.created_at >= start_date
        )
        result = await db.execute(query)
        reminders = result.scalars().all()

        stats = {
            'total_reminders': len(reminders),
            'sent': sum(1 for r in reminders if r.is_sent),
            'pending': sum(1 for r in reminders if not r.is_sent),
            'failed': sum(
                1 for r in reminders 
                if r.send_attempts > 0 and not r.is_sent
            ),
            'by_type': {},
            'escalations': sum(1 for r in reminders if r.is_escalated),
        }

        # Count by type
        for reminder in reminders:
            reminder_type = reminder.reminder_type
            if reminder_type not in stats['by_type']:
                stats['by_type'][reminder_type] = 0
            stats['by_type'][reminder_type] += 1

        return stats
