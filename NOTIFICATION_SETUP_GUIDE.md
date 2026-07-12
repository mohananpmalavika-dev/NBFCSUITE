# Notification System - Quick Setup Guide 🚀

## 📋 Overview

This guide will help you set up and configure the automated notification system for Property & Rent Management in under 10 minutes.

---

## ⚡ Quick Start (5 Steps)

### Step 1: Set Environment Variables

Create a `.env` file or add these to your existing environment:

```env
# Email Configuration (Gmail Example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@nbfcsuite.com
SMTP_FROM_NAME=NBFC Suite Property Management

# SMS Configuration (Twilio - Optional)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_FROM_NUMBER=+1234567890
```

### Step 2: Run Database Migrations

The notification tables will be created automatically when you start the application.

```bash
# Tables created:
# - notification_templates
# - notification_logs
# - notification_preferences
# - notification_schedules
# - notification_queue
```

### Step 3: Create Default Templates

Access the API or use the UI to create notification templates:

**Via UI:**
1. Go to `/property-management/notifications`
2. Admin section will have template management

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/notifications/templates \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @rent_due_template.json
```

### Step 4: Start the Scheduler

Add to your `main.py` startup:

```python
from backend.services.notifications import start_notification_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await start_notification_scheduler()
    
    yield
    
    # Shutdown
    from backend.services.notifications import stop_notification_scheduler
    await stop_notification_scheduler()
```

### Step 5: Configure User Preferences

Each user should configure their preferences:

1. Go to `/property-management/notifications`
2. Enable/disable channels (Email, SMS)
3. Enter contact information
4. Select notification types to receive
5. Click "Save Changes"

---

## 📧 Gmail Setup (Recommended for Testing)

### Option 1: App Password (Recommended)

1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate App Password:
   - Go to Security → App passwords
   - Select "Mail" and "Other (Custom name)"
   - Copy the 16-character password
4. Use this password in `SMTP_PASSWORD`

### Option 2: Less Secure App Access (Not Recommended)

1. Go to Google Account settings
2. Security → Less secure app access
3. Turn ON
4. Use your regular Gmail password

---

## 📱 Twilio Setup (Optional)

### If You Want SMS Notifications:

1. Sign up at [twilio.com](https://www.twilio.com)
2. Get a phone number ($1/month)
3. Copy Account SID and Auth Token
4. Add to environment variables
5. Test with the phone number

### If You Don't Want SMS:

Simply don't set the Twilio environment variables. The system will:
- Still work for Email notifications
- Log SMS to console (mock mode)
- Not throw errors

---

## 🎨 Default Templates

### Template 1: Rent Due Reminder

**File:** `rent_due_template.json`
```json
{
  "template_code": "rent_due_reminder",
  "template_name": "Rent Due Reminder",
  "channel": "rent_due_reminder",
  "notification_type": "email",
  "subject": "Rent Payment Reminder - {{ property_name }}",
  "body_template": "<html><body><h2>Rent Payment Reminder</h2><p>Dear {{ tenant_name }},</p><p>Your rent payment for <strong>{{ property_name }}</strong> is due on <strong>{{ due_date }}</strong>.</p><p><strong>Amount:</strong> {{ amount }}<br><strong>Month:</strong> {{ payment_month }}</p><p>Thank you!</p></body></html>",
  "sms_template": "Rent reminder for {{ property_name }}. Due: {{ due_date }}. Amount: {{ amount }}",
  "send_days_before": 3,
  "is_active": true,
  "priority": "high"
}
```

### Template 2: Lease Expiry Alert

**File:** `lease_expiry_template.json`
```json
{
  "template_code": "lease_expiry_alert",
  "template_name": "Lease Expiry Alert",
  "channel": "lease_expiry_alert",
  "notification_type": "email",
  "subject": "Lease Expiry Notice - {{ property_name }}",
  "body_template": "<html><body><h2>Lease Expiry Notice</h2><p>Dear {{ tenant_name }},</p><p>Your lease for <strong>{{ property_name }}</strong> will expire on <strong>{{ expiry_date }}</strong> ({{ days_remaining }} days).</p><p>Please contact us for renewal.</p></body></html>",
  "sms_template": "Lease expiring in {{ days_remaining }} days. Contact us for renewal. Property: {{ property_name }}",
  "send_days_before": 60,
  "is_active": true,
  "priority": "high"
}
```

### Template 3: Payment Overdue

**File:** `payment_overdue_template.json`
```json
{
  "template_code": "payment_overdue",
  "template_name": "Payment Overdue Notice",
  "channel": "payment_overdue",
  "notification_type": "email",
  "subject": "Urgent: Overdue Payment - {{ property_name }}",
  "body_template": "<html><body><h2 style='color: red;'>Payment Overdue</h2><p>Dear {{ tenant_name }},</p><p>Your rent payment for {{ property_name }} was due on {{ due_date }} and is now <strong>{{ days_overdue }} days overdue</strong>.</p><p><strong>Amount:</strong> {{ amount }}</p><p>Please make payment immediately to avoid late fees.</p></body></html>",
  "sms_template": "URGENT: Rent payment overdue by {{ days_overdue }} days. Amount: {{ amount }}. Pay now to avoid late fees.",
  "is_active": true,
  "priority": "urgent"
}
```

---

## 🧪 Testing

### Test 1: Send Manual Notification

```bash
curl -X POST http://localhost:8000/api/v1/notifications/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "test@example.com",
    "channel": "rent_due_reminder",
    "subject": "Test Notification",
    "message": "This is a test email from the notification system"
  }'
