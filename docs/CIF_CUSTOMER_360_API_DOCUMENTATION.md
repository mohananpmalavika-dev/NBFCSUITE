# CIF/Customer 360 - API Documentation

## Overview

Complete API documentation for Customer Information File (CIF) / Customer 360 module with enhanced features:

- **Customer Timeline & Activity Tracking**
- **Credit Bureau Integration** (CIBIL, Equifax, Experian, CRIF)
- **Aadhaar eKYC** (OTP & Biometric)
- **DigiLocker Integration**

**Base URL**: `https://api.yourcompany.com/api/v1`

**Authentication**: Bearer token required for all endpoints

---

## Table of Contents

1. [Customer Timeline APIs](#customer-timeline-apis)
2. [Credit Bureau APIs](#credit-bureau-apis)
3. [eKYC / Aadhaar APIs](#ekyc-aadhaar-apis)
4. [DigiLocker APIs](#digilocker-apis)
5. [Common Schemas](#common-schemas)
6. [Error Handling](#error-handling)
7. [Environment Configuration](#environment-configuration)

---

## Customer Timeline APIs

### 1. Get Customer Timeline

**Endpoint**: `GET /customers/{customer_id}/timeline`

**Description**: Retrieve customer activity history with advanced filtering

**Query Parameters**:
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50, max: 100): Items per page
- `activity_types` (array[string], optional): Filter by activity types
- `event_category` (string, optional): Filter by category (kyc, loan, payment, etc.)
- `start_date` (datetime, optional): Start date filter
- `end_date` (datetime, optional): End date filter
- `important_only` (boolean, default: false): Show only important events

**Activity Types**:
- Customer: `customer_created`, `customer_updated`, `customer_activated`, `customer_deactivated`, `customer_blacklisted`
- KYC: `kyc_initiated`, `kyc_completed`, `kyc_rejected`, `aadhaar_verified`, `pan_verified`, `video_kyc_completed`, `biometric_captured`
- Document: `document_uploaded`, `document_verified`, `document_rejected`, `document_expired`
- Bureau: `cibil_pulled`, `bureau_report_fetched`, `credit_score_updated`, `risk_rating_changed`
- Loan: `loan_application_submitted`, `loan_approved`, `loan_rejected`, `loan_disbursed`, `loan_closed`
- Payment: `payment_received`, `payment_missed`, `emi_bounced`, `prepayment_done`, `foreclosure_done`
- Collection: `collection_call`, `field_visit`, `payment_promise`, `legal_notice_sent`
- Communication: `sms_sent`, `email_sent`, `whatsapp_sent`, `call_made`

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": 12345,
      "customer_id": 101,
      "activity_type": "aadhaar_verified",
      "title": "Aadhaar verified successfully",
      "description": "Name: John Doe",
      "event_date": "2024-01-15T10:30:00Z",
      "event_category": "kyc",
      "event_source": "api",
      "performed_by": 5,
      "performed_by_name": "System Admin",
      "performed_by_role": "admin",
      "old_value": null,
      "new_value": null,
      "changes": null,
      "metadata": {
        "name": "John Doe",
        "dob": "1990-01-15",
        "address": {...}
      },
      "is_important": true,
      "is_system_generated": true,
      "is_visible_to_customer": false,
      "priority": 1,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 156,
  "page": 1,
  "page_size": 50,
  "pages": 4
}
```

**Example Usage**:
```bash
# Get all timeline events
curl -X GET "https://api.yourcompany.com/api/v1/customers/101/timeline" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by KYC events only
curl -X GET "https://api.yourcompany.com/api/v1/customers/101/timeline?event_category=kyc" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get important events from last 30 days
curl -X GET "https://api.yourcompany.com/api/v1/customers/101/timeline?important_only=true&start_date=2024-01-01" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 2. Get Recent Activities

**Endpoint**: `GET /customers/{customer_id}/timeline/recent`

**Description**: Get N most recent activities

**Query Parameters**:
- `limit` (integer, default: 10, max: 50): Number of recent activities

**Response** (200 OK):
```json
[
  {
    "id": 12345,
    "activity_type": "payment_received",
    "title": "EMI payment received",
    "event_date": "2024-01-15T10:30:00Z",
    "performed_by_name": "Payment Gateway"
  }
]
```

---

### 3. Get Activity Summary

**Endpoint**: `GET /customers/{customer_id}/timeline/summary`

**Description**: Get activity count by type for last N days

**Query Parameters**:
- `days` (integer, default: 30, max: 365): Number of days

**Response** (200 OK):
```json
{
  "customer_id": 101,
  "days": 30,
  "activity_counts": {
    "payment_received": 3,
    "sms_sent": 10,
    "collection_call": 2,
    "document_verified": 1
  }
}
```

---

### 4. Search Timeline

**Endpoint**: `GET /customers/{customer_id}/timeline/search`

**Description**: Search timeline by keyword

**Query Parameters**:
- `q` (string, required, min: 2): Search query
- `limit` (integer, default: 20, max: 50): Maximum results

**Response** (200 OK): Array of timeline activities matching the search

---

### 5. Add Manual Activity/Note

**Endpoint**: `POST /customers/{customer_id}/timeline`

**Description**: Log a manual activity or event

**Request Body**:
```json
{
  "activity_type": "note_added",
  "title": "Customer called for loan inquiry",
  "description": "Customer wants to know about gold loan rates. Interested in 2L loan.",
  "event_category": "communication",
  "metadata": {
    "call_duration": "5 minutes",
    "interested_product": "gold_loan"
  },
  "is_important": false,
  "is_visible_to_customer": false
}
```

**Response** (201 Created): Timeline activity object

---

### 6. Add Quick Note

**Endpoint**: `POST /customers/{customer_id}/timeline/notes`

**Description**: Quick way to add a note

**Query Parameters**:
- `note` (string, required): Note text
- `is_important` (boolean, default: false): Mark as important

**Response** (201 Created): Timeline activity object

**Example**:
```bash
curl -X POST "https://api.yourcompany.com/api/v1/customers/101/timeline/notes?note=Customer+requested+callback&is_important=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 7. Mark as Important

**Endpoint**: `PUT /customers/{customer_id}/timeline/{timeline_id}/important`

**Description**: Flag a timeline event as important

**Response** (200 OK): Updated timeline activity

---

## Credit Bureau APIs

### 1. Pull Credit Report

**Endpoint**: `POST /customers/{customer_id}/bureau/pull`

**Description**: Pull credit report from any bureau

**Request Body**:
```json
{
  "bureau_provider": "cibil",
  "request_purpose": "loan_application"
}
```

**Bureau Providers**:
- `cibil` - CIBIL (TransUnion)
- `equifax` - Equifax
- `experian` - Experian
- `crif` - CRIF High Mark

**Response** (201 Created):
```json
{
  "id": 789,
  "customer_id": 101,
  "bureau_provider": "cibil",
  "bureau_request_id": "CIBIL-20240115103000",
  "request_date": "2024-01-15T10:30:00Z",
  "response_date": "2024-01-15T10:30:02Z",
  "status": "success",
  "credit_score": 750,
  "score_date": "2024-01-15",
  "total_accounts": 5,
  "active_accounts": 3,
  "total_outstanding": 250000.00,
  "recent_enquiries_1m": 1,
  "recent_enquiries_3m": 2,
  "recent_enquiries_6m": 4,
  "recent_enquiries_12m": 8,
  "response_time_ms": 2145,
  "error_message": null,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Example**:
```bash
curl -X POST "https://api.yourcompany.com/api/v1/customers/101/bureau/pull" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bureau_provider": "cibil",
    "request_purpose": "loan_application"
  }'
```

---

### 2. Pull CIBIL Report (Quick)

**Endpoint**: `POST /customers/{customer_id}/bureau/pull-cibil`

**Description**: Convenience endpoint for CIBIL (most common)

**Query Parameters**:
- `request_purpose` (string, default: "loan_application")

**Response** (201 Created): Same as Pull Credit Report

---

### 3. Get Bureau History

**Endpoint**: `GET /customers/{customer_id}/bureau/history`

**Description**: Get all bureau pull history

**Query Parameters**:
- `limit` (integer, default: 10, max: 50)

**Response** (200 OK):
```json
[
  {
    "id": 789,
    "bureau_provider": "cibil",
    "request_date": "2024-01-15T10:30:00Z",
    "status": "success",
    "credit_score": 750,
    "response_time_ms": 2145
  }
]
```

---

### 4. Get Latest Credit Score

**Endpoint**: `GET /customers/{customer_id}/bureau/latest-score`

**Description**: Get most recent credit score

**Response** (200 OK):
```json
{
  "customer_id": 101,
  "credit_score": 750
}
```

**Response** (404 Not Found): If no credit score found

---

### 5. Get Available Providers

**Endpoint**: `GET /customers/{customer_id}/bureau/available-providers`

**Description**: Check which bureau providers are configured

**Response** (200 OK):
```json
{
  "providers": [
    {
      "provider": "cibil",
      "name": "CIBIL",
      "configured": true
    },
    {
      "provider": "equifax",
      "name": "EQUIFAX",
      "configured": false
    },
    {
      "provider": "experian",
      "name": "EXPERIAN",
      "configured": true
    },
    {
      "provider": "crif",
      "name": "CRIF",
      "configured": false
    }
  ],
  "total_configured": 2
}
```

---

## eKYC / Aadhaar APIs

### 1. Initiate Aadhaar OTP

**Endpoint**: `POST /customers/{customer_id}/ekyc/aadhaar/otp/initiate`

**Description**: Send OTP to Aadhaar-linked mobile (Step 1)

**Request Body**:
```json
{
  "aadhaar_number": "123456789012"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "request_id": "OTP-20240115103000-1234",
  "message": "OTP sent successfully",
  "expires_at": "2024-01-15T10:40:00Z"
}
```

**Note**: OTP is valid for 10 minutes

---

### 2. Verify Aadhaar OTP

**Endpoint**: `POST /customers/{customer_id}/ekyc/aadhaar/otp/verify`

**Description**: Verify OTP and fetch eKYC data (Step 2)

**Request Body**:
```json
{
  "aadhaar_number": "123456789012",
  "otp": "123456",
  "request_id": "OTP-20240115103000-1234"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "verified": true,
  "message": "Aadhaar verified successfully",
  "ekyc_data": {
    "name": "John Doe",
    "date_of_birth": "1990-01-15",
    "gender": "Male",
    "address": {
      "line1": "House No 123",
      "line2": "MG Road",
      "city": "Bangalore",
      "district": "Bangalore Urban",
      "state": "Karnataka",
      "pincode": "560001"
    },
    "photo": "base64_encoded_photo_data",
    "mobile": "9876543210",
    "email": "john@example.com"
  }
}
```

**What Happens**:
1. OTP is verified with UIDAI
2. eKYC data is fetched
3. Customer record is auto-updated with verified data
4. KYC status is updated
5. Timeline event is logged

---

### 3. Verify with Biometric

**Endpoint**: `POST /customers/{customer_id}/ekyc/aadhaar/biometric`

**Description**: Verify Aadhaar using fingerprint/iris

**Request Body**:
```json
{
  "aadhaar_number": "123456789012",
  "biometric_data": "base64_encoded_biometric_data",
  "biometric_type": "fingerprint"
}
```

**Biometric Types**:
- `fingerprint`
- `iris`

**Response** (200 OK): Same structure as OTP verify

---

## DigiLocker APIs

### 1. Initiate Authorization

**Endpoint**: `POST /customers/{customer_id}/digilocker/authorize`

**Description**: Start DigiLocker OAuth flow (Step 1)

**Query Parameters**:
- `redirect_uri` (string, required): OAuth callback URL

**Response** (200 OK):
```json
{
  "authorization_url": "https://digitallocker.gov.in/authorize?...",
  "state": "random_state_for_csrf_protection"
}
```

**Flow**:
1. Call this endpoint
2. Redirect customer to `authorization_url`
3. Customer logs into DigiLocker
4. DigiLocker redirects to your `redirect_uri` with `code` and `state`
5. Call complete endpoint with the code

---

### 2. Complete Authorization

**Endpoint**: `POST /customers/{customer_id}/digilocker/complete`

**Description**: Exchange code for access token (Step 2)

**Request Body**:
```json
{
  "code": "authorization_code_from_callback",
  "redirect_uri": "https://yourapp.com/callback"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "access_token": "DigiLocker_Access_Token",
  "expires_in": 3600,
  "documents": [
    {
      "uri": "AADHAAR-123456",
      "name": "Aadhaar Card",
      "type": "ADHAR",
      "size": 524288,
      "date": "2020-01-15",
      "issuer": "UIDAI"
    },
    {
      "uri": "PAN-ABCDE1234F",
      "name": "PAN Card",
      "type": "PANCR",
      "size": 245760,
      "date": "2019-06-20",
      "issuer": "Income Tax Department"
    }
  ]
}
```

---

### 3. Get Available Documents

**Endpoint**: `GET /customers/{customer_id}/digilocker/documents`

**Description**: List all documents in DigiLocker

**Query Parameters**:
- `access_token` (string, required): From complete endpoint

**Response** (200 OK): Array of document metadata

---

### 4. Fetch and Store Document

**Endpoint**: `POST /customers/{customer_id}/digilocker/documents/fetch`

**Description**: Import document from DigiLocker to system

**Request Body**:
```json
{
  "access_token": "DigiLocker_Access_Token",
  "document_uri": "AADHAAR-123456",
  "document_type_id": "uuid-of-document-type"
}
```

**Response** (200 OK):
```json
{
  "id": 456,
  "customer_id": 101,
  "document_type_id": 1,
  "document_name": "Aadhaar Card",
  "document_url": "/documents/101/AADHAAR-123456.pdf",
  "document_format": "PDF",
  "status": "submitted",
  "uploaded_date": "2024-01-15T10:30:00Z"
}
```

**What Happens**:
1. Document is fetched from DigiLocker
2. Uploaded to your storage (S3/MinIO)
3. Document record created
4. Timeline event logged

---

## Common Schemas

### Error Response

All errors follow this structure:

```json
{
  "detail": "Error message explaining what went wrong"
}
```

**HTTP Status Codes**:
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### Validation Errors (422)

```json
{
  "detail": [
    {
      "loc": ["body", "aadhaar_number"],
      "msg": "Aadhaar must be exactly 12 digits",
      "type": "value_error"
    }
  ]
}
```

---

## Error Handling

### Bureau Pull Errors

**Scenario**: Bureau API timeout
```json
{
  "status": "timeout",
  "error_message": "Bureau API did not respond within 30 seconds"
}
```

**Scenario**: Invalid PAN
```json
{
  "detail": "Customer PAN number is required for bureau pull"
}
```

### eKYC Errors

**Scenario**: Invalid OTP
```json
{
  "success": false,
  "verified": false,
  "error": "Invalid OTP"
}
```

**Scenario**: OTP Expired
```json
{
  "success": false,
  "verified": false,
  "error": "OTP expired"
}
```

### DigiLocker Errors

**Scenario**: Invalid authorization code
```json
{
  "detail": "Failed to complete authorization: Invalid code"
}
```

---

## Environment Configuration

### Required Environment Variables

```bash
# Credit Bureau Configuration
BUREAU_USE_MOCK=true  # Set to false for production
CIBIL_API_KEY=your_cibil_key
CIBIL_API_SECRET=your_cibil_secret
CIBIL_API_URL=https://api.cibil.com

EQUIFAX_API_KEY=your_equifax_key
EQUIFAX_API_SECRET=your_equifax_secret
EQUIFAX_API_URL=https://api.equifax.co.in

EXPERIAN_API_KEY=your_experian_key
EXPERIAN_API_SECRET=your_experian_secret
EXPERIAN_API_URL=https://api.experian.in

CRIF_API_KEY=your_crif_key
CRIF_API_SECRET=your_crif_secret
CRIF_API_URL=https://api.crifhighmark.com

# eKYC Configuration
EKYC_USE_MOCK=true  # Set to false for production
UIDAI_API_KEY=your_uidai_key
UIDAI_API_SECRET=your_uidai_secret
UIDAI_API_URL=https://ekyc.uidai.gov.in/api

# DigiLocker Configuration
DIGILOCKER_USE_MOCK=true  # Set to false for production
DIGILOCKER_CLIENT_ID=your_client_id
DIGILOCKER_CLIENT_SECRET=your_client_secret
DIGILOCKER_API_URL=https://api.digitallocker.gov.in
```

### Mock Mode

When `*_USE_MOCK=true`, all APIs use mock providers that return fake data. Perfect for:
- Development
- Testing
- Demo environments
- CI/CD pipelines

Mock providers simulate realistic responses without external API calls.

---

## Best Practices

### 1. Bureau Pulls

- Always get customer consent before pulling credit reports
- Track consent in database (date, IP address)
- Limit bureau pulls to necessary occasions
- Cache results to avoid duplicate pulls
- Monitor API costs (each pull has a cost)

### 2. eKYC

- Validate Aadhaar format before initiating OTP (12 digits)
- Handle OTP expiry gracefully (10 minutes)
- Store consent records
- Secure biometric data transmission
- Never log or store raw OTPs

### 3. DigiLocker

- Implement proper OAuth state validation (CSRF protection)
- Store access tokens securely (encrypted)
- Handle token expiry (typically 1 hour)
- Request only necessary document access
- Verify redirect_uri matches registered URL

### 4. Timeline

- Use appropriate activity types
- Add meaningful descriptions
- Include metadata for context
- Mark critical events as important
- Search and filter for analysis

---

## Rate Limits

| API Category | Rate Limit | Notes |
|-------------|-----------|-------|
| Timeline APIs | 100 req/min | Per customer |
| Bureau APIs | 10 req/hour | Per customer (cost consideration) |
| eKYC APIs | 5 OTP/hour | Per Aadhaar (prevent abuse) |
| DigiLocker | 20 req/min | Per customer |

---

## Webhooks (Future)

Planned webhook support for:
- Bureau report completion
- eKYC success/failure
- Document verification status
- Critical timeline events

---

## Support

For API issues or questions:
- Email: api-support@yourcompany.com
- Documentation: https://docs.yourcompany.com
- Status Page: https://status.yourcompany.com

---

**Last Updated**: January 15, 2026  
**API Version**: v1.0  
**Document Version**: 1.0
