# License Renewal Reminder System

## Overview
The License Renewal Reminder System is an automated background service that monitors license expiration dates and compliance requirements, sending timely notifications to stakeholders.

## Features

### 1. Automated Reminder Checks
- **Daily Checks**: System runs daily at 9 AM to check all licenses
- **Smart Alerts**: Sends reminders at configured intervals (e.g., 90, 60, 30, 15, 7 days before expiry)
- **Compliance Monitoring**: Tracks compliance check due dates

### 2. Escalation Management
- **Automatic Escalation**: When licenses reach critical expiry threshold
- **Priority Notifications**: High-priority alerts for critical licenses
- **Custom Escalation Lists**: Configurable escalation recipients

### 3. Reminder Types

#### Renewal Reminders
- Sent based on `alert_days_before_expiry` configuration
- Includes license details, expiry date, renewal fee
- Tracks reminder count and last sent date

#### Compliance Reminders
- Sent 30, 15, 7 days before compliance check due date
- Includes current compliance status
- Suggests action items

#### Escalation Notices
- Triggered when license reaches submission deadline
- Sent to escalation recipients
- Marked as high priority

### 4. Status Updates
- Automatically updates license status to `PENDING_RENEWAL`
- Marks expired licenses as `EXPIRED`
- Updates renewal status to `PENDING`

## Configuration

### License Alert Configuration
```python
{
    "alert_enabled": true,
    "alert_days_before_expiry": [90, 60, 30, 15, 7],
    "renewal_notice_days": 60,
    "renewal_submission_deadline_days": 30,
    "alert_recipients": ["user1@example.com", "user2@example.com"],
    "escalation_to": ["manager@example.com", "admin@example.com"],
    "reminder_frequency": "weekly"
}
```

### Scheduler Configuration
The scheduler runs three main tasks:

1. **Reminder Check** - Daily at 9:00 AM
   - Checks all licenses for renewal/compliance needs
   - Sends appropriate notifications

2. **Process Pending Reminders** - Every hour
   - Processes unsent reminders
   - Retries failed notifications (max 3 attempts)

3. **Daily Report** - Daily at 6:00 PM
   - Generates statistics report
   - Summarizes day's reminder activity

## API Endpoints

### Trigger Manual Reminder Check
```
POST /api/v1/legal/licenses/reminders/trigger-check
```
Manually triggers the reminder check process.

**Response:**
```json
{
  "success": true,
  "message": "Reminder check completed",
  "data": {
    "total_checked": 50,
    "renewal_reminders_sent": 5,
    "compliance_reminders_sent": 2,
    "escalations_sent": 1,
    "errors": []
  }
}
```

### Get Reminder Statistics
```
GET /api/v1/legal/licenses/reminders/statistics?days=30
```
Returns reminder statistics for the specified period.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_reminders": 150,
    "sent": 145,
    "pending": 3,
    "failed": 2,
    "by_type": {
      "renewal": 100,
      "compliance": 45,
      "escalation": 5
    },
    "escalations": 5
  }
}
```

## Database Schema

### LicenseReminder Table
Stores all reminder records with the following key fields:
- `reminder_type`: renewal, compliance, escalation
- `reminder_date`: When the reminder was created
- `days_before_due`: Days remaining until due date
- `is_sent`: Whether reminder was successfully sent
- `recipients`: List of notification recipients
- `delivery_status`: sent, failed, pending
- `is_escalated`: Whether this is an escalation

## Integration with Notification System

The reminder service creates notification records that can be processed by:
- Email service
- SMS service
- In-app notifications
- Webhook notifications

## Monitoring & Logging

### Log Levels
- **INFO**: Normal operation, reminders sent
- **WARNING**: Escalations triggered, retry attempts
- **ERROR**: Failed to send reminders, system errors

### Key Metrics
- Total reminders sent per day
- Success/failure rate
- Average processing time
- Escalation count

## Best Practices

1. **Configure Alert Days Appropriately**
   - Consider authority processing time
   - Account for document preparation time
   - Include buffer for delays

2. **Set Up Escalation Lists**
   - Include decision makers
   - Add backup contacts
   - Consider time zones

3. **Monitor Failed Reminders**
   - Check delivery status regularly
   - Investigate failures
   - Update contact information

4. **Review Reminder Reports**
   - Daily statistics
   - Identify patterns
   - Optimize alert timing

## Troubleshooting

### Reminders Not Being Sent
1. Check if scheduler is running
2. Verify `alert_enabled` is true
3. Confirm recipients list is populated
4. Check notification service status

### Duplicate Reminders
1. Verify alert days configuration
2. Check reminder history
3. Ensure scheduler isn't running multiple times

### Missing Escalations
1. Verify `escalation_to` is configured
2. Check `renewal_submission_deadline_days`
3. Confirm escalation threshold logic

## Future Enhancements

- [ ] SMS notification support
- [ ] WhatsApp integration
- [ ] Customizable reminder templates
- [ ] Machine learning for optimal reminder timing
- [ ] Multi-language support
- [ ] Mobile push notifications
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Slack/Teams integration

## Dependencies

```
APScheduler>=3.10.0  # Task scheduling
```

Add to `requirements.txt`:
```
apscheduler==3.10.4
```

## Installation

1. Install dependencies:
```bash
pip install apscheduler
```

2. The scheduler starts automatically with the application

3. Verify scheduler is running:
```bash
# Check logs for "License reminder scheduler started"
```

## Testing

### Manual Testing
```python
# Trigger immediate reminder check
curl -X POST http://localhost:8000/api/v1/legal/licenses/reminders/trigger-check \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get statistics
curl http://localhost:8000/api/v1/legal/licenses/reminders/statistics?days=7 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Unit Testing
```python
# Test reminder check logic
async def test_reminder_check():
    async with AsyncSessionLocal() as db:
        stats = await LicenseReminderService.check_and_send_reminders(db)
        assert stats['total_checked'] > 0
```

## Support

For issues or questions:
1. Check application logs
2. Review configuration
3. Consult this documentation
4. Contact system administrator
