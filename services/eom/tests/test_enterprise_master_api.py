import os
import tempfile

import pytest
from httpx import ASGITransport, AsyncClient


tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"
from services.eom.app.main import app


@pytest.mark.asyncio
async def test_enterprise_master_profile_dashboard_health_and_audit():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver', follow_redirects=True) as client:
        created = await client.post(
            '/eom/enterprises',
            json={'code': 'ENT-MASTER', 'name': 'Enterprise Master', 'display_name': 'Enterprise Master'},
            headers={'X-User-Roles': 'enterprise.admin'},
        )
        assert created.status_code == 201
        enterprise_id = created.json()['id']

        profile_payload = {
            'branding': {
                'primary_color': '#0f766e',
                'secondary_color': '#1d4ed8',
                'theme': 'enterprise',
                'website': 'https://example.com',
                'email_domain': 'example.com',
                'mobile_app_name': 'ARTH Mobile',
                'portal_name': 'ARTH Portal',
            },
            'legal': {
                'country': 'India',
                'registration_number': 'REG-001',
                'incorporation_date': '2010-04-01',
                'tax_number': 'TAX-001',
                'gst_vat_number': 'GST-001',
                'pan': 'ABCDE1234F',
                'corporate_identity_number': 'CIN-001',
                'regulatory_license': 'RBI-NBFC',
            },
            'finance': {
                'base_currency': 'INR',
                'financial_year': 'April-March',
                'accounting_standard': 'Ind AS',
                'tax_system': 'GST',
                'default_gl': '1000',
                'default_cost_center': 'HO',
                'default_profit_center': 'NBFC',
            },
            'localization': {
                'language': 'en-IN',
                'time_zone': 'Asia/Kolkata',
                'date_format': 'DD/MM/YYYY',
                'number_format': 'en-IN',
                'fiscal_calendar': 'India FY',
                'holiday_calendar': 'India',
            },
            'contact': {
                'corporate_address': 'Head office',
                'head_office': 'HO',
                'email': 'admin@example.com',
                'phone': '+91-9999999999',
                'website': 'https://example.com',
                'support_contact': 'support@example.com',
            },
            'compliance': {
                'aml_enabled': True,
                'kyc_policy': 'Standard KYC',
                'data_retention': '8 years',
                'audit_retention': '10 years',
                'password_policy': 'Strong',
                'session_policy': '30 minutes',
            },
            'integrations': [
                {'integration_type': 'core_banking', 'provider': 'Core', 'status': 'active'},
                {'integration_type': 'credit_bureau', 'provider': 'Bureau', 'status': 'planned'},
            ],
            'documents': [
                {'document_type': 'certificate', 'name': 'Certificate of incorporation', 'status': 'verified'},
            ],
            'settings': [
                {'setting_group': 'Workflow', 'setting_key': 'enterprise_creation', 'setting_value': 'approval-required'},
            ],
        }

        updated = await client.put(
            f'/eom/enterprises/{enterprise_id}/profile',
            json=profile_payload,
            headers={'X-User-Roles': 'enterprise.admin'},
        )
        assert updated.status_code == 200
        assert updated.json()['health']['score'] >= 90

        profile = await client.get(f'/eom/enterprises/{enterprise_id}/profile')
        assert profile.status_code == 200
        assert profile.json()['legal']['regulatory_license'] == 'RBI-NBFC'
        assert len(profile.json()['integrations']) == 2

        health = await client.get(f'/eom/enterprises/{enterprise_id}/health')
        assert health.status_code == 200
        assert health.json()['score'] >= 90

        dashboard = await client.get(f'/eom/enterprises/{enterprise_id}/dashboard')
        assert dashboard.status_code == 200
        assert dashboard.json()['enterprise']['code'] == 'ENT-MASTER'
        assert any(item['label'] == 'AI score' for item in dashboard.json()['indicators'])

        settings = await client.get(f'/eom/enterprises/{enterprise_id}/settings')
        assert settings.status_code == 200
        assert settings.json()['items'][0]['setting_group'] == 'Workflow'

        audit = await client.get(f'/eom/enterprises/{enterprise_id}/audit')
        assert audit.status_code == 200
        assert audit.json()['total'] >= 1
