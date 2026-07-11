# Reporting & Analytics API Reference

Complete API reference for the Reporting & Analytics module.

---

## Base URL
```
http://localhost:8000/api/v1
```

---

## Authentication
All endpoints require JWT authentication:
```
Authorization: Bearer <your_jwt_token>
```

---

## Report Templates API

### List Report Templates
```http
GET /reports/templates
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `page_size` (integer): Items per page (default: 50, max: 100)
- `category` (string): Filter by category (portfolio, collection, risk, etc.)
- `search` (string): Search in name and description
- `is_active` (boolean): Filter by active status

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "report_code": "PORTFOLIO_SUMMARY",
        "report_name": "Portfolio Summary Report",
        "report_description": "Overall portfolio health and key metrics",
        "category": "portfolio",
        "sub_category": null,
        "is_active": true,
        "is_system": true,
        "created_at": "2026-07-09T10:00:00Z"
      }
    ],
    "total": 124,
    "page": 1,
    "page_size": 50,
    "total_pages": 3
  },
  "message": "Found 124 report templates"
}
```

### Get Report Template
```http
GET /reports/templates/{template_id}
```

### Create Report Template
```http
POST /reports/templates
```

**Request Body:**
```json
{
  "report_code": "CUSTOM_REPORT_01",
  "report_name": "Custom Report",
  "report_description": "My custom report",
  "category": "operational",
  "query_template": "SELECT * FROM loans WHERE tenant_id = :tenant_id",
  "columns": {
    "account_number": {
      "label": "Account Number",
      "type": "string"
    },
    "amount": {
      "label": "Amount",
      "type": "currency"
    }
  },
  "is_public": false
}
```

### Get Report Categories
```http
GET /reports/templates/categories
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "value": "portfolio",
      "label": "Portfolio Reports",
      "count": 20
    },
    {
      "value": "collection",
      "label": "Collection Reports",
      "count": 15
    }
  ]
}
```

---

## Report Generation API

### Generate Report
```http
POST /reports/generate
```

**Request Body:**
```json
{
  "template_id": 1,
  "parameters": {
    "branch_id": "BR001"
  },
  "filters": {
    "status": "Active"
  },
  "date_range_start": "2026-01-01",
  "date_range_end": "2026-12-31",
  "file_format": "pdf"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "report": {
      "id": 1001,
      "report_name": "Portfolio Summary Report",
      "status": "completed",
      "row_count": 150,
      "execution_time_ms": 245,
      "file_url": "https://storage.example.com/reports/1001.pdf",
      "generation_date": "2026-07-09T14:30:00Z"
    },
    "data": [
      {
        "total_loans": 1500,
        "total_sanctioned": 50000000,
        "outstanding": 35000000
      }
    ],
    "columns": ["total_loans", "total_sanctioned", "outstanding"]
  },
  "message": "Report generated successfully with 150 rows"
}
```

### List Generated Reports
```http
GET /reports/generated
```

**Query Parameters:**
- `page`, `page_size`
- `status`: Filter by status (pending, completed, failed)
- `category`: Filter by category
- `start_date`, `end_date`: Filter by generation date

### Get Generated Report
```http
GET /reports/generated/{report_id}
```

### Delete Generated Report
```http
DELETE /reports/generated/{report_id}
```

---

## Scheduled Reports API

### Schedule Report
```http
POST /reports/schedule
```

**Request Body:**
```json
{
  "template_id": 1,
  "report_name": "Daily Portfolio Report",
  "frequency": "daily",
  "schedule_time": "09:00",
  "timezone": "Asia/Kolkata",
  "parameters": {},
  "filters": {},
  "delivery_method": {
    "type": "email",
    "recipients": ["manager@nbfc.com"]
  },
  "file_format": "xlsx"
}
```

### List Scheduled Reports
```http
GET /reports/schedule/list
```

### Delete Scheduled Report
```http
DELETE /reports/schedule/{schedule_id}
```

---

## Dashboards API

### List Dashboards
```http
GET /dashboards
```

**Query Parameters:**
- `page`, `page_size`
- `dashboard_type`: executive, operations, risk, collection, branch, treasury
- `is_active`: Filter by active status

