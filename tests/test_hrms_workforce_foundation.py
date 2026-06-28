import pathlib


def test_hrms_routes_and_field_present_in_source():
    p = pathlib.Path("services/hrms/app/main.py")
    assert p.exists(), "HRMS main.py not found"
    src = p.read_text(encoding="utf-8")

    expected_routes = [
        "/job-families",
        "/job-roles",
        "/employee-assignments",
        "/positions/vacant",
        "/positions/occupied",
        "/organization/{organization_unit_id}/positions",
        "/employees/{employee_id}/timeline",
    ]

    for route in expected_routes:
        assert route in src, f"Expected route {route} not found in main.py"

    assert "budgeted_salary" in src, "Expected 'budgeted_salary' not found in HRPosition model"


def test_attendance_models_and_routes_present():
    p = pathlib.Path("services/hrms/app/main.py")
    src = p.read_text(encoding="utf-8")

    attendance_things = [
        "hr_shifts",
        "hr_attendance",
        "hr_leave_types",
        "/attendance/check-in",
        "/attendance/check-out",
        "/leave/apply",
    ]

    for token in attendance_things:
        assert token in src, f"Expected {token} present in HRMS source"


def test_ai_and_event_scaffold_present():
    p = pathlib.Path("services/hrms/app/main.py")
    src = p.read_text(encoding="utf-8")
    tokens = [
        "event_publisher",
        "ai_service",
        "/attendance/regularize",
        "/shifts",
        "/attendance/analyze",
        "get_publisher",
        "get_ai_service",
    ]
    for t in tokens:
        assert t in src, f"Expected {t} present in HRMS source"
