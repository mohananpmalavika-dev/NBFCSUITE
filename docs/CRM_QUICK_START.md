# CRM Account Management - Quick Start Guide

## Overview
Get started with the CRM Account Management module in 5 minutes.

## Prerequisites
- Backend server running on http://localhost:8000
- Frontend server running on http://localhost:3000
- PostgreSQL database configured

## Step 1: Access CRM Module

Navigate to: **http://localhost:3000/crm/accounts**

You'll see the Account List page with:
- Search bar
- Status and type filters
- Stats cards (Total, Active, Prospects, Customers)
- Account table with pagination

## Step 2: Create Your First Account

1. Click **"+ New Account"** button
2. Fill in the form:
   - **Account Name**: "Acme Corporation" (required)
   - **Account Type**: Select "Business"
   - **Status**: Select "Prospect"
   - **Industry**: Select "Technology"
   - **Email**: contact@acme.com
   - **Phone**: +91-22-12345678
   - **PAN Number**: AAACT1234F
   - **Billing City**: Mumbai
   - **Billing State**: Maharashtra
3. Click **"Create Account"**

You'll be redirected to the Account 360 view.

## Step 3: Explore Account 360 View

The Account 360 view shows:
- **Header**: Account name, status, metrics
- **Tabs**:
  - **Overview**: Account details, address
  - **Contacts**: List of contacts (initially empty)
  - **Relationships**: Account relationships
  - **Activities**: Recent activities
  - **Child Accounts**: Sub-accounts

## Step 4: Add a Contact

1. Click **"Add Contact"** button
2. Fill in the form:
   - **Salutation**: "Mr"
   - **First Name**: "John" (required)
   - **Last Name**: "Doe" (required)
   - **Contact Type**: "Primary"
   - **Job Title**: "CEO"
   - **Email**: john.doe@acme.com
   - **Mobile**: +91-98765-43210
3. Click **"Create Contact"**

You'll return to the Account 360 view with the new contact visible.

## Step 5: Add a Relationship

1. Create a second account (repeat Step 2)
2. Go back to first account's 360 view
3. Click **"Relationships"** tab
4. Click **"Add Relationship"**
5. Fill in the form:
   - **Primary Account**: (auto-selected)
   - **Related Account**: Select the second account
   - **Relationship Type**: "Partner"
   - **Strength**: "Strong"
   - **Description**: "Strategic partnership"
6. Click **"Create Relationship"**

## Step 6: Search and Filter

Back on the Account List page:

1. **Search**: Type in search box to find accounts by name, email, or phone
2. **Filter by Status**: Select "Prospect", "Customer", or "Active"
3. **Filter by Type**: Select "Business", "Individual", etc.
4. **Pagination**: Navigate through pages if you have many accounts

## Common Operations

### Edit an Account
1. Go to Account 360 view
2. Click **"Edit Account"** button
3. Modify fields
4. Click **"Update Account"**

### Edit a Contact
1. Go to Account 360 view
2. Click **"Contacts"** tab
3. Click **"Edit"** next to a contact
4. Modify fields
5. Click **"Update Contact"**

### Delete an Account
1. On Account List page
2. Click **"Delete"** in the Actions column
3. Confirm deletion
4. Account is soft-deleted (can be recovered)

### View Metrics
Account 360 view header shows:
- **Total Revenue**: Sum of all opportunities
- **Opportunities**: Count of opportunities
- **Contacts**: Number of contacts
- **Relationships**: Number of relationships
- **Child Accounts**: Number of sub-accounts

## API Testing with Swagger

Visit: **http://localhost:8000/docs**

Try these endpoints:
1. **POST /api/v1/crm/accounts** - Create account
2. **GET /api/v1/crm/accounts** - List accounts
3. **GET /api/v1/crm/accounts/{id}/360** - Get 360 view
4. **POST /api/v1/crm/accounts/contacts** - Create contact

## Sample Data

Use this JSON to create a test account via API:

```json
{
  "account_name": "Tech Solutions India Pvt Ltd",
  "account_type": "business",
  "status": "customer",
  "industry": "technology",
  "annual_revenue": 50000000,
  "employee_count": "100-500",
  "pan_number": "AABCT1234F",
  "gst_number": "29AABCT1234F1Z5",
  "email": "info@techsolutions.in",
  "phone": "+91-80-12345678",
  "mobile": "+91-98765-43210",
  "website": "https://www.techsolutions.in",
  "billing_address_line1": "123, Tech Park",
  "billing_city": "Bangalore",
  "billing_state": "Karnataka",
  "billing_pincode": "560001",
  "description": "Leading IT solutions provider in India"
}
```

## Keyboard Shortcuts

- **Ctrl/Cmd + K**: Focus search box
- **Esc**: Close modal/go back
- **Enter**: Submit form

## Tips & Tricks

1. **Quick Navigation**: Use browser back/forward buttons
2. **Tab Navigation**: Use Tab key in forms
3. **Batch Operations**: Select multiple accounts (future feature)
4. **Export Data**: Use browser print to PDF (or wait for CSV export)
5. **Responsive Design**: Works on mobile and tablet

## Troubleshooting

### "Failed to load accounts"
- Check backend is running on port 8000
- Check database connection
- Check browser console for errors

### "Account not found"
- Account may have been deleted
- Check account ID in URL
- Try refreshing the page

### Forms not saving
- Check required fields are filled
- Check console for validation errors
- Ensure backend API is accessible

### Blank pages
- Check browser console for errors
- Verify routes are correct
- Clear browser cache and reload

## Next Steps

After getting familiar with basic operations:

1. **Explore Advanced Features**:
   - Create multiple contacts per account
   - Build complex relationship networks
   - Use filters to segment accounts

2. **Integration**:
   - Link accounts to opportunities
   - Connect with marketing campaigns
   - Generate reports

3. **Customization**:
   - Add custom fields (requires backend changes)
   - Customize status values
   - Add custom relationship types

4. **Workflows**:
   - Set up automated follow-ups
   - Create account scoring rules
   - Configure territory assignment

## Support Resources

- **Full Documentation**: See `CRM_ACCOUNT_MANAGEMENT_IMPLEMENTATION.md`
- **API Documentation**: http://localhost:8000/docs
- **Database Schema**: See implementation docs
- **Component Code**: See `frontend/apps/admin-portal/src/components/crm/`

## Summary

You now know how to:
- ✅ Create accounts
- ✅ Add contacts
- ✅ Create relationships
- ✅ Search and filter
- ✅ Navigate the 360 view
- ✅ Edit and delete records

**Happy CRM-ing! 🚀**