### Get Dashboard with Widgets
```http
GET /dashboards/{dashboard_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "dashboard": {
      "id": 1,
      "dashboard_name": "Executive Dashboard",
      "dashboard_type": "executive",
      "is_default": true
    },
    "widgets": [
      {
        "id": 1,
        "widget_title": "Total Portfolio",
        "widget_type": "kpi_card",
        "position": {"x": 0, "y": 0, "width": 3, "height": 2},
        "refresh_interval_seconds": 300
      }
    ]
  }
}
```

### Create Dashboard
```http
POST /dashboards
```

**Request Body:**
```json
{
  "dashboard_name": "My Custom Dashboard",
  "dashboard_description": "Custom dashboard for branch managers",
  "dashboard_type": "custom",
  "layout_config": {
    "columns": 12,
    "rowHeight": 100
  },
  "theme": "default",
  "is_public": false
}
```

### Add Dashboard Widget
```http
POST /dashboards/widgets
```

**Request Body:**
```json
{
  "dashboard_id": 1,
  "position": {"x": 0, "y": 0, "width": 4, "height": 3},
  "widget_title": "Portfolio Growth",
  "widget_type": "line_chart",
  "data_source_type": "report",
  "report_template_id": 5,
  "parameters": {},
  "refresh_interval_seconds": 300,
  "visualization_config": {
    "x_axis": "month",
    "y_axis": "amount",
    "color": "blue"
  }
}
```

### Get Executive Dashboard Summary
```http
GET /dashboards/executive/summary
```

**Response:**
```json
{
  "success": true,
  "data": {
    "portfolio": {
      "total_loans": 1500,
      "total_sanctioned": 50000000.00,
      "outstanding": 35000000.00,
      "avg_ticket_size": 33333.33
    },
    "customers": {
      "total_customers": 2500,
      "new_this_month": 45,
      "active_customers": 2350
    },
    "collections": {
      "collection_efficiency": 92.5,
      "overdue_amount": 2500000.00,
      "overdue_accounts": 85
    },
    "risk": {
      "npa_ratio": 2.3,
      "portfolio_at_risk": 5.8,
      "high_risk_accounts": 45
    }
  }
}
```

---

## Custom Report Builder API

### Get Available Data Sources
```http
GET /reports/builder/datasources
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "table": "customers",
      "label": "Customers",
      "fields": [
        {
          "name": "customer_code",
          "label": "Customer Code",
          "type": "string"
        },
        {
          "name": "first_name",
          "label": "First Name",
          "type": "string"
        }
      ]
    },
    {
      "table": "loan_accounts",
      "label": "Loan Accounts",
      "fields": [
        {
          "name": "account_number",
          "label": "Account Number",
          "type": "string"
        },
        {
          "name": "sanctioned_amount",
          "label": "Sanctioned Amount",
          "type": "number"
        }
      ]
    }
  ]
}
```

### Get Available Aggregations
```http
GET /reports/builder/aggregations
```

### Create Custom Report
```http
POST /reports/builder
```

**Request Body:**
```json
{
  "report_name": "My Custom Loan Report",
  "report_description": "Loans by branch and status",
  "category": "operational",
  "data_sources": {
    "table": "loan_accounts"
  },
  "selected_fields": {
    "account_number": {"label": "Account Number"},
    "sanctioned_amount": {"label": "Amount"},
    "status": {"label": "Status"}
  },
  "filters": [
    {
      "field": "status",
      "operator": "equals",
      "value": "Active"
    }
  ],
  "grouping": ["branch_id"],
  "aggregations": [
    {
      "field": "sanctioned_amount",
      "function": "SUM"
    }
  ],
  "visualization_type": "bar_chart",
  "is_public": false
}
```

### List Custom Reports
```http
GET /reports/builder
```

### Get Custom Report
```http
GET /reports/builder/{report_id}
```

### Update Custom Report
```http
PUT /reports/builder/{report_id}
```

### Delete Custom Report
```http
DELETE /reports/builder/{report_id}
```

---

## Predictive Analytics API

### List ML Models
```http
GET /analytics/models
```

**Query Parameters:**
- `page`, `page_size`
- `model_type`: classification, regression, clustering
- `use_case`: credit_risk, churn, default, fraud, ltv
- `is_deployed`: Filter by deployment status

### Create ML Model
```http
POST /analytics/models
```

