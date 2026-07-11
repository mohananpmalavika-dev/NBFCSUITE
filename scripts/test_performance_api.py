#!/usr/bin/env python3
"""
Performance Management API Testing Script

This script tests all Performance Management API endpoints to verify:
- API connectivity
- Authentication
- Request/Response validation
- Business logic
- Error handling

Usage:
    python test_performance_api.py --base-url http://localhost:8000 --token YOUR_JWT_TOKEN
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import argparse


class PerformanceAPITester:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1/hrms/performance"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.test_results = []
        self.test_data = {}
        
    def log_test(self, name: str, success: bool, message: str = "", response: Any = None):
        """Log test result"""
        status = "✓" if success else "✗"
        result = {
            "name": name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        print(f"{status} {name}")
        if message:
            print(f"  → {message}")
        if response and not success:
            print(f"  → Response: {response}")
            
    def test_health_check(self):
        """Test API health"""
        print("\n=== Testing API Health ===")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            self.log_test(
                "API Health Check",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test("API Health Check", False, str(e))
            
    def test_appraisal_cycles(self):
        """Test Appraisal Cycle endpoints"""
        print("\n=== Testing Appraisal Cycles ===")
        
        # 1. Create cycle
        cycle_data = {
            "name": "TEST-2024-25",
            "description": "Test Cycle for API Testing",
            "start_date": (datetime.now() + timedelta(days=1)).date().isoformat(),
            "end_date": (datetime.now() + timedelta(days=365)).date().isoformat(),
            "goal_setting_start": (datetime.now() + timedelta(days=1)).date().isoformat(),
            "goal_setting_end": (datetime.now() + timedelta(days=30)).date().isoformat(),
            "self_assessment_start": (datetime.now() + timedelta(days=270)).date().isoformat(),
            "self_assessment_end": (datetime.now() + timedelta(days=300)).date().isoformat(),
            "manager_review_start": (datetime.now() + timedelta(days=301)).date().isoformat(),
            "manager_review_end": (datetime.now() + timedelta(days=330)).date().isoformat(),
            "hr_review_start": (datetime.now() + timedelta(days=331)).date().isoformat(),
            "hr_review_end": (datetime.now() + timedelta(days=365)).date().isoformat(),
            "status": "DRAFT",
            "enable_goal_setting": True,
            "enable_self_assessment": True,
            "enable_360_feedback": True
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/cycles",
                headers=self.headers,
                json=cycle_data
            )
            
            if response.status_code == 201:
                cycle = response.json()
                self.test_data['cycle_id'] = cycle['id']
                self.log_test(
                    "Create Appraisal Cycle",
                    True,
                    f"Created cycle: {cycle['name']} (ID: {cycle['id']})"
                )
            else:
                self.log_test(
                    "Create Appraisal Cycle",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test("Create Appraisal Cycle", False, str(e))
            
        # 2. Get cycle by ID
        if 'cycle_id' in self.test_data:
            try:
                response = requests.get(
                    f"{self.api_base}/cycles/{self.test_data['cycle_id']}",
                    headers=self.headers
                )
                self.log_test(
                    "Get Appraisal Cycle by ID",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                self.log_test("Get Appraisal Cycle by ID", False, str(e))
                
        # 3. List cycles
        try:
            response = requests.get(
                f"{self.api_base}/cycles",
                headers=self.headers,
                params={"page": 1, "per_page": 10}
            )
            self.log_test(
                "List Appraisal Cycles",
                response.status_code == 200,
                f"Found {len(response.json().get('items', []))} cycles"
            )
        except Exception as e:
            self.log_test("List Appraisal Cycles", False, str(e))
            
        # 4. Update cycle
        if 'cycle_id' in self.test_data:
            try:
                update_data = {
                    "description": "Updated Test Cycle Description",
                    "status": "ACTIVE"
                }
                response = requests.put(
                    f"{self.api_base}/cycles/{self.test_data['cycle_id']}",
                    headers=self.headers,
                    json=update_data
                )
                self.log_test(
                    "Update Appraisal Cycle",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                self.log_test("Update Appraisal Cycle", False, str(e))
                
    def test_performance_goals(self):
        """Test Performance Goal endpoints"""
        print("\n=== Testing Performance Goals ===")
        
        if 'cycle_id' not in self.test_data:
            print("⚠ Skipping goal tests - no cycle created")
            return
            
        # 1. Create goal
        goal_data = {
            "appraisal_id": None,  # Will be set after creating appraisal
            "goal_type": "KPI",
            "title": "Test KPI Goal",
            "description": "This is a test KPI for API testing",
            "target_value": "100",
            "measurement_unit": "Count",
            "weightage": 25.0,
            "status": "DRAFT"
        }
        
        # First, we need to create an employee appraisal
        # This would normally be done by the system when cycle is activated
        # For testing, we'll create a minimal appraisal
        
        print("  → Creating test appraisal first...")
        appraisal_data = {
            "cycle_id": self.test_data['cycle_id'],
            "employee_id": 1,  # Assuming test employee exists
            "status": "DRAFT"
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/appraisals",
                headers=self.headers,
                json=appraisal_data
            )
            
            if response.status_code == 201:
                appraisal = response.json()
                self.test_data['appraisal_id'] = appraisal['id']
                goal_data['appraisal_id'] = appraisal['id']
                print(f"  → Created appraisal ID: {appraisal['id']}")
            else:
                print(f"  → Failed to create appraisal: {response.status_code}")
                return
        except Exception as e:
            print(f"  → Error creating appraisal: {e}")
            return
            
        # Now create the goal
        try:
            response = requests.post(
                f"{self.api_base}/goals",
                headers=self.headers,
                json=goal_data
            )
            
            if response.status_code == 201:
                goal = response.json()
                self.test_data['goal_id'] = goal['id']
                self.log_test(
                    "Create Performance Goal",
                    True,
                    f"Created goal: {goal['title']} (ID: {goal['id']})"
                )
            else:
                self.log_test(
                    "Create Performance Goal",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test("Create Performance Goal", False, str(e))
            
        # 2. Get goal by ID
        if 'goal_id' in self.test_data:
            try:
                response = requests.get(
                    f"{self.api_base}/goals/{self.test_data['goal_id']}",
                    headers=self.headers
                )
                self.log_test(
                    "Get Performance Goal by ID",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                self.log_test("Get Performance Goal by ID", False, str(e))
                
        # 3. Update goal progress
        if 'goal_id' in self.test_data:
            try:
                update_data = {
                    "current_value": "50",
                    "progress_percentage": 50.0,
                    "status": "IN_PROGRESS"
                }
                response = requests.put(
                    f"{self.api_base}/goals/{self.test_data['goal_id']}",
                    headers=self.headers,
                    json=update_data
                )
                self.log_test(
                    "Update Goal Progress",
                    response.status_code == 200,
                    f"Progress: 50%"
                )
            except Exception as e:
                self.log_test("Update Goal Progress", False, str(e))
                
        # 4. Submit goal for approval
        if 'goal_id' in self.test_data:
            try:
                response = requests.post(
                    f"{self.api_base}/goals/{self.test_data['goal_id']}/submit",
                    headers=self.headers
                )
                self.log_test(
                    "Submit Goal for Approval",
                    response.status_code == 200,
                    "Goal submitted"
                )
            except Exception as e:
                self.log_test("Submit Goal for Approval", False, str(e))
                
    def test_self_assessment(self):
        """Test Self-Assessment workflow"""
        print("\n=== Testing Self-Assessment ===")
        
        if 'appraisal_id' not in self.test_data:
            print("⚠ Skipping self-assessment tests - no appraisal created")
            return
            
        try:
            assessment_data = {
                "self_rating": 4,
                "achievements": "Completed all assigned projects on time",
                "areas_of_improvement": "Need to improve communication skills",
                "training_requirements": "Leadership training",
                "comments": "Overall a good year"
            }
            
            response = requests.post(
                f"{self.api_base}/appraisals/{self.test_data['appraisal_id']}/self-assessment",
                headers=self.headers,
                json=assessment_data
            )
            
            self.log_test(
                "Submit Self-Assessment",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test("Submit Self-Assessment", False, str(e))
            
    def test_360_feedback(self):
        """Test 360 Feedback workflow"""
        print("\n=== Testing 360 Feedback ===")
        
        if 'appraisal_id' not in self.test_data:
            print("⚠ Skipping feedback tests - no appraisal created")
            return
            
        # 1. Create feedback request
        try:
            request_data = {
                "appraisal_id": self.test_data['appraisal_id'],
                "reviewer_id": 2,  # Assuming test reviewer exists
                "feedback_type": "PEER",
                "due_date": (datetime.now() + timedelta(days=7)).date().isoformat()
            }
            
            response = requests.post(
                f"{self.api_base}/feedback/requests",
                headers=self.headers,
                json=request_data
            )
            
            if response.status_code == 201:
                feedback_request = response.json()
                self.test_data['feedback_request_id'] = feedback_request['id']
                self.log_test(
                    "Create Feedback Request",
                    True,
                    f"Created request ID: {feedback_request['id']}"
                )
            else:
                self.log_test(
                    "Create Feedback Request",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test("Create Feedback Request", False, str(e))
            
        # 2. List feedback requests
        try:
            response = requests.get(
                f"{self.api_base}/feedback/requests",
                headers=self.headers
            )
            self.log_test(
                "List Feedback Requests",
                response.status_code == 200,
                f"Found {len(response.json())} requests"
            )
        except Exception as e:
            self.log_test("List Feedback Requests", False, str(e))
            
    def test_error_handling(self):
        """Test error handling"""
        print("\n=== Testing Error Handling ===")
        
        # 1. Test 404 - Non-existent cycle
        try:
            response = requests.get(
                f"{self.api_base}/cycles/99999",
                headers=self.headers
            )
            self.log_test(
                "Handle 404 Error",
                response.status_code == 404,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test("Handle 404 Error", False, str(e))
            
        # 2. Test 400 - Invalid data
        try:
            invalid_cycle = {
                "name": "",  # Empty name should fail validation
                "start_date": "invalid-date"  # Invalid date format
            }
            response = requests.post(
                f"{self.api_base}/cycles",
                headers=self.headers,
                json=invalid_cycle
            )
            self.log_test(
                "Handle 400 Validation Error",
                response.status_code == 422,  # FastAPI uses 422 for validation
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test("Handle 400 Validation Error", False, str(e))
            
        # 3. Test 401 - Unauthorized (no token)
        try:
            response = requests.get(
                f"{self.api_base}/cycles",
                headers={"Content-Type": "application/json"}  # No auth header
            )
            self.log_test(
                "Handle 401 Unauthorized",
                response.status_code == 401,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test("Handle 401 Unauthorized", False, str(e))
            
    def cleanup(self):
        """Clean up test data"""
        print("\n=== Cleaning Up Test Data ===")
        
        # Delete test goal
        if 'goal_id' in self.test_data:
            try:
                response = requests.delete(
                    f"{self.api_base}/goals/{self.test_data['goal_id']}",
                    headers=self.headers
                )
                self.log_test(
                    "Delete Test Goal",
                    response.status_code in [200, 204],
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                self.log_test("Delete Test Goal", False, str(e))
                
        # Delete test cycle
        if 'cycle_id' in self.test_data:
            try:
                response = requests.delete(
                    f"{self.api_base}/cycles/{self.test_data['cycle_id']}",
                    headers=self.headers
                )
                self.log_test(
                    "Delete Test Cycle",
                    response.status_code in [200, 204],
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                self.log_test("Delete Test Cycle", False, str(e))
                
    def run_all_tests(self, skip_cleanup: bool = False):
        """Run all tests"""
        print("=" * 60)
        print("PERFORMANCE MANAGEMENT API TEST SUITE")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"API Base: {self.api_base}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_health_check()
        self.test_appraisal_cycles()
        self.test_performance_goals()
        self.test_self_assessment()
        self.test_360_feedback()
        self.test_error_handling()
        
        if not skip_cleanup:
            self.cleanup()
            
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['name']}")
                    if result['message']:
                        print(f"    {result['message']}")
        else:
            print("\n✅ ALL TESTS PASSED!")
            
        print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Return exit code
        return 0 if failed == 0 else 1


def main():
    parser = argparse.ArgumentParser(description='Test Performance Management API')
    parser.add_argument(
        '--base-url',
        default='http://localhost:8000',
        help='Base URL of the API (default: http://localhost:8000)'
    )
    parser.add_argument(
        '--token',
        required=True,
        help='JWT authentication token'
    )
    parser.add_argument(
        '--skip-cleanup',
        action='store_true',
        help='Skip cleanup of test data'
    )
    
    args = parser.parse_args()
    
    tester = PerformanceAPITester(args.base_url, args.token)
    exit_code = tester.run_all_tests(skip_cleanup=args.skip_cleanup)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
