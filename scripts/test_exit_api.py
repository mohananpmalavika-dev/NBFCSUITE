#!/usr/bin/env python3
"""
Exit Management API Testing Script
Tests all Exit Management API endpoints
"""

import sys
import os
from pathlib import Path
import asyncio
import httpx
from datetime import date, timedelta
from typing import Dict, Any
import json

# ANSI color codes
class Colors:
    OKGREEN = '\033[92m'
    OKBLUE = '\033[94m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    HEADER = '\033[95m'


def print_header(message: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(message: str):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_info(message: str):
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")


def print_warning(message: str):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


class ExitAPITester:
    """Exit Management API Tester"""
    
    def __init__(self, base_url: str = "http://localhost:8000", token: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1/hrms/exit"
        self.token = token
        self.headers = {}
        
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
        
        self.test_data = {}
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }
    
    async def test_endpoint(self, method: str, endpoint: str, data: Dict = None, 
                          params: Dict = None, expected_status: int = 200,
                          description: str = "") -> Dict:
        """Test a single API endpoint"""
        
        url = f"{self.api_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(url, headers=self.headers, params=params)
                elif method == "POST":
                    response = await client.post(url, headers=self.headers, json=data)
                elif method == "PUT":
                    response = await client.put(url, headers=self.headers, json=data)
                elif method == "DELETE":
                    response = await client.delete(url, headers=self.headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                success = response.status_code == expected_status
                
                if success:
                    print_success(f"{method} {endpoint} - {description or 'OK'} [{response.status_code}]")
                    self.test_results['passed'] += 1
                else:
                    print_error(f"{method} {endpoint} - Expected {expected_status}, got {response.status_code}")
                    self.test_results['failed'] += 1
                
                return {
                    'success': success,
                    'status_code': response.status_code,
                    'data': response.json() if response.content else None
                }
        
        except Exception as e:
            print_error(f"{method} {endpoint} - Error: {str(e)}")
            self.test_results['failed'] += 1
            return {
                'success': False,
                'error': str(e)
            }
    
    async def test_resignations(self):
        """Test resignation endpoints"""
        print_header("Testing Resignation Endpoints")
        
        # Test 1: List resignations
        result = await self.test_endpoint(
            "GET", "/resignations",
            description="List all resignations"
        )
        
        # Test 2: Create resignation
        resignation_data = {
            'employee_id': 'test-employee-id',  # Will need to be replaced with real ID
            'resignation_type': 'voluntary',
            'resignation_date': str(date.today()),
            'last_working_date': str(date.today() + timedelta(days=30)),
            'notice_period_days': 30,
            'reason_category': 'Better Opportunity',
            'reason_details': 'Test resignation for API testing purposes'
        }
        
        result = await self.test_endpoint(
            "POST", "/resignations",
            data=resignation_data,
            expected_status=201,
            description="Create new resignation"
        )
        
        if result.get('success') and result.get('data'):
            resignation_id = result['data'].get('id')
            self.test_data['resignation_id'] = resignation_id
            print_info(f"Created resignation with ID: {resignation_id}")
            
            # Test 3: Get resignation by ID
            await self.test_endpoint(
                "GET", f"/resignations/{resignation_id}",
                description="Get resignation by ID"
            )
            
            # Test 4: Update resignation
            update_data = {
                'reason_details': 'Updated resignation reason for testing'
            }
            await self.test_endpoint(
                "PUT", f"/resignations/{resignation_id}",
                data=update_data,
                description="Update resignation"
            )
            
            # Test 5: Manager review
            manager_review_data = {
                'manager_comments': 'Test manager review comments',
                'manager_recommendation': 'approve',
                'counter_offer_details': None
            }
            await self.test_endpoint(
                "POST", f"/resignations/{resignation_id}/manager-review",
                data=manager_review_data,
                description="Submit manager review"
            )
            
            # Test 6: HR review
            hr_review_data = {
                'hr_comments': 'Test HR review comments',
                're_employment_eligible': True,
                'blacklist_flag': False
            }
            await self.test_endpoint(
                "POST", f"/resignations/{resignation_id}/hr-review",
                data=hr_review_data,
                description="Submit HR review"
            )
            
            # Test 7: Approve resignation
            approval_data = {
                'approval_comments': 'Test approval comments',
                'actual_last_working_date': str(date.today() + timedelta(days=30))
            }
            await self.test_endpoint(
                "POST", f"/resignations/{resignation_id}/approve",
                data=approval_data,
                description="Approve resignation"
            )
        else:
            print_warning("Skipping resignation workflow tests due to creation failure")
            self.test_results['skipped'] += 6
    
    async def test_clearances(self):
        """Test clearance endpoints"""
        print_header("Testing Clearance Endpoints")
        
        # Test 1: List clearances
        result = await self.test_endpoint(
            "GET", "/clearances",
            description="List all clearances"
        )
        
        # Test 2: Create clearance (requires resignation_id)
        if 'resignation_id' in self.test_data:
            clearance_data = {
                'resignation_id': self.test_data['resignation_id'],
                'clearance_from': 'IT Department',
                'clearance_type': 'IT Assets',
                'description': 'Test clearance',
                'is_mandatory': True
            }
            
            result = await self.test_endpoint(
                "POST", "/clearances",
                data=clearance_data,
                expected_status=201,
                description="Create new clearance"
            )
            
            if result.get('success') and result.get('data'):
                clearance_id = result['data'].get('id')
                self.test_data['clearance_id'] = clearance_id
                
                # Test 3: Get clearance by ID
                await self.test_endpoint(
                    "GET", f"/clearances/{clearance_id}",
                    description="Get clearance by ID"
                )
                
                # Test 4: Complete clearance
                complete_data = {
                    'clearance_remarks': 'Test clearance completion remarks',
                    'supporting_documents': None
                }
                await self.test_endpoint(
                    "POST", f"/clearances/{clearance_id}/complete",
                    data=complete_data,
                    description="Complete clearance"
                )
        else:
            print_warning("Skipping clearance tests - no resignation_id available")
            self.test_results['skipped'] += 4
    
    async def test_settlements(self):
        """Test settlement endpoints"""
        print_header("Testing Settlement Endpoints")
        
        # Test 1: List settlements
        result = await self.test_endpoint(
            "GET", "/settlements",
            description="List all settlements"
        )
        
        # Test 2: Create settlement (requires resignation_id)
        if 'resignation_id' in self.test_data:
            settlement_data = {
                'resignation_id': self.test_data['resignation_id'],
                'employee_id': 'test-employee-id',
                'settlement_from_date': str(date.today().replace(day=1)),
                'settlement_to_date': str(date.today())
            }
            
            result = await self.test_endpoint(
                "POST", "/settlements",
                data=settlement_data,
                expected_status=201,
                description="Create new settlement"
            )
            
            if result.get('success') and result.get('data'):
                settlement_id = result['data'].get('id')
                self.test_data['settlement_id'] = settlement_id
                
                # Test 3: Get settlement by ID
                await self.test_endpoint(
                    "GET", f"/settlements/{settlement_id}",
                    description="Get settlement by ID"
                )
                
                # Test 4: Calculate settlement
                calculation_data = {
                    'basic_salary_amount': 30000,
                    'leave_encashment_amount': 5000,
                    'gratuity_amount': 50000,
                    'tds_amount': 5000
                }
                await self.test_endpoint(
                    "POST", f"/settlements/{settlement_id}/calculate",
                    data=calculation_data,
                    description="Calculate settlement"
                )
                
                # Test 5: Approve settlement
                approval_data = {
                    'approval_remarks': 'Test settlement approval'
                }
                await self.test_endpoint(
                    "POST", f"/settlements/{settlement_id}/approve",
                    data=approval_data,
                    description="Approve settlement"
                )
        else:
            print_warning("Skipping settlement tests - no resignation_id available")
            self.test_results['skipped'] += 5
    
    async def test_documents(self):
        """Test document endpoints"""
        print_header("Testing Document Endpoints")
        
        # Test 1: List documents
        result = await self.test_endpoint(
            "GET", "/documents",
            description="List all documents"
        )
        
        # Test 2: Generate document (requires resignation_id)
        if 'resignation_id' in self.test_data:
            document_data = {
                'document_type': 'experience_letter',
                'template_name': 'default',
                'document_number': f'EXP{date.today().strftime("%Y%m%d")}001',
                'issue_place': 'Mumbai'
            }
            
            result = await self.test_endpoint(
                "POST", f"/resignations/{self.test_data['resignation_id']}/documents/generate",
                data=document_data,
                expected_status=201,
                description="Generate document"
            )
            
            if result.get('success') and result.get('data'):
                document_id = result['data'].get('id')
                self.test_data['document_id'] = document_id
                
                # Test 3: Get document by ID
                await self.test_endpoint(
                    "GET", f"/documents/{document_id}",
                    description="Get document by ID"
                )
                
                # Test 4: Approve document
                approval_data = {
                    'approval_remarks': 'Test document approval'
                }
                await self.test_endpoint(
                    "POST", f"/documents/{document_id}/approve",
                    data=approval_data,
                    description="Approve document"
                )
                
                # Test 5: Issue document
                issuance_data = {
                    'issue_remarks': 'Test document issuance',
                    'delivery_mode': 'email',
                    'recipient_email': 'test@example.com'
                }
                await self.test_endpoint(
                    "POST", f"/documents/{document_id}/issue",
                    data=issuance_data,
                    description="Issue document"
                )
        else:
            print_warning("Skipping document tests - no resignation_id available")
            self.test_results['skipped'] += 5
    
    async def test_dashboard(self):
        """Test dashboard endpoints"""
        print_header("Testing Dashboard Endpoints")
        
        # Test 1: Get dashboard statistics
        await self.test_endpoint(
            "GET", "/dashboard/stats",
            description="Get dashboard statistics"
        )
    
    async def run_all_tests(self):
        """Run all API tests"""
        print_header("Exit Management API Testing Suite")
        print_info(f"Base URL: {self.base_url}")
        print_info(f"API URL: {self.api_url}\n")
        
        # Run all test suites
        await self.test_resignations()
        await self.test_clearances()
        await self.test_settlements()
        await self.test_documents()
        await self.test_dashboard()
        
        # Print summary
        print_header("Test Summary")
        total_tests = sum(self.test_results.values())
        
        print(f"{Colors.BOLD}Total Tests: {total_tests}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Passed: {self.test_results['passed']}{Colors.ENDC}")
        print(f"{Colors.FAIL}Failed: {self.test_results['failed']}{Colors.ENDC}")
        print(f"{Colors.WARNING}Skipped: {self.test_results['skipped']}{Colors.ENDC}")
        
        if self.test_results['failed'] == 0:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}All tests passed!{Colors.ENDC}")
        else:
            print(f"\n{Colors.WARNING}{Colors.BOLD}Some tests failed. Please review the logs.{Colors.ENDC}")
        
        success_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.ENDC}")


async def main():
    """Main entry point"""
    print("=" * 70)
    print("Exit Management API Testing Script".center(70))
    print("=" * 70 + "\n")
    
    # Get configuration from environment
    base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
    token = os.getenv('API_TOKEN')
    
    if not token:
        print_warning("No API token provided. Some tests may fail.")
        print_info("Set API_TOKEN environment variable to authenticate requests.\n")
    
    # Create tester and run tests
    tester = ExitAPITester(base_url=base_url, token=token)
    await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Testing interrupted{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}Error: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
