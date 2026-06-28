import os
import subprocess
import sys
from pathlib import Path


def build_pythonpath(root: Path) -> str:
    services_dir = root / "services"
    parts = []
    if services_dir.exists():
        for d in services_dir.iterdir():
            app_dir = d / "app"
            if app_dir.exists():
                parts.append(str(app_dir))
    # include workspace root
    parts.append(str(root))
    return os.pathsep.join(parts)


def main():
    root = Path(__file__).resolve().parents[1]
    pythonpath = build_pythonpath(root)
    env = os.environ.copy()
    env["PYTHONPATH"] = pythonpath

    # Run only HRMS-related tests (expand globs)
    tests_dir = root / "tests"
    candidates = list(tests_dir.glob("test_hrms_*.py")) if tests_dir.exists() else []
    if not candidates and tests_dir.exists():
        candidates = [p for p in tests_dir.iterdir() if p.is_file() and "hrms" in p.name]

    if not candidates:
        print("No HRMS-specific test files found under tests/ — exiting with code 0")
        sys.exit(0)

    args = [str(p) for p in candidates]
    print(f"Running HRMS tests with PYTHONPATH={pythonpath}: {args}")
    cmd = [sys.executable, "-m", "pytest", "-q"] + args
    rc = subprocess.call(cmd, env=env)
    if rc != 0:
        print(f"pytest exited with {rc}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