**Request Body:**
```json
{
  "model_name": "Credit Risk Scorer v2",
  "model_description": "Enhanced credit risk scoring model",
  "model_type": "classification",
  "use_case": "credit_risk",
  "algorithm": "xgboost",
  "features": {
    "credit_score": "number",
    "income": "number",
    "existing_loans": "number",
    "payment_history": "categorical"
  },
  "target_variable": "risk_grade",
  "training_data_query": "SELECT * FROM training_data"
}
```

### Get ML Model Details
```http
GET /analytics/models/{model_id}
```

### Make Prediction
```http
POST /analytics/predict
```

**Request Body:**
```json
{
  "model_id": 1,
  "entity_type": "customer",
  "entity_id": "CUST12345",
  "input_features": {
    "credit_score": 750,
    "income": 50000,
    "existing_loans": 2,
    "payment_history": "good"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 5001,
    "model_id": 1,
    "entity_type": "customer",
    "entity_id": "CUST12345",
    "predicted_class": "LOW_RISK",
    "probability": 0.85,
    "feature_importance": {
      "credit_score": 0.35,
      "income": 0.25,
      "existing_loans": 0.20,
      "payment_history": 0.20
    },
    "explanation": "Based on credit score, income, and payment history analysis",
    "prediction_date": "2026-07-09T15:00:00Z",
    "prediction_time_ms": 45
  },
  "message": "Prediction generated successfully"
}
```

### List Predictions
```http
GET /analytics/predictions
```

**Query Parameters:**
- `page`, `page_size`
- `model_id`: Filter by model
- `entity_type`: Filter by entity type
- `entity_id`: Filter by entity ID

### Get Analytics Use Cases
```http
GET /analytics/use-cases
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "value": "credit_risk",
      "label": "Credit Risk Scoring",
      "description": "Predict credit risk for loan applications",
      "output_type": "classification",
      "classes": ["LOW_RISK", "MEDIUM_RISK", "HIGH_RISK"]
    },
    {
      "value": "churn",
      "label": "Customer Churn Prediction",
      "description": "Predict customer churn probability",
      "output_type": "classification",
      "classes": ["WILL_CHURN", "NO_CHURN"]
    }
  ]
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": "Additional error details (only in debug mode)"
  }
}
```

**Common Error Codes:**
- `400`: Bad Request - Invalid parameters
- `401`: Unauthorized - Invalid or missing token
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `422`: Validation Error - Request validation failed
- `500`: Internal Server Error

---

## Rate Limiting

- Default: 1000 requests per hour per user
- Report generation: 100 requests per hour per user
- ML predictions: 500 requests per hour per user

---

## Pagination

All list endpoints support pagination:

**Request:**
```
GET /endpoint?page=2&page_size=50
```

**Response:**
```json
{
  "data": {
    "items": [],
    "total": 250,
    "page": 2,
    "page_size": 50,
    "total_pages": 5
  }
}
```

---

## Webhooks (Optional)

Configure webhooks for report completion:

```json
POST /reports/webhooks
{
  "url": "https://your-app.com/webhook",
  "events": ["report.completed", "report.failed"],
  "secret": "your-secret-key"
}
```

---

## SDKs and Client Libraries

### JavaScript/TypeScript
```typescript
import { ReportingAPI } from '@nbfc/reporting-sdk';

const api = new ReportingAPI({
  baseUrl: 'http://localhost:8000/api/v1',
  apiKey: 'your-api-key'
});

// Generate report
const report = await api.reports.generate({
  templateId: 1,
  parameters: { branch_id: 'BR001' },
  format: 'pdf'
});
```

### Python
```python
from nbfc_sdk import ReportingClient

client = ReportingClient(
    base_url='http://localhost:8000/api/v1',
    api_key='your-api-key'
)

# Generate report
report = client.reports.generate(
    template_id=1,
    parameters={'branch_id': 'BR001'},
    format='pdf'
)
```

---

## Testing

### Swagger UI
Access interactive API documentation:
```
http://localhost:8000/docs
```

### Postman Collection
Import the Postman collection:
```
./postman/Reporting_Analytics_API.postman_collection.json
```

---

## Support

For API support:
- Documentation: `/docs`
- Email: api-support@nbfc.com
- Slack: #api-support

---

**Last Updated**: July 9, 2026  
**API Version**: 1.0.0
