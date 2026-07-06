"""
Purity Testing Service
Manages gold purity testing and verification
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from fastapi import HTTPException

from backend.shared.database.gold_loan_models import (
    PurityTest,
    GoldOrnament,
    GoldLoanAccount
)
from backend.services.gold.schemas import (
    PurityTestCreateRequest,
    PurityTestUpdateRequest,
    PurityTestResponse
)


class PurityService:
    """Service for purity testing"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        
        # Acceptable variance thresholds (in percentage points)
        self.acceptable_variance = {
            "XRF": Decimal("1.0"),  # ±1% for XRF
            "Touchstone": Decimal("2.0"),  # ±2% for touchstone
            "Fire Assay": Decimal("0.5"),  # ±0.5% for fire assay
            "Acid Test": Decimal("2.5"),  # ±2.5% for acid test
            "Electronic Tester": Decimal("1.5")  # ±1.5% for electronic
        }
    
    def create_purity_test(
        self,
        test_data: PurityTestCreateRequest
    ) -> PurityTest:
        """
        Create new purity test record
        """
        # Validate ornament exists
        ornament = self.db.query(GoldOrnament).filter(
            and_(
                GoldOrnament.id == test_data.ornament_id,
                GoldOrnament.tenant_id == self.tenant_id
            )
        ).first()
        
        if not ornament:
            raise HTTPException(status_code=404, detail="Ornament not found")
        
        # Get loan details
        loan = self.db.query(GoldLoanAccount).filter(
            and_(
                GoldLoanAccount.id == test_data.gold_loan_id,
                GoldLoanAccount.tenant_id == self.tenant_id
            )
        ).first()
        
        if not loan:
            raise HTTPException(status_code=404, detail="Gold loan not found")
        
        # Calculate variance
        purity_variance = test_data.tested_purity_percentage - test_data.claimed_purity_percentage
        
        # Determine test result
        test_result = self._determine_test_result(
            test_data.test_method,
            abs(purity_variance)
        )
        
        # Generate test number
        test_number = self._generate_test_number()
        
        # Create purity test
        purity_test = PurityTest(
            tenant_id=self.tenant_id,
            test_number=test_number,
            test_date=test_data.test_date or datetime.utcnow(),
            gold_loan_id=test_data.gold_loan_id,
            ornament_id=test_data.ornament_id,
            customer_id=loan.customer_id,
            test_method=test_data.test_method,
            claimed_purity_karat=test_data.claimed_purity_karat,
            claimed_purity_percentage=test_data.claimed_purity_percentage,
            tested_purity_karat=test_data.tested_purity_karat,
            tested_purity_percentage=test_data.tested_purity_percentage,
            purity_variance=purity_variance,
            equipment_id=test_data.equipment_id,
            equipment_name=test_data.equipment_name,
            equipment_calibration_date=test_data.equipment_calibration_date,
            sample_weight=test_data.sample_weight,
            test_temperature=test_data.test_temperature,
            test_result=test_result,
            tested_by=self.user_id,
            tester_name=test_data.tester_name,
            tester_license=test_data.tester_license,
            verified_by=test_data.verified_by,
            test_photo_url=test_data.test_photo_url,
            remarks=test_data.remarks
        )
        
        self.db.add(purity_test)
        self.db.commit()
        self.db.refresh(purity_test)
        
        # Auto-update ornament if test passes
        if test_result == "Pass" and test_data.auto_update_ornament:
            self._update_ornament_purity(ornament, purity_test)
        
        return purity_test
    
    def update_purity_test(
        self,
        test_id: str,
        test_data: PurityTestUpdateRequest
    ) -> PurityTest:
        """
        Update purity test details
        """
        purity_test = self.db.query(PurityTest).filter(
            and_(
                PurityTest.id == test_id,
                PurityTest.tenant_id == self.tenant_id
            )
        ).first()
        
        if not purity_test:
            raise HTTPException(status_code=404, detail="Purity test not found")
        
        # Update fields
        if test_data.tested_purity_karat is not None:
            purity_test.tested_purity_karat = test_data.tested_purity_karat
        if test_data.tested_purity_percentage is not None:
            purity_test.tested_purity_percentage = test_data.tested_purity_percentage
            purity_test.purity_variance = test_data.tested_purity_percentage - purity_test.claimed_purity_percentage
            purity_test.test_result = self._determine_test_result(
                purity_test.test_method,
                abs(purity_test.purity_variance)
            )
        if test_data.action_taken is not None:
            purity_test.action_taken = test_data.action_taken
        if test_data.adjusted_value is not None:
            purity_test.adjusted_value = test_data.adjusted_value
        if test_data.certificate_number is not None:
            purity_test.certificate_number = test_data.certificate_number
        if test_data.certificate_url is not None:
            purity_test.certificate_url = test_data.certificate_url
        if test_data.report_url is not None:
            purity_test.report_url = test_data.report_url
        if test_data.remarks is not None:
            purity_test.remarks = test_data.remarks
        
        self.db.add(purity_test)
        self.db.commit()
        self.db.refresh(purity_test)
        
        return purity_test
    
    def get_purity_test(self, test_id: str) -> Optional[PurityTest]:
        """Get purity test by ID"""
        return self.db.query(PurityTest).filter(
            and_(
                PurityTest.id == test_id,
                PurityTest.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_purity_tests(
        self,
        loan_id: Optional[str] = None,
        ornament_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        test_method: Optional[str] = None,
        test_result: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[PurityTest]:
        """List purity tests with filters"""
        query = self.db.query(PurityTest).filter(
            PurityTest.tenant_id == self.tenant_id
        )
        
        if loan_id:
            query = query.filter(PurityTest.gold_loan_id == loan_id)
        if ornament_id:
            query = query.filter(PurityTest.ornament_id == ornament_id)
        if customer_id:
            query = query.filter(PurityTest.customer_id == customer_id)
        if test_method:
            query = query.filter(PurityTest.test_method == test_method)
        if test_result:
            query = query.filter(PurityTest.test_result == test_result)
        if start_date:
            query = query.filter(PurityTest.test_date >= start_date)
        if end_date:
            query = query.filter(PurityTest.test_date <= end_date)
        
        return query.order_by(desc(PurityTest.test_date)).all()
    
    def generate_test_certificate(
        self,
        test_id: str,
        certificate_number: Optional[str] = None,
        valid_days: int = 365
    ) -> PurityTest:
        """
        Generate purity test certificate
        """
        purity_test = self.get_purity_test(test_id)
        if not purity_test:
            raise HTTPException(status_code=404, detail="Purity test not found")
        
        if purity_test.test_result not in ["Pass", "Acceptable Variance"]:
            raise HTTPException(
                status_code=400,
                detail="Certificate can only be generated for passed tests"
            )
        
        # Generate certificate number if not provided
        if not certificate_number:
            certificate_number = self._generate_certificate_number(purity_test.test_number)
        
        purity_test.certificate_number = certificate_number
        purity_test.certificate_issued_date = datetime.utcnow()
        purity_test.certificate_valid_until = datetime.utcnow() + timedelta(days=valid_days)
        
        # In a real implementation, generate PDF certificate here
        # purity_test.certificate_url = generate_certificate_pdf(purity_test)
        
        self.db.add(purity_test)
        self.db.commit()
        self.db.refresh(purity_test)
        
        return purity_test
    
    def perform_bulk_testing(
        self,
        loan_id: str,
        test_method: str,
        tester_name: str,
        equipment_id: Optional[str] = None,
        equipment_name: Optional[str] = None
    ) -> List[PurityTest]:
        """
        Perform purity testing for all ornaments in a loan
        """
        # Get all ornaments for the loan
        ornaments = self.db.query(GoldOrnament).filter(
            and_(
                GoldOrnament.gold_loan_id == loan_id,
                GoldOrnament.tenant_id == self.tenant_id,
                GoldOrnament.is_active == True
            )
        ).all()
        
        if not ornaments:
            raise HTTPException(
                status_code=404,
                detail="No ornaments found for this loan"
            )
        
        tests = []
        for ornament in ornaments:
            # Create test request
            test_data = PurityTestCreateRequest(
                gold_loan_id=loan_id,
                ornament_id=ornament.id,
                test_method=test_method,
                claimed_purity_karat=ornament.purity_karat,
                claimed_purity_percentage=ornament.purity_percentage,
                tested_purity_karat=ornament.purity_karat,  # Will be updated
                tested_purity_percentage=ornament.purity_percentage,  # Will be updated
                tester_name=tester_name,
                equipment_id=equipment_id,
                equipment_name=equipment_name,
                auto_update_ornament=False
            )
            
            test = self.create_purity_test(test_data)
            tests.append(test)
        
        return tests
    
    def get_test_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        test_method: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get purity test statistics
        """
        query = self.db.query(PurityTest).filter(
            PurityTest.tenant_id == self.tenant_id
        )
        
        if start_date:
            query = query.filter(PurityTest.test_date >= start_date)
        if end_date:
            query = query.filter(PurityTest.test_date <= end_date)
        if test_method:
            query = query.filter(PurityTest.test_method == test_method)
        
        tests = query.all()
        
        if not tests:
            return {
                "total_tests": 0,
                "pass_rate": 0,
                "average_variance": 0
            }
        
        pass_count = sum(1 for t in tests if t.test_result == "Pass")
        acceptable_count = sum(1 for t in tests if t.test_result == "Acceptable Variance")
        fail_count = sum(1 for t in tests if t.test_result == "Fail")
        major_discrepancy_count = sum(1 for t in tests if t.test_result == "Major Discrepancy")
        
        variances = [abs(float(t.purity_variance)) for t in tests]
        avg_variance = sum(variances) / len(variances) if variances else 0
        
        return {
            "total_tests": len(tests),
            "pass_count": pass_count,
            "acceptable_variance_count": acceptable_count,
            "fail_count": fail_count,
            "major_discrepancy_count": major_discrepancy_count,
            "pass_rate": (pass_count / len(tests)) * 100,
            "acceptable_rate": ((pass_count + acceptable_count) / len(tests)) * 100,
            "average_variance_percentage": round(avg_variance, 2),
            "test_methods": self._get_method_breakdown(tests)
        }
    
    def verify_equipment_calibration(
        self,
        equipment_id: str,
        calibration_date: datetime,
        valid_days: int = 180
    ) -> Dict[str, Any]:
        """
        Verify if equipment calibration is valid
        """
        expiry_date = calibration_date + timedelta(days=valid_days)
        is_valid = datetime.utcnow() < expiry_date
        
        days_until_expiry = (expiry_date - datetime.utcnow()).days
        
        return {
            "equipment_id": equipment_id,
            "calibration_date": calibration_date,
            "expiry_date": expiry_date,
            "is_valid": is_valid,
            "days_until_expiry": days_until_expiry,
            "requires_recalibration": days_until_expiry <= 30
        }
    
    def flag_discrepancy(
        self,
        test_id: str,
        action_taken: str,
        adjusted_value: Optional[Decimal] = None,
        remarks: Optional[str] = None
    ) -> PurityTest:
        """
        Flag and handle purity test discrepancy
        """
        purity_test = self.get_purity_test(test_id)
        if not purity_test:
            raise HTTPException(status_code=404, detail="Purity test not found")
        
        purity_test.action_taken = action_taken
        purity_test.adjusted_value = adjusted_value
        
        if remarks:
            purity_test.remarks = f"{purity_test.remarks or ''}\nDiscrepancy: {remarks}"
        
        # Update ornament if value adjusted
        if action_taken == "Value Adjusted" and adjusted_value:
            ornament = self.db.query(GoldOrnament).filter(
                and_(
                    GoldOrnament.id == purity_test.ornament_id,
                    GoldOrnament.tenant_id == self.tenant_id
                )
            ).first()
            
            if ornament:
                ornament.appraised_value = adjusted_value
                ornament.purity_percentage = purity_test.tested_purity_percentage
                ornament.purity_karat = purity_test.tested_purity_karat
                self.db.add(ornament)
        
        self.db.add(purity_test)
        self.db.commit()
        self.db.refresh(purity_test)
        
        return purity_test
    
    # ==================== Helper Methods ====================
    
    def _determine_test_result(
        self,
        test_method: str,
        variance: Decimal
    ) -> str:
        """
        Determine test result based on variance and method
        """
        acceptable = self.acceptable_variance.get(test_method, Decimal("2.0"))
        
        if variance == Decimal("0.0"):
            return "Pass"
        elif variance <= acceptable:
            return "Acceptable Variance"
        elif variance <= acceptable * 2:
            return "Fail"
        else:
            return "Major Discrepancy"
    
    def _update_ornament_purity(
        self,
        ornament: GoldOrnament,
        purity_test: PurityTest
    ) -> None:
        """
        Update ornament with tested purity values
        """
        ornament.purity_karat = purity_test.tested_purity_karat
        ornament.purity_percentage = purity_test.tested_purity_percentage
        
        # Recalculate value based on new purity
        purity_ratio = purity_test.tested_purity_percentage / ornament.purity_percentage
        ornament.market_value = ornament.market_value * purity_ratio
        ornament.appraised_value = ornament.appraised_value * purity_ratio
        
        self.db.add(ornament)
    
    def _generate_test_number(self) -> str:
        """Generate unique test number"""
        count = self.db.query(func.count(PurityTest.id)).filter(
            PurityTest.tenant_id == self.tenant_id
        ).scalar()
        
        return f"PT-{datetime.utcnow().strftime('%Y%m%d')}-{count + 1:05d}"
    
    def _generate_certificate_number(self, test_number: str) -> str:
        """Generate certificate number from test number"""
        return f"CERT-{test_number}"
    
    def _get_method_breakdown(self, tests: List[PurityTest]) -> Dict[str, int]:
        """Get breakdown of tests by method"""
        methods = {}
        for test in tests:
            method = test.test_method
            methods[method] = methods.get(method, 0) + 1
        return methods
