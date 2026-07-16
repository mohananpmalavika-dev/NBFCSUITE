"""
Instant Decision Framework Service
Real-time decisioning with parallel async checks
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from .decision_engine_models import (
    DecisionRequest, BureauCheck, BankStatementAnalysis,
    KYCVerification, FraudCheck, EligibilityCheck, DecisionAudit,
    DecisionStatus, DecisionOutcome, CheckStatus, CheckResult,
    BureauProvider, FraudRiskLevel, DeclineReason,
    DecisionRequestCreate
)


class DecisionEngineService:
    """Service for instant decision framework"""
    
    def __init__(self, db: Session, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.decision_timeout = 60  # seconds
    
    # =====================================================================
    # MAIN DECISION FLOW
    # =====================================================================
    
    async def process_decision(
        self,
        request_data: DecisionRequestCreate,
        user_id: UUID
    ) -> DecisionRequest:
        """
        Main decision processing flow with parallel checks
        Target: < 60 seconds total time
        """
        start_time = datetime.utcnow()
        
        # Create decision request
        decision_request = DecisionRequest(
            tenant_id=self.tenant_id,
            application_id=request_data.application_id,
            customer_id=request_data.customer_id,
            product_id=request_data.product_id,
            loan_amount=request_data.loan_amount,
            tenure_months=request_data.tenure_months,
            purpose=request_data.purpose,
            applicant_data=request_data.applicant_data,
            status=DecisionStatus.IN_PROGRESS,
            request_time=start_time,
            start_time=start_time,
            created_by=user_id
        )
        
        self.db.add(decision_request)
        self.db.flush()  # Get the ID
        
        # Log request received
        self._log_audit(decision_request.id, "REQUEST_RECEIVED", "Decision request created")
        
        try:
            # Run all checks in parallel
            check_results = await asyncio.gather(
                self._run_bureau_checks(decision_request),
                self._run_bank_statement_analysis(decision_request),
                self._run_kyc_verification(decision_request),
                self._run_fraud_check(decision_request),
                self._run_eligibility_check(decision_request),
                return_exceptions=True
            )
            
            # Aggregate results
            bureau_result, bank_result, kyc_result, fraud_result, eligibility_result = check_results
            
            # Count checks
            total_checks = 5
            passed_checks = 0
            failed_checks = 0
            warning_checks = 0
            
            for result in check_results:
                if isinstance(result, Exception):
                    failed_checks += 1
                elif result == CheckResult.PASS:
                    passed_checks += 1
                elif result == CheckResult.FAIL:
                    failed_checks += 1
                elif result == CheckResult.WARNING:
                    warning_checks += 1
            
            decision_request.total_checks = total_checks
            decision_request.passed_checks = passed_checks
            decision_request.failed_checks = failed_checks
            decision_request.warning_checks = warning_checks
            
            # Calculate decision score
            decision_score = self._calculate_decision_score(decision_request)
            decision_request.decision_score = decision_score
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(decision_request)
            decision_request.confidence_score = confidence_score
            
            # Make final decision
            decision_outcome, approved_amount, approved_rate, decline_reasons, conditions = \
                self._make_final_decision(decision_request, decision_score)
            
            decision_request.decision_outcome = decision_outcome
            decision_request.approved_amount = approved_amount
            decision_request.approved_rate = approved_rate
            decision_request.decline_reasons = decline_reasons
            decision_request.conditions = conditions
            
            # Check if manual review is needed
            if self._requires_manual_review(decision_request):
                decision_request.requires_manual_review = True
                decision_request.manual_review_reason = "Decision criteria require manual review"
            
            # Mark as completed
            decision_request.status = DecisionStatus.COMPLETED
            
        except Exception as e:
            decision_request.status = DecisionStatus.FAILED
            self._log_audit(decision_request.id, "DECISION_FAILED", f"Error: {str(e)}")
            raise
        
        finally:
            # Calculate total duration
            end_time = datetime.utcnow()
            decision_request.end_time = end_time
            duration = (end_time - start_time).total_seconds() * 1000
            decision_request.total_duration_ms = int(duration)
            
            self.db.commit()
            self.db.refresh(decision_request)
            
            self._log_audit(
                decision_request.id, 
                "DECISION_COMPLETED", 
                f"Decision: {decision_request.decision_outcome}, Score: {decision_request.decision_score}"
            )
        
        return decision_request
    
    # =====================================================================
    # PARALLEL CHECK METHODS
    # =====================================================================
    
    async def _run_bureau_checks(self, decision_request: DecisionRequest) -> CheckResult:
        """Run credit bureau checks (simulated for now)"""
        start_time = datetime.utcnow()
        
        try:
            # Simulate bureau API call (in production, call actual bureau APIs)
            await asyncio.sleep(0.5)  # Simulate API delay
            
            # For demo, use data from applicant_data
            applicant_data = decision_request.applicant_data
            credit_score = applicant_data.get('credit_score', 750)
            
            # Create bureau check record
            bureau_check = BureauCheck(
                decision_request_id=decision_request.id,
                tenant_id=self.tenant_id,
                bureau_provider=BureauProvider.CIBIL,
                status=CheckStatus.COMPLETED,
                credit_score=credit_score,
                total_accounts=applicant_data.get('total_accounts', 5),
                active_accounts=applicant_data.get('active_accounts', 3),
                total_outstanding=applicant_data.get('total_outstanding', 100000.0),
                credit_utilization=applicant_data.get('credit_utilization', 30.0),
                max_dpd_last_12m=applicant_data.get('max_dpd_last_12m', 0),
                enquiries_last_6m=applicant_data.get('enquiries_last_6m', 2),
                start_time=start_time,
                end_time=datetime.utcnow()
            )
            
            # Determine result
            if credit_score >= 700:
                bureau_check.result = CheckResult.PASS
            elif credit_score >= 600:
                bureau_check.result = CheckResult.WARNING
            else:
                bureau_check.result = CheckResult.FAIL
            
            bureau_check.duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            self.db.add(bureau_check)
            self.db.flush()
            
            self._log_audit(
                decision_request.id,
                "BUREAU_CHECK_COMPLETED",
                f"Credit Score: {credit_score}, Result: {bureau_check.result}"
            )
            
            return bureau_check.result
            
        except Exception as e:
            bureau_check = BureauCheck(
                decision_request_id=decision_request.id,
                tenant_id=self.tenant_id,
                bureau_provider=BureauProvider.CIBIL,
                status=CheckStatus.FAILED,
                result=CheckResult.FAIL,
                error_message=str(e),
                start_time=start_time,
                end_time=datetime.utcnow()
            )
            self.db.add(bureau_check)
            self.db.flush()
            return CheckResult.FAIL
    
    async def _run_bank_statement_analysis(self, decision_request: DecisionRequest) -> CheckResult:
        """Run bank statement AI analysis (simulated)"""
        start_time = datetime.utcnow()
        
        try:
            # Simulate bank statement analysis
            await asyncio.sleep(0.8)  # Simulate processing delay
            
            applicant_data = decision_request.applicant_data
            monthly_income = applicant_data.get('monthly_income', 50000.0)
            monthly_obligations = applicant_data.get('monthly_obligations', 15000.0)
            
            # Calculate DTI
            dti = (monthly_obligations / monthly_income) * 100 if monthly_income > 0 else 100
            
            analysis = BankStatementAnalysis(
                decision_request_id=decision_request.id,
                tenant_id=self.tenant_id,
                status=CheckStatus.COMPLETED,
                statement_period_months=6,
                bank_name="Demo Bank",
                average_monthly_credit=monthly_income,
                salary_credits_count=6,
                salary_amount=monthly_income,
                salary_regularity_score=95.0,
                average_monthly_debit=monthly_obligations + 5000,
                emi_deductions=monthly_obligations,
                average_balance=monthly_income * 0.3,
                bounced_cheques_count=0,
                banking_behavior_score=85.0,
                calculated_monthly_income=monthly_income,
                calculated_monthly_obligations=monthly_obligations,
                calculated_dti=dti,
                start_time=start_time,
                end_time=datetime.utcnow()
            )
            
            # Determine result
            if dti <= 40 and analysis.bounced_cheques_count == 0:
                analysis.result = CheckResult.PASS
            elif dti <= 50:
                analysis.result = CheckResult.WARNING
            else:
                analysis.result = CheckResult.FAIL
            
            analysis.duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            self.db.add(analysis)
            self.db.flush()
            
            self._log_audit(
                decision_request.id,
                "BANK_STATEMENT_COMPLETED",
                f"DTI: {dti:.2f}%, Banking Score: {analysis.banking_behavior_score}"
            )
            
            return analysis.result
            
        except Exception as e:
            analysis = BankStatementAnalysis(
                decision_request_id=decision_request.id,
                tenant_id=self.tenant_id,
                status=CheckStatus.FAILED,
                result=CheckResult.FAIL,
                error_message=str(e),
                start_time=start_time,
                end_time=datetime.utcnow()
            )
            self.db.add(analysis)
            self.db.flush()
            return CheckResult.FAIL
    
    async def _run_kyc_verification(self, decision_request: DecisionRequest) -> CheckResult:
        """Run KYC verification (simulated)"""
        start_time = datetime.utcnow()
        
        try:
            # Simulate KYC verification
            await asyncio.sleep(0.6)
            
            applicant_data = decision_request.applicant_data
            
            kyc = KYCVerification(
                decision_request_id=decision_request.id,
                tenant_id=self.tenant_id,
                status=CheckStatus.COMPLETED,
                aadhaar_verified=True,
                aadhaar_name_match=True,
                aadhaar_address_match=True,
                aadhaar_dob_match=True,
                pan_verified=True,
                pan_name_match=True,
                pan_dob_match=True,
                pan_status="Active",
                address_verified=True,
                address_match_score=95.0,
                employment_verified=applicant_data.get('employment_verified', True),
                kyc_score=95.0,
                start_time=start_time,
                end_time=datetime.utcnow()
            )
            
            # Determine result
            if kyc.kyc_score >= 80:
                kyc.result = CheckResult.PASS
            elif kyc.kyc_score >= 60:
                kyc.result = CheckResult.WARNING
            else:
                kyc.result = CheckResult.FAIL
            
            kyc.duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            self.db.add(kyc)
            self.db.flush()
            
            self._log_audit(
                decision_request.id,
                "KYC_VERIFICATION_COMPLETED",
                f"KYC Score: {kyc.kyc_score}, Aadhaar: {kyc.aadhaar_verified}, PAN: {kyc.pan_verified}"
            )
            
            return kyc.result
            
        except Exception as e:
            kyc = KYCVerification(
                decision_request_id=decision_request.id,
                tenant_id=self.tenant_id,
                status=CheckStatus.FAILED,
                result=CheckResult.FAIL,
                error_message=str(e),
                start_time=start_time,
                end_time=datetime.utcnow()
            )
            self.db.add(kyc)
            self.db.flush()
            return CheckResult.FAIL
    
    async def _run_fraud_check(self, decision_request: DecisionRequest) -> CheckResult:
        """Run fraud detection check (simulated)"""
        start_time = datetime.utcnow()
        
        try:
            # Simulate fraud check
            await asyncio.sleep(0.4)
            
            applicant_data = decision_request.applicant_data
            
            # Check velocity
            recent_apps = self._get_recent_applications(decision_request.customer_id)
            
            fraud = FraudCheck(
                decision_request_id=decision_request.id,
                tenant_id=self.tenant_id,
                status=CheckStatus.COMPLETED,
                device_id=applicant_data.get('device_id', 'DEV123'),
                device_type=applicant_data.get('device_type', 'Mobile'),
                device_risk_score=10.0,
                ip_address=applicant_data.get('ip_address', '192.168.1.1'),
                geo_country="India",
                geo_state=applicant_data.get('state', 'Maharashtra'),
                geo_city=applicant_data.get('city', 'Mumbai'),
                geo_risk_score=5.0,
                applications_last_24h=recent_apps['last_24h'],
                applications_last_7d=recent_apps['last_7d'],
                applications_last_30d=recent_apps['last_30d'],
                velocity_risk_score=15.0 if recent_apps['last_24h'] > 2 else 5.0,
                duplicate_applications=0,
                duplicate_phone=False,
                duplicate_email=False,
                blacklisted=False,
                email_verified=True,
                email_risk_score=5.0,
                phone_verified=True,
                phone_risk_score=5.0,
                fraud_score=10.0,  # Low fraud score
                fraud_risk_level=FraudRiskLevel.LOW,
                fraud_indicators=[],
                start_time=start_time,
                end_time=datetime.utcnow()
            )
            
            # Determine result based on fraud score
            if fraud.fraud_score <= 30:
                fraud.result = CheckResult.PASS
            elif fraud.fraud_score <= 60:
                fraud.result = CheckResult.WARNING
            else:
                fraud.result = CheckResult.FAIL
            
            fraud.duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Update decision request fraud info
            decision_request.fraud_score = fraud.fraud_score
            decision_request.fraud_risk_level = fraud.fraud_risk_level
            decision_request.fraud_indicators = fraud.fraud_indicators
            
            self.db.add(fraud)
            self.db.flush()
            
            self._log_audit(
                decision_request.id,
                "FRAUD_CHECK_COMPLETED",
                f"Fraud Score: {fraud.fraud_score}, Risk Level: {fraud.fraud_risk_level}"
            )
            
            return fraud.result
            
        except Exception as e:
            fraud = FraudCheck(
                decision_request_id=decision_request.id,
                tenant_id=self.tenant_id,
                status=CheckStatus.FAILED,
                result=CheckResult.FAIL,
                error_message=str(e),
                start_time=start_time,
                end_time=datetime.utcnow()
            )
            self.db.add(fraud)
            self.db.flush()
            return CheckResult.FAIL
    
    async def _run_eligibility_check(self, decision_request: DecisionRequest) -> CheckResult:
        """Run eligibility and business rules check"""
        start_time = datetime.utcnow()
        
        try:
            # Simulate eligibility check
            await asyncio.sleep(0.3)
            
            applicant_data = decision_request.applicant_data
            
            # Get bureau data for credit score
            bureau_check = self.db.query(BureauCheck).filter(
                BureauCheck.decision_request_id == decision_request.id
            ).first()
            
            credit_score = bureau_check.credit_score if bureau_check else applicant_data.get('credit_score', 750)
            
            # Get bank statement data for DTI
            bank_analysis = self.db.query(BankStatementAnalysis).filter(
                BankStatementAnalysis.decision_request_id == decision_request.id
            ).first()
            
            monthly_income = bank_analysis.calculated_monthly_income if bank_analysis else applicant_data.get('monthly_income', 50000.0)
            monthly_obligations = bank_analysis.calculated_monthly_obligations if bank_analysis else applicant_data.get('monthly_obligations', 15000.0)
            dti = (monthly_obligations / monthly_income * 100) if monthly_income > 0 else 100
            
            age = applicant_data.get('age', 30)
            
            eligibility = EligibilityCheck(
                decision_request_id=decision_request.id,
                tenant_id=self.tenant_id,
                status=CheckStatus.COMPLETED,
                age=age,
                age_eligible=21 <= age <= 65,
                min_age=21,
                max_age=65,
                monthly_income=monthly_income,
                income_eligible=monthly_income >= 25000,
                min_income=25000,
                monthly_obligations=monthly_obligations,
                dti_ratio=dti,
                dti_eligible=dti <= 50,
                max_dti=50,
                employment_type=applicant_data.get('employment_type', 'SALARIED'),
                employment_duration_months=applicant_data.get('employment_duration', 24),
                employment_eligible=applicant_data.get('employment_duration', 24) >= 6,
                min_employment_months=6,
                credit_score=credit_score,
                credit_score_eligible=credit_score >= 650,
                min_credit_score=650,
                requested_amount=decision_request.loan_amount,
                amount_eligible=10000 <= decision_request.loan_amount <= 1000000,
                min_loan_amount=10000,
                max_loan_amount=1000000,
                geography_eligible=True,
                product_rules_passed=True,
                policy_rules_passed=True,
                start_time=start_time,
                end_time=datetime.utcnow()
            )
            
            # Check overall eligibility
            failed_criteria = []
            if not eligibility.age_eligible:
                failed_criteria.append("Age not in range")
            if not eligibility.income_eligible:
                failed_criteria.append("Insufficient income")
            if not eligibility.dti_eligible:
                failed_criteria.append("DTI too high")
            if not eligibility.employment_eligible:
                failed_criteria.append("Insufficient employment duration")
            if not eligibility.credit_score_eligible:
                failed_criteria.append("Credit score below minimum")
            if not eligibility.amount_eligible:
                failed_criteria.append("Loan amount out of range")
            
            eligibility.overall_eligible = len(failed_criteria) == 0
            eligibility.failed_criteria = failed_criteria
            
            # Calculate eligibility score
            passed_checks = sum([
                eligibility.age_eligible,
                eligibility.income_eligible,
                eligibility.dti_eligible,
                eligibility.employment_eligible,
                eligibility.credit_score_eligible,
                eligibility.amount_eligible
            ])
            eligibility.eligibility_score = (passed_checks / 6) * 100
            
            # Determine result
            if eligibility.overall_eligible:
                eligibility.result = CheckResult.PASS
            elif eligibility.eligibility_score >= 70:
                eligibility.result = CheckResult.WARNING
            else:
                eligibility.result = CheckResult.FAIL
            
            eligibility.duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            self.db.add(eligibility)
            self.db.flush()
            
            self._log_audit(
                decision_request.id,
                "ELIGIBILITY_CHECK_COMPLETED",
                f"Eligibility Score: {eligibility.eligibility_score}, Overall: {eligibility.overall_eligible}"
            )
            
            return eligibility.result
            
        except Exception as e:
            eligibility = EligibilityCheck(
                decision_request_id=decision_request.id,
                tenant_id=self.tenant_id,
                status=CheckStatus.FAILED,
                result=CheckResult.FAIL,
                error_message=str(e),
                start_time=start_time,
                end_time=datetime.utcnow()
            )
            self.db.add(eligibility)
            self.db.flush()
            return CheckResult.FAIL
    
    # =====================================================================
    # DECISION LOGIC
    # =====================================================================
    
    def _calculate_decision_score(self, decision_request: DecisionRequest) -> float:
        """Calculate overall decision score (0-100)"""
        scores = []
        weights = []
        
        # Bureau check (weight: 30%)
        bureau = self.db.query(BureauCheck).filter(
            BureauCheck.decision_request_id == decision_request.id
        ).first()
        if bureau and bureau.credit_score:
            # Normalize credit score (300-900 -> 0-100)
            bureau_score = ((bureau.credit_score - 300) / 600) * 100
            scores.append(bureau_score)
            weights.append(0.30)
        
        # Bank statement (weight: 25%)
        bank = self.db.query(BankStatementAnalysis).filter(
            BankStatementAnalysis.decision_request_id == decision_request.id
        ).first()
        if bank and bank.banking_behavior_score:
            scores.append(bank.banking_behavior_score)
            weights.append(0.25)
        
        # KYC (weight: 15%)
        kyc = self.db.query(KYCVerification).filter(
            KYCVerification.decision_request_id == decision_request.id
        ).first()
        if kyc and kyc.kyc_score:
            scores.append(kyc.kyc_score)
            weights.append(0.15)
        
        # Fraud (weight: 20%, inverted)
        fraud = self.db.query(FraudCheck).filter(
            FraudCheck.decision_request_id == decision_request.id
        ).first()
        if fraud and fraud.fraud_score is not None:
            # Invert fraud score (lower fraud = higher score)
            fraud_score = 100 - fraud.fraud_score
            scores.append(fraud_score)
            weights.append(0.20)
        
        # Eligibility (weight: 10%)
        eligibility = self.db.query(EligibilityCheck).filter(
            EligibilityCheck.decision_request_id == decision_request.id
        ).first()
        if eligibility and eligibility.eligibility_score:
            scores.append(eligibility.eligibility_score)
            weights.append(0.10)
        
        # Calculate weighted average
        if scores and weights:
            total_weight = sum(weights)
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
            return round(weighted_score, 2)
        
        return 0.0
    
    def _calculate_confidence_score(self, decision_request: DecisionRequest) -> float:
        """Calculate confidence in the decision (0-100)"""
        confidence = 100.0
        
        # Reduce confidence for missing checks
        if decision_request.failed_checks > 0:
            confidence -= decision_request.failed_checks * 15
        
        # Reduce confidence for warnings
        if decision_request.warning_checks > 0:
            confidence -= decision_request.warning_checks * 5
        
        # Reduce confidence if close to threshold
        if decision_request.decision_score:
            if 45 <= decision_request.decision_score <= 55:
                confidence -= 10  # Borderline case
        
        return max(0.0, min(100.0, confidence))
    
    def _make_final_decision(
        self,
        decision_request: DecisionRequest,
        decision_score: float
    ) -> Tuple[DecisionOutcome, Optional[float], Optional[float], List[str], List[str]]:
        """Make final decision based on all checks"""
        
        decline_reasons = []
        conditions = []
        approved_amount = None
        approved_rate = None
        
        # Get check results
        eligibility = self.db.query(EligibilityCheck).filter(
            EligibilityCheck.decision_request_id == decision_request.id
        ).first()
        
        fraud = self.db.query(FraudCheck).filter(
            FraudCheck.decision_request_id == decision_request.id
        ).first()
        
        bureau = self.db.query(BureauCheck).filter(
            BureauCheck.decision_request_id == decision_request.id
        ).first()
        
        # Hard declines (auto-reject)
        if fraud and fraud.fraud_risk_level in [FraudRiskLevel.HIGH, FraudRiskLevel.CRITICAL]:
            decline_reasons.append("High fraud risk detected")
            return DecisionOutcome.DECLINED, None, None, decline_reasons, []
        
        if eligibility and not eligibility.overall_eligible:
            decline_reasons.extend(eligibility.failed_criteria)
            return DecisionOutcome.DECLINED, None, None, decline_reasons, []
        
        if bureau and bureau.credit_score and bureau.credit_score < 600:
            decline_reasons.append("Credit score below minimum threshold")
            return DecisionOutcome.DECLINED, None, None, decline_reasons, []
        
        # Approve with score-based pricing
        if decision_score >= 70:
            # Strong approval
            approved_amount = decision_request.loan_amount
            
            # Risk-based pricing
            if decision_score >= 85:
                approved_rate = 12.0  # Best rate
            elif decision_score >= 75:
                approved_rate = 14.0  # Good rate
            else:
                approved_rate = 16.0  # Standard rate
            
            return DecisionOutcome.APPROVED, approved_amount, approved_rate, [], conditions
        
        elif decision_score >= 55:
            # Conditional approval
            approved_amount = decision_request.loan_amount * 0.8  # 80% of requested
            approved_rate = 18.0  # Higher rate
            
            conditions.append("Additional documentation required")
            conditions.append("Co-applicant recommended")
            
            return DecisionOutcome.APPROVED_WITH_CONDITIONS, approved_amount, approved_rate, [], conditions
        
        elif decision_score >= 45:
            # Manual review required
            decline_reasons.append("Score in borderline range - requires manual assessment")
            return DecisionOutcome.MANUAL_REVIEW, None, None, decline_reasons, []
        
        else:
            # Decline
            decline_reasons.append("Decision score below minimum threshold")
            return DecisionOutcome.DECLINED, None, None, decline_reasons, []
    
    def _requires_manual_review(self, decision_request: DecisionRequest) -> bool:
        """Check if manual review is needed"""
        
        # Check for borderline scores
        if decision_request.decision_score and 45 <= decision_request.decision_score <= 55:
            return True
        
        # Check for low confidence
        if decision_request.confidence_score and decision_request.confidence_score < 60:
            return True
        
        # Check for medium fraud risk
        fraud = self.db.query(FraudCheck).filter(
            FraudCheck.decision_request_id == decision_request.id
        ).first()
        if fraud and fraud.fraud_risk_level == FraudRiskLevel.MEDIUM:
            return True
        
        # Check for warnings
        if decision_request.warning_checks >= 2:
            return True
        
        return False
    
    def _get_recent_applications(self, customer_id: UUID) -> Dict[str, int]:
        """Get count of recent applications by customer"""
        now = datetime.utcnow()
        
        last_24h = self.db.query(func.count(DecisionRequest.id)).filter(
            and_(
                DecisionRequest.customer_id == customer_id,
                DecisionRequest.request_time >= now - timedelta(hours=24),
                DecisionRequest.tenant_id == self.tenant_id
            )
        ).scalar() or 0
        
        last_7d = self.db.query(func.count(DecisionRequest.id)).filter(
            and_(
                DecisionRequest.customer_id == customer_id,
                DecisionRequest.request_time >= now - timedelta(days=7),
                DecisionRequest.tenant_id == self.tenant_id
            )
        ).scalar() or 0
        
        last_30d = self.db.query(func.count(DecisionRequest.id)).filter(
            and_(
                DecisionRequest.customer_id == customer_id,
                DecisionRequest.request_time >= now - timedelta(days=30),
                DecisionRequest.tenant_id == self.tenant_id
            )
        ).scalar() or 0
        
        return {
            'last_24h': last_24h,
            'last_7d': last_7d,
            'last_30d': last_30d
        }
    
    def _log_audit(self, decision_request_id: UUID, action: str, details: str):
        """Log audit trail"""
        audit = DecisionAudit(
            decision_request_id=decision_request_id,
            tenant_id=self.tenant_id,
            action=action,
            details=details,
            timestamp=datetime.utcnow()
        )
        self.db.add(audit)
        self.db.flush()
    
    # =====================================================================
    # CRUD OPERATIONS
    # =====================================================================
    
    def get_decision(self, decision_id: UUID) -> Optional[DecisionRequest]:
        """Get decision by ID"""
        return self.db.query(DecisionRequest).filter(
            and_(
                DecisionRequest.id == decision_id,
                DecisionRequest.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_decisions(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[DecisionStatus] = None,
        outcome: Optional[DecisionOutcome] = None,
        customer_id: Optional[UUID] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[DecisionRequest]:
        """List decisions with filters"""
        query = self.db.query(DecisionRequest).filter(
            DecisionRequest.tenant_id == self.tenant_id
        )
        
        if status:
            query = query.filter(DecisionRequest.status == status)
        
        if outcome:
            query = query.filter(DecisionRequest.decision_outcome == outcome)
        
        if customer_id:
            query = query.filter(DecisionRequest.customer_id == customer_id)
        
        if from_date:
            query = query.filter(DecisionRequest.request_time >= from_date)
        
        if to_date:
            query = query.filter(DecisionRequest.request_time <= to_date)
        
        return query.order_by(DecisionRequest.request_time.desc()).offset(skip).limit(limit).all()
    
    def get_decision_details(self, decision_id: UUID) -> Optional[Dict[str, Any]]:
        """Get decision with all check details"""
        decision = self.get_decision(decision_id)
        if not decision:
            return None
        
        # Get all checks
        bureau = self.db.query(BureauCheck).filter(
            BureauCheck.decision_request_id == decision_id
        ).all()
        
        bank_analysis = self.db.query(BankStatementAnalysis).filter(
            BankStatementAnalysis.decision_request_id == decision_id
        ).all()
        
        kyc = self.db.query(KYCVerification).filter(
            KYCVerification.decision_request_id == decision_id
        ).all()
        
        fraud = self.db.query(FraudCheck).filter(
            FraudCheck.decision_request_id == decision_id
        ).all()
        
        eligibility = self.db.query(EligibilityCheck).filter(
            EligibilityCheck.decision_request_id == decision_id
        ).all()
        
        audit = self.db.query(DecisionAudit).filter(
            DecisionAudit.decision_request_id == decision_id
        ).order_by(DecisionAudit.timestamp).all()
        
        return {
            "decision": decision,
            "bureau_checks": bureau,
            "bank_analysis": bank_analysis,
            "kyc_verification": kyc,
            "fraud_checks": fraud,
            "eligibility_checks": eligibility,
            "audit_trail": audit
        }
    
    async def rerun_decision(
        self,
        original_decision_id: UUID,
        user_id: UUID
    ) -> DecisionRequest:
        """Rerun decision with same inputs"""
        original = self.get_decision(original_decision_id)
        if not original:
            raise ValueError("Original decision not found")
        
        # Create new request with same data
        request_data = DecisionRequestCreate(
            application_id=original.application_id,
            customer_id=original.customer_id,
            product_id=original.product_id,
            loan_amount=original.loan_amount,
            tenure_months=original.tenure_months,
            purpose=original.purpose,
            applicant_data=original.applicant_data
        )
        
        return await self.process_decision(request_data, user_id)
    
    # =====================================================================
    # ANALYTICS & REPORTING
    # =====================================================================
    
    def get_decision_statistics(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get decision statistics"""
        query = self.db.query(DecisionRequest).filter(
            DecisionRequest.tenant_id == self.tenant_id
        )
        
        if from_date:
            query = query.filter(DecisionRequest.request_time >= from_date)
        
        if to_date:
            query = query.filter(DecisionRequest.request_time <= to_date)
        
        total_decisions = query.count()
        
        # Count by outcome
        approved = query.filter(DecisionRequest.decision_outcome == DecisionOutcome.APPROVED).count()
        approved_conditions = query.filter(
            DecisionRequest.decision_outcome == DecisionOutcome.APPROVED_WITH_CONDITIONS
        ).count()
        declined = query.filter(DecisionRequest.decision_outcome == DecisionOutcome.DECLINED).count()
        manual_review = query.filter(DecisionRequest.decision_outcome == DecisionOutcome.MANUAL_REVIEW).count()
        
        # Approval rate
        approval_rate = ((approved + approved_conditions) / total_decisions * 100) if total_decisions > 0 else 0
        
        # Average scores
        avg_decision_score = self.db.query(func.avg(DecisionRequest.decision_score)).filter(
            DecisionRequest.tenant_id == self.tenant_id,
            DecisionRequest.decision_score.isnot(None)
        ).scalar() or 0
        
        avg_confidence_score = self.db.query(func.avg(DecisionRequest.confidence_score)).filter(
            DecisionRequest.tenant_id == self.tenant_id,
            DecisionRequest.confidence_score.isnot(None)
        ).scalar() or 0
        
        # Average processing time
        avg_duration = self.db.query(func.avg(DecisionRequest.total_duration_ms)).filter(
            DecisionRequest.tenant_id == self.tenant_id,
            DecisionRequest.total_duration_ms.isnot(None)
        ).scalar() or 0
        
        # Count by fraud risk level
        fraud_stats = self.db.query(
            DecisionRequest.fraud_risk_level,
            func.count(DecisionRequest.id)
        ).filter(
            DecisionRequest.tenant_id == self.tenant_id
        ).group_by(DecisionRequest.fraud_risk_level).all()
        
        return {
            "total_decisions": total_decisions,
            "approved": approved,
            "approved_with_conditions": approved_conditions,
            "declined": declined,
            "manual_review": manual_review,
            "approval_rate": round(approval_rate, 2),
            "avg_decision_score": round(avg_decision_score, 2),
            "avg_confidence_score": round(avg_confidence_score, 2),
            "avg_processing_time_ms": round(avg_duration, 2),
            "fraud_risk_distribution": {
                str(level): count for level, count in fraud_stats
            }
        }
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary for today"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_stats = self.get_decision_statistics(from_date=today_start)
        
        # Get pending decisions
        pending = self.db.query(DecisionRequest).filter(
            and_(
                DecisionRequest.tenant_id == self.tenant_id,
                DecisionRequest.status == DecisionStatus.IN_PROGRESS
            )
        ).count()
        
        # Get decisions needing manual review
        needs_review = self.db.query(DecisionRequest).filter(
            and_(
                DecisionRequest.tenant_id == self.tenant_id,
                or_(
                    DecisionRequest.decision_outcome == DecisionOutcome.MANUAL_REVIEW,
                    DecisionRequest.requires_manual_review == True
                )
            )
        ).count()
        
        # Recent decisions
        recent = self.list_decisions(limit=10)
        
        return {
            "today_stats": today_stats,
            "pending_decisions": pending,
            "needs_manual_review": needs_review,
            "recent_decisions": recent
        }
