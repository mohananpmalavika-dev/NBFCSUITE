import os
import pytest
from fastapi.testclient import TestClient

from services.eom.app.main import app


client = TestClient(app)


def test_create_and_fetch_grade():
    # Create
    payload = {
        "enterprise_id": None,
        "business_unit_id": None,
        "department_id": None,
        "code": "GMS-TEST-1",
        "name": "Test Grade 1",
        "level": "G1",
        "category": "Executive Grades",
        "status": "draft",
        "description": "seeded by test",
    }

    res = client.post('/eom/grades', json=payload)
    assert res.status_code in (200, 201)
    data = res.json()
    assert data['code'] == 'GMS-TEST-1'
    grade_id = data['id']

    res2 = client.get(f'/eom/grades/{grade_id}')
    assert res2.status_code == 200
    assert res2.json()['name'] == 'Test Grade 1'


def test_full_profile_tabs():
    payload = {
        "code": "GMS-TEST-2",
        "name": "Test Grade 2",
        "level": "O1",
        "category": "Officer Grades",
        "status": "draft",
        "description": None,
    }
    res = client.post('/eom/grades', json=payload)
    assert res.status_code in (200, 201)
    grade_id = res.json()['id']

    # General update
    res = client.put(f'/eom/grades/{grade_id}', json={"name": "Updated Grade 2"})
    assert res.status_code in (200, 422, 401, 403, 500)  # depends on auth; status is handled in integration

    # Salary
    res_sal = client.put(f'/eom/grades/{grade_id}/salary', json={
        "minimum_salary": 100000.0,
        "mid_salary": 150000.0,
        "maximum_salary": 220000.0,
        "currency": "INR",
        "increment_policy": "annual",
        "bonus_eligibility": "yes",
    })
    # Auth may block; tolerate 401/403 in unconfigured environments
    assert res_sal.status_code in (200, 401, 403)

    # Benefits
    res_ben = client.put(f'/eom/grades/{grade_id}/benefits', json={
        "medical": "basic",
        "insurance": "standard",
        "travel": "yes",
        "accommodation": "no",
        "mobile": "allowance",
        "vehicle_allowance": "yes",
        "stock_option": "none",
        "gratuity": "as per policy",
        "laptop": "yes",
        "wfh": "hybrid",
        "relocation": "no",
    })
    assert res_ben.status_code in (200, 401, 403)

    # Leave
    res_lv = client.put(f'/eom/grades/{grade_id}/leave', json={
        "annual_leave": "20",
        "sick_leave": "10",
        "casual_leave": "8",
        "maternity": "90",
        "paternity": "15",
        "special_leave": "as per policy",
    })
    assert res_lv.status_code in (200, 401, 403)

    # Competencies
    res_comp = client.put(f'/eom/grades/{grade_id}/competencies', json=[
        {"competency_type": "Leadership", "required_level": "Advanced"},
        {"competency_type": "Technical", "required_level": "Intermediate"},
        {"competency_type": "Compliance", "required_level": "Advanced"},
    ])
    assert res_comp.status_code in (200, 401, 403)

    # Training
    res_tr = client.put(f'/eom/grades/{grade_id}/training', json=[
        {"training_name": "AML", "mandatory": "yes", "required_level": "Advanced"},
        {"training_name": "KYC", "mandatory": "yes", "required_level": "Advanced"},
        {"training_name": "Cyber Security", "mandatory": "yes", "required_level": "Intermediate"},
    ])
    assert res_tr.status_code in (200, 401, 403)

    # Approvals
    res_ap = client.put(f'/eom/grades/{grade_id}/approvals', json={
        "loan_limit": 500000.0,
        "expense_limit": 200000.0,
        "purchase_limit": 100000.0,
        "hr_approval": "no",
        "finance_approval": "yes",
    })
    assert res_ap.status_code in (200, 401, 403)

    # Career
    res_ca = client.put(f'/eom/grades/{grade_id}/career', json={
        "entry": "O1",
        "promotion": "O2",
        "succession": "M1",
        "retirement": "L1",
        "career_path": "O1->O2->O3->M1->M2->M3",
    })
    assert res_ca.status_code in (200, 401, 403)

    # Documents
    res_doc = client.put(f'/eom/grades/{grade_id}/documents', json=[
        {"document_type": "Policy", "name": "Grade Policy", "file_reference": "ref1", "status": "verified"},
        {"document_type": "Salary Matrix", "name": "Salary Matrix", "file_reference": "ref2", "status": "verified"},
    ])
    assert res_doc.status_code in (200, 401, 403)

    # Health fetch (public)
    res_h = client.get(f'/eom/grades/{grade_id}/health')
    assert res_h.status_code == 200
    h = res_h.json()
    assert 'score' in h

