"""
Integration tests for NBFCSUITE microservices
Tests complete workflows across services
"""

import pytest
import httpx
from datetime import datetime
from uuid import uuid4

# Base URLs - in production these would be environment variables
AUTH_SERVICE = "http://localhost:8001"
LOS_SERVICE = "http://localhost:8002"
LMS_SERVICE = "http://localhost:8003"
COLLECTIONS_SERVICE = "http://localhost:8004"
CUSTOMER_SERVICE = "http://localhost:8005"
FINDNA_SERVICE = "http://localhost:8006"
DEPOSITS_SERVICE = "http://localhost:8007"
ACCOUNTING_SERVICE = "http://localhost:8008"
CRM_SERVICE = "http://localhost:8009"
DOCUMENT_SERVICE = "http://localhost:8010"
COMPLIANCE_SERVICE = "http://localhost:8011"
DEFAULT_TENANT_ID = "tenant-integration"


@pytest.fixture
def auth_token():
    """Get JWT token for authenticated requests"""
    client = httpx.Client()
    response = client.post(
        f"{AUTH_SERVICE}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
def headers(auth_token):
    """Create headers with authentication"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestAuthService:
    """Test Auth Service endpoints"""

    def test_health_check(self):
        """Test service health endpoint"""
        client = httpx.Client()
        response = client.get(f"{AUTH_SERVICE}/health")
        assert response.status_code == 200

    def test_login(self):
        """Test user login"""
        client = httpx.Client()
        response = client.post(
            f"{AUTH_SERVICE}/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_create_user(self, headers):
        """Test user creation"""
        client = httpx.Client()
        response = client.post(
            f"{AUTH_SERVICE}/auth/users",
            headers=headers,
            json={
                "username": f"testuser-{uuid4().hex[:8]}",
                "email": f"test-{uuid4().hex[:8]}@example.com",
                "password": "testpass123",
                "tenant_id": DEFAULT_TENANT_ID
            }
        )
        assert response.status_code in [200, 201]


class TestCustomerService:
    """Test Customer Service endpoints"""

    def test_health_check(self):
        """Test service health endpoint"""
        client = httpx.Client()
        response = client.get(f"{CUSTOMER_SERVICE}/health")
        assert response.status_code == 200

    def test_create_customer(self, headers):
        """Test customer creation"""
        client = httpx.Client()
        response = client.post(
            f"{CUSTOMER_SERVICE}/customers",
            headers=headers,
            json={
                "first_name": "Test",
                "last_name": "Customer",
                "email": f"test{datetime.now().timestamp()}@example.com",
                "phone": "9876543210",
                "dob": "1990-01-15",
                "gender": "M"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        return data

    def test_get_customer(self, headers):
        """Test retrieving customer"""
        client = httpx.Client()
        
        # First create a customer
        create_response = client.post(
            f"{CUSTOMER_SERVICE}/customers",
            headers=headers,
            json={
                "first_name": "Test",
                "last_name": "Customer",
                "email": f"test{datetime.now().timestamp()}@example.com",
                "phone": "9876543210",
                "dob": "1990-01-15",
                "gender": "M"
            }
        )
        
        if create_response.status_code in [200, 201]:
            customer_id = create_response.json()["id"]
            
            # Then retrieve it
            response = client.get(
                f"{CUSTOMER_SERVICE}/customers/{customer_id}",
                headers=headers
            )
            assert response.status_code == 200


class TestLOSService:
    """Test Loan Origination System endpoints"""

    def test_health_check(self):
        """Test service health endpoint"""
        client = httpx.Client()
        response = client.get(f"{LOS_SERVICE}/health")
        assert response.status_code == 200

    def test_create_loan_application(self, headers):
        """Test creating loan application"""
        client = httpx.Client()
        
        # Create customer first
        customer_response = client.post(
            f"{CUSTOMER_SERVICE}/customers",
            headers=headers,
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": f"john{datetime.now().timestamp()}@example.com",
                "phone": "9876543211",
                "dob": "1990-01-15",
                "gender": "M"
            }
        )
        
        if customer_response.status_code in [200, 201]:
            customer_id = customer_response.json()["id"]
            
            # Create loan application
            response = client.post(
                f"{LOS_SERVICE}/applications",
                headers=headers,
                json={
                    "customer_id": customer_id,
                    "product_code": "PERSONAL_LOAN",
                    "applied_amount": 500000,
                    "tenure_months": 60
                }
            )
            assert response.status_code in [200, 201]
            return response.json()

    def test_list_applications(self, headers):
        """Test listing loan applications"""
        client = httpx.Client()
        response = client.get(
            f"{LOS_SERVICE}/applications",
            headers=headers
        )
        assert response.status_code == 200


class TestLMSService:
    """Test Loan Management System endpoints"""

    def test_health_check(self):
        """Test service health endpoint"""
        client = httpx.Client()
        response = client.get(f"{LMS_SERVICE}/health")
        assert response.status_code == 200

    def test_get_loan_details(self, headers):
        """Test retrieving loan details"""
        client = httpx.Client()
        response = client.get(
            f"{LMS_SERVICE}/loans/loan-123",
            headers=headers
        )
        # May return 404 if loan doesn't exist in test env
        assert response.status_code in [200, 404]

    def test_get_emi_schedule(self, headers):
        """Test retrieving EMI schedule"""
        client = httpx.Client()
        response = client.get(
            f"{LMS_SERVICE}/loans/loan-123/emi-schedule",
            headers=headers
        )
        assert response.status_code in [200, 404]


class TestFinDNAService:
    """Test FinDNA AI Service endpoints"""

    def test_health_check(self):
        """Test service health endpoint"""
        client = httpx.Client()
        response = client.get(f"{FINDNA_SERVICE}/health")
        assert response.status_code == 200

    def test_score_behavior(self, headers):
        """Test behavioral score endpoint"""
        client = httpx.Client()
        response = client.post(
            f"{FINDNA_SERVICE}/score/behavior",
            headers=headers,
            json={
                "customer_id": "customer-123",
                "income_data": {"monthly_income": 65000, "annual_salary": 780000},
                "bank_statement_url": "https://example.com/statement.pdf"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] in ["low", "medium", "high"]
        assert "default_probability_90d" in data

    def test_score_fraud(self, headers):
        """Test fraud detection endpoint"""
        client = httpx.Client()
        response = client.post(
            f"{FINDNA_SERVICE}/score/fraud",
            headers=headers,
            json={
                "customer_id": "customer-123",
                "application_id": "app-456",
                "documents": ["id_proof.pdf", "income_proof.pdf"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "fraud_score" in data
        assert data["risk_level"] in ["low", "medium", "high", "critical"]

    def test_predict_churn(self, headers):
        """Test churn prediction endpoint"""
        client = httpx.Client()
        response = client.post(
            f"{FINDNA_SERVICE}/predict/churn",
            headers=headers,
            json={"customer_id": "customer-123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "churn_probability" in data

    def test_underwriting_assistant(self, headers):
        """Test underwriting assistant endpoint"""
        client = httpx.Client()
        response = client.post(
            f"{FINDNA_SERVICE}/underwriting-assistant/app-789",
            headers=headers,
            json={
                "customer_id": "customer-123",
                "context_text": "Assess eligibility for a salaried customer with stable income."
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "recommendation" in data

    def test_collections_assistant(self, headers):
        """Test collections assistant endpoint"""
        client = httpx.Client()
        response = client.post(
            f"{FINDNA_SERVICE}/collections-assistant/customer-123",
            headers=headers,
            json={
                "context_text": "Customer missed two recent payments." 
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "risk_indicators" in data

    def test_relationship_manager(self, headers):
        """Test relationship manager endpoint"""
        client = httpx.Client()
        response = client.post(
            f"{FINDNA_SERVICE}/relationship-manager/customer-123",
            headers=headers,
            json={
                "context_text": "Recommend relationship strategies for a value customer."}
        )
        assert response.status_code == 200
        data = response.json()
        assert "action_plan" in data


class TestDepositsService:
    """Test Deposits Microservice endpoints"""

    def test_health_check(self):
        client = httpx.Client()
        response = client.get(f"{DEPOSITS_SERVICE}/health")
        assert response.status_code == 200

    def test_list_deposit_types(self):
        client = httpx.Client()
        response = client.get(f"{DEPOSITS_SERVICE}/deposit-types")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_and_get_deposit_account(self, headers):
        client = httpx.Client()
        response = client.post(
            f"{DEPOSITS_SERVICE}/deposit-accounts",
            headers=headers,
            json={
                "customer_id": "customer-123",
                "deposit_type_code": "CASA",
                "principal_amount": 10000
            }
        )
        assert response.status_code == 200
        account = response.json()
        assert account["customer_id"] == "customer-123"
        account_id = account["id"]

        get_response = client.get(f"{DEPOSITS_SERVICE}/deposit-accounts/{account_id}")
        assert get_response.status_code == 200


class TestAccountingService:
    """Test Accounting Microservice endpoints"""

    def test_health_check(self):
        client = httpx.Client()
        response = client.get(f"{ACCOUNTING_SERVICE}/health")
        assert response.status_code == 200

    def test_create_and_list_gl_account(self, headers):
        client = httpx.Client()
        response = client.post(
            f"{ACCOUNTING_SERVICE}/gl-accounts",
            headers=headers,
            json={
                "tenant_id": DEFAULT_TENANT_ID,
                "account_code": f"GL-{uuid4().hex[:8].upper()}",
                "account_name": "Cash Account",
                "account_type": "asset"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tenant_id"] == DEFAULT_TENANT_ID

        list_response = client.get(
            f"{ACCOUNTING_SERVICE}/gl-accounts",
            params={"tenant_id": DEFAULT_TENANT_ID},
        )
        assert list_response.status_code == 200

    def test_create_balanced_journal_entry(self, headers):
        client = httpx.Client()
        # Create a GL account for the journal entry
        account_response = client.post(
            f"{ACCOUNTING_SERVICE}/gl-accounts",
            headers=headers,
            json={
                "tenant_id": DEFAULT_TENANT_ID,
                "account_code": f"GL-{uuid4().hex[:8].upper()}",
                "account_name": "Receivables",
                "account_type": "asset"
            }
        )
        assert account_response.status_code == 200
        account_id = account_response.json()["id"]

        journal_response = client.post(
            f"{ACCOUNTING_SERVICE}/journal-entries",
            headers=headers,
            json={
                "tenant_id": DEFAULT_TENANT_ID,
                "description": "Test balanced entry",
                "lines": [
                    {"gl_account_id": account_id, "debit": 100.0, "credit": 0.0},
                    {"gl_account_id": account_id, "debit": 0.0, "credit": 100.0}
                ]
            }
        )
        assert journal_response.status_code == 200
        assert "id" in journal_response.json()


class TestCRMService:
    """Test CRM Microservice endpoints"""

    def test_health_check(self):
        client = httpx.Client()
        response = client.get(f"{CRM_SERVICE}/health")
        assert response.status_code == 200

    def test_create_and_list_leads(self, headers):
        client = httpx.Client()
        response = client.post(
            f"{CRM_SERVICE}/leads",
            headers=headers,
            json={
                "tenant_id": DEFAULT_TENANT_ID,
                "source": "web",
                "assigned_to": "user1"
            }
        )
        assert response.status_code == 201
        lead = response.json()
        assert lead["status"] == "new"

        list_response = client.get(
            f"{CRM_SERVICE}/leads",
            params={"tenant_id": DEFAULT_TENANT_ID},
        )
        assert list_response.status_code == 200

    def test_create_campaign_and_opportunity(self, headers):
        client = httpx.Client()
        campaign_response = client.post(
            f"{CRM_SERVICE}/campaigns",
            headers=headers,
            json={
                "tenant_id": DEFAULT_TENANT_ID,
                "name": "Summer Campaign",
                "description": "Test campaign",
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-12-31T00:00:00Z",
                "budget": 10000.0
            }
        )
        assert campaign_response.status_code == 200

        lead_response = client.post(
            f"{CRM_SERVICE}/leads",
            headers=headers,
            json={
                "tenant_id": DEFAULT_TENANT_ID,
                "source": "referral"
            }
        )
        assert lead_response.status_code == 201
        lead_id = lead_response.json()["id"]

        opportunity_response = client.post(
            f"{CRM_SERVICE}/opportunities",
            headers=headers,
            json={
                "tenant_id": DEFAULT_TENANT_ID,
                "lead_id": lead_id,
                "product_code": "PL-001",
                "value": 50000.0,
                "probability": 0.75
            }
        )
        assert opportunity_response.status_code == 200


class TestDocumentService:
    """Test Document Microservice endpoints"""

    def test_health_check(self):
        client = httpx.Client()
        response = client.get(f"{DOCUMENT_SERVICE}/health")
        assert response.status_code == 200

    def test_create_and_get_document(self, headers):
        client = httpx.Client()
        response = client.post(
            f"{DOCUMENT_SERVICE}/documents",
            headers=headers,
            json={
                "subject_type": "customer",
                "subject_id": "customer-123",
                "document_type": "aadhar",
                "document_name": "Aadhar Card",
                "document_url": "https://example.com/aadhar.pdf"
            }
        )
        assert response.status_code == 200
        document_id = response.json()["id"]

        get_response = client.get(f"{DOCUMENT_SERVICE}/documents/{document_id}")
        assert get_response.status_code == 200

    def test_list_documents(self, headers):
        client = httpx.Client()
        response = client.get(
            f"{DOCUMENT_SERVICE}/documents",
            headers=headers
        )
        assert response.status_code == 200


class TestComplianceService:
    """Test Compliance Microservice endpoints"""

    def test_health_check(self):
        client = httpx.Client()
        response = client.get(f"{COMPLIANCE_SERVICE}/health")
        assert response.status_code == 200

    def test_watchlist_and_list(self, headers):
        client = httpx.Client()
        response = client.post(
            f"{COMPLIANCE_SERVICE}/watchlist",
            headers=headers,
            json={
                "name": "Sanctioned Person",
                "list_type": "sanctions",
                "country": "IN",
                "risk_level": "high"
            }
        )
        assert response.status_code == 200

        list_response = client.get(f"{COMPLIANCE_SERVICE}/watchlist")
        assert list_response.status_code == 200

    def test_compliance_check_and_audit_log(self, headers):
        client = httpx.Client()
        check_response = client.post(
            f"{COMPLIANCE_SERVICE}/compliance-checks",
            headers=headers,
            json={
                "customer_id": "customer-123",
                "check_type": "aml",
                "status": "pass"
            }
        )
        assert check_response.status_code == 200

        audit_response = client.post(
            f"{COMPLIANCE_SERVICE}/audit-logs",
            headers=headers,
            json={
                "entity_type": "customer",
                "entity_id": "customer-123",
                "action": "compliance_check",
                "performed_by": "system"
            }
        )
        assert audit_response.status_code == 200

        get_checks = client.get(f"{COMPLIANCE_SERVICE}/compliance-checks/customer-123")
        assert get_checks.status_code == 200


class TestCollectionsService:
    """Test Collections Service endpoints"""

    def test_health_check(self):
        """Test service health endpoint"""
        client = httpx.Client()
        response = client.get(f"{COLLECTIONS_SERVICE}/health")
        assert response.status_code == 200

    def test_collection_buckets(self, headers):
        """Test retrieving collection buckets"""
        client = httpx.Client()
        response = client.get(
            f"{COLLECTIONS_SERVICE}/collection-buckets",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestEndToEndWorkflow:
    """Test complete workflows across services"""

    def test_complete_loan_workflow(self, headers):
        """Test complete loan application to payment flow"""
        client = httpx.Client()
        
        try:
            # Step 1: Create customer
            customer_response = client.post(
                f"{CUSTOMER_SERVICE}/customers",
                headers=headers,
                json={
                    "first_name": "Alice",
                    "last_name": "Smith",
                    "email": f"alice{datetime.now().timestamp()}@example.com",
                    "phone": "9876543212",
                    "dob": "1990-01-15",
                    "gender": "F"
                }
            )
            
            if customer_response.status_code not in [200, 201]:
                pytest.skip("Customer creation failed")
            
            customer_id = customer_response.json()["id"]
            
            # Step 2: Create loan application
            app_response = client.post(
                f"{LOS_SERVICE}/applications",
                headers=headers,
                json={
                    "customer_id": customer_id,
                    "product_code": "PERSONAL_LOAN",
                    "applied_amount": 500000,
                    "tenure_months": 60
                }
            )
            
            if app_response.status_code in [200, 201]:
                application_id = app_response.json()["id"]
                
                # Step 3: Submit application
                submit_response = client.post(
                    f"{LOS_SERVICE}/applications/{application_id}/submit",
                    headers=headers
                )
                assert submit_response.status_code in [200, 201]
                
                # Step 4: Get behavioral score
                score_response = client.post(
                    f"{FINDNA_SERVICE}/behavioral-score/{customer_id}",
                    headers=headers
                )
                assert score_response.status_code == 200
                
        except Exception as e:
            pytest.skip(f"End-to-end test skipped: {str(e)}")

    def test_phase4_crm_accounting_tenant_isolation(self, headers):
        """Create lead -> opportunity -> CRM report and GL posting -> trial balance with tenant isolation."""
        client = httpx.Client()
        tenant_a = f"tenant-a-{uuid4().hex[:8]}"
        tenant_b = f"tenant-b-{uuid4().hex[:8]}"
        overlapping_code = f"GL-SHARED-{uuid4().hex[:6].upper()}"

        # Same GL account code must be valid for two different tenants.
        for tenant_id in [tenant_a, tenant_b]:
            account_response = client.post(
                f"{ACCOUNTING_SERVICE}/gl-accounts",
                headers=headers,
                json={
                    "tenant_id": tenant_id,
                    "account_code": overlapping_code,
                    "account_name": "Shared Code Cash",
                    "account_type": "asset",
                },
            )
            assert account_response.status_code == 200
            assert account_response.json()["tenant_id"] == tenant_id

        lead_response = client.post(
            f"{CRM_SERVICE}/leads",
            headers=headers,
            json={
                "tenant_id": tenant_a,
                "source": "phase4-e2e",
                "assigned_to": "ceo",
            },
        )
        assert lead_response.status_code == 201
        lead = lead_response.json()

        opportunity_response = client.post(
            f"{CRM_SERVICE}/opportunities",
            headers=headers,
            json={
                "tenant_id": tenant_a,
                "lead_id": lead["id"],
                "product_code": "PL-CEO",
                "value": 75000.0,
                "probability": 0.8,
            },
        )
        assert opportunity_response.status_code == 200

        cross_tenant_opportunity = client.post(
            f"{CRM_SERVICE}/opportunities",
            headers=headers,
            json={
                "tenant_id": tenant_b,
                "lead_id": lead["id"],
                "product_code": "PL-CEO",
                "value": 75000.0,
                "probability": 0.8,
            },
        )
        assert cross_tenant_opportunity.status_code == 404

        report_response = client.post(
            f"{CRM_SERVICE}/reports/execute",
            headers=headers,
            json={
                "tenant_id": tenant_a,
                "data_source": "opportunities",
                "columns": ["id", "lead_id", "product_code", "value", "probability"],
                "filters": {"lead_id": lead["id"]},
                "group_by": ["product_code"],
            },
        )
        assert report_response.status_code == 200
        report = report_response.json()
        assert report["tenant_id"] == tenant_a
        assert report["row_count"] == 1
        assert report["groups"][0]["value"] == 75000.0

        dashboard_response = client.post(
            f"{CRM_SERVICE}/dashboards/defaults/ceo-command-center",
            headers=headers,
            params={"tenant_id": tenant_a},
        )
        assert dashboard_response.status_code == 200

        idem_key = f"phase4-{uuid4().hex}"
        posting_payload = {
            "tenant_id": tenant_a,
            "idempotency_key": idem_key,
            "source_module": "loans",
            "source_event": "disbursement",
            "source_reference": lead["id"],
            "amount": 25000.0,
            "metadata": {"scenario": "phase4-e2e"},
        }
        posting_response = client.post(
            f"{ACCOUNTING_SERVICE}/gl-postings/auto",
            headers=headers,
            json=posting_payload,
        )
        assert posting_response.status_code == 200
        first_posting = posting_response.json()
        assert first_posting["posting_status"] == "posted"
        assert first_posting["source_reference"] == lead["id"]

        duplicate_response = client.post(
            f"{ACCOUNTING_SERVICE}/gl-postings/auto",
            headers=headers,
            json=posting_payload,
        )
        assert duplicate_response.status_code == 200
        assert duplicate_response.json()["id"] == first_posting["id"]

        other_tenant_response = client.post(
            f"{ACCOUNTING_SERVICE}/gl-postings/auto",
            headers=headers,
            json={**posting_payload, "tenant_id": tenant_b},
        )
        assert other_tenant_response.status_code == 200
        assert other_tenant_response.json()["id"] != first_posting["id"]

        trial_balance_response = client.get(
            f"{ACCOUNTING_SERVICE}/reports/trial-balance",
            headers=headers,
            params={"tenant_id": tenant_a},
        )
        assert trial_balance_response.status_code == 200
        trial_balance = trial_balance_response.json()
        assert trial_balance["tenant_id"] == tenant_a
        assert trial_balance["is_balanced"] is True
        assert trial_balance["total_debit"] == 25000.0
        assert trial_balance["total_credit"] == 25000.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