```

### Test 2: Check Notification History

1. Go to `/property-management/notifications/history`
2. You should see the test notification
3. Check status (sent/delivered/failed)

### Test 3: Update Preferences

1. Go to `/property-management/notifications`
2. Toggle Email ON
3. Enter your email address
4. Enable "Rent Due Reminders"
5. Save changes
6. Send another test

---

## 🔍 Verification Checklist

- [ ] Environment variables set
- [ ] Database tables created (check `/debug/tables`)
- [ ] Templates created (at least 3)
- [ ] User preferences configured
- [ ] Scheduler started (check logs)
- [ ] Test notification sent successfully
- [ ] Email received (check spam folder)
- [ ] Notification appears in history

---

## ⏰ Scheduler Jobs

The system runs these jobs automatically:

| Job | Schedule | Checks | Action |
|-----|----------|--------|--------|
| Rent Due | Daily 9 AM | Payments due in 3 days | Send reminder |
| Lease Expiry | Monday 10 AM | Leases expiring in 60 days | Send alert |
| Payment Overdue | Daily 11 AM | Payments overdue 7+ days | Send notice |

**No manual intervention required!**

---

## 🎯 Common Use Cases

### Use Case 1: New Tenant

1. Create lease in system
2. System automatically:
   - Sends welcome email
   - Schedules rent reminders
   - Adds lease expiry alert

### Use Case 2: Payment Due

1. System checks daily at 9 AM
2. Finds rent due in 3 days
3. Sends email + SMS (if enabled)
4. Logs delivery status
5. Tenant receives reminder

### Use Case 3: Lease Expiring

1. System checks weekly on Monday
2. Finds lease expiring in 60 days
3. Sends renewal reminder
4. Tracks delivery
5. Follow-up at 30 days

### Use Case 4: Payment Overdue

1. System checks daily at 11 AM
2. Finds payment overdue 7+ days
3. Sends urgent notice
4. Repeats weekly until paid
5. Escalates to legal notice

---

## 🎨 Customization

### Custom Email Template

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: #1a56db; color: white; padding: 20px; }
    .content { padding: 20px; }
    .footer { background: #f3f4f6; padding: 15px; text-align: center; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>{{ company_name }}</h1>
    </div>
    <div class="content">
      <h2>{{ subject_line }}</h2>
      <p>Dear {{ tenant_name }},</p>
      {{ message_body }}
    </div>
    <div class="footer">
      <p>{{ company_address }}</p>
      <p>{{ contact_email }} | {{ contact_phone }}</p>
    </div>
  </div>
</body>
</html>
```

### Custom Variables

Add to template:
```json
{
  "available_variables": [
    "tenant_name",
    "property_name",
    "due_date",
    "amount",
    "custom_field_1",
    "custom_field_2"
  ]
}
```

---

## 🐛 Troubleshooting

### Problem: Emails not sending

**Solution:**
```bash
# Check logs
tail -f backend.log | grep "notification"

# Test SMTP connection
python -c "import smtplib; s = smtplib.SMTP('smtp.gmail.com', 587); s.starttls(); s.login('your@email.com', 'password'); print('Success')"

# Verify environment variables
echo $SMTP_HOST
echo $SMTP_USERNAME
```

### Problem: Scheduler not running

**Solution:**
```python
# Add debug logging
logger.info("Starting notification scheduler...")
await start_notification_scheduler()
logger.info("Scheduler started successfully")
```

### Problem: Notifications not in history

**Solution:**
1. Check database connection
2. Verify tenant_id matches
3. Check `is_deleted` flag
4. Review filters applied

---

## 📚 Additional Resources

- [Full Documentation](./NOTIFICATION_SYSTEM_COMPLETE.md)
- [API Reference](http://localhost:8000/docs#/Notifications)
- [Template Variables Guide](./NOTIFICATION_SYSTEM_COMPLETE.md#template-variables)
- [Error Codes](./NOTIFICATION_SYSTEM_COMPLETE.md#troubleshooting)

---

## ✅ Production Checklist

Before going live:

- [ ] Use production SMTP server (not Gmail)
- [ ] Set up SPF/DKIM records
- [ ] Configure SMTP relay limits
- [ ] Set up SMS provider account
- [ ] Load test with 1000+ emails
- [ ] Set up monitoring alerts
- [ ] Configure retry limits
- [ ] Add unsubscribe links
- [ ] Test all templates
- [ ] Review error handling
- [ ] Set up backup notification channel
- [ ] Configure rate limiting
- [ ] Add admin notifications for failures

---

## 🎉 You're Ready!

The notification system is now fully configured and ready to use. The system will automatically:

✅ Send rent reminders 3 days before due  
✅ Alert about lease expiry 60 days ahead  
✅ Notify about overdue payments 7+ days after due  
✅ Track all delivery statuses  
✅ Honor user preferences  
✅ Prevent duplicate sends  
✅ Log all errors  
✅ Retry on failures  

**No manual work required - it's all automated!**

---

**Need Help?** Check the logs or documentation, or contact support.

**Status**: ✅ Ready for Production  
**Version**: 1.0.0  
**Last Updated**: July 11, 2026
