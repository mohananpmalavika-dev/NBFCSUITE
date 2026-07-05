"""
Credit Scoring Service
Automated credit assessment for loan applications
"""

from sqlalchemy.orm import Session
from typing import Dict, Tuple, Optional
from decimal import Decimal
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from backend.shared.database.loan_models import LoanApplication, LoanProduct
from backend.shared.database.customer_models import Customer
from .schemas import RiskRating


class CreditScoringService:
    """Service for credit scoring and risk assessment"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    def calculate_credit_score(
        self,
        application: LoanApplication,
        customer: Customer,
        product: LoanProduct
    ) -> Tuple[int, RiskRating, Dict[str, any]]:
        """
        Calculate comprehensive credit score (0-100) and risk rating
        
        Returns:
            - credit_score (0-100)
            - risk_rating (low, medium, high, very_high)
            - breakdown (detailed scoring breakdown)
        """
        
        breakdown = {}
        
        # 1. CIBIL Score Factor (40% weight)
        cibil_score, cibil_points = self._calculate_cibil_factor(
            customer.cibil_score
        )
        breakdown['cibil'] = {
            'score': customer.cibil_score,
            'points': cibil_points,
            'weight': 40,
            'weighted_score': cibil_score
        }
        
        # 2. Income Factor (25% weight)
        income_score, income_points = self._calculate_income_factor(
            monthly_income=customer.monthly_income or Decimal("0"),
            loan_amount=application.requested_amount,
            emi_amount=application.emi_amount or Decimal("0")
        )
        breakdown['income'] = {
            'monthly_income': float(customer.monthly_income or 0),
            'loan_amount': float(application.requested_amount),
            'emi_amount': float(application.emi_amount or 0),
            'points': income_points,
            'weight': 25,
            'weighted_score': income_score
        }
        
        # 3. Debt-to-Income Ratio (20% weight)
        dti_score, dti_ratio, dti_points = self._calculate_dti_factor(
            monthly_income=customer.monthly_income or Decimal("0"),
            emi_amount=application.emi_amount or Decimal("0"),
            existing_obligations=Decimal("0")  # TODO: Calculate from existing loans
        )
        breakdown['debt_to_income'] = {
            'ratio': float(dti_ratio),
            'points': dti_points,
            'weight': 20,
            'weighted_score': dti_score
        }
        
        # 4. Employment Stability (10% weight)
        employment_score, employment_points = self._calculate_employment_factor(
            employment_type=customer.employment_type,
            years_in_business=customer.years_in_business
        )
        breakdown['employment'] = {
            'type': customer.employment_type,
            'years': customer.years_in_business,
            'points': employment_points,
            'weight': 10,
            'weighted_score': employment_score
        }
        
        # 5. Age Factor (5% weight)
        age_score, age_points = self._calculate_age_factor(customer.age or 0)
        breakdown['age'] = {
            'age': customer.age,
            'points': age_points,
            'weight': 5,
            'weighted_score': age_score
        }
        
        # Calculate total score
        total_score = (
            cibil_score +
            income_score +
            dti_score +
            employment_score +
            age_score
        )
        
        # Determine risk rating
        risk_rating = self._determine_risk_rating(total_score)
        
        breakdown['total'] = {
            'score': round(total_score, 2),
            'risk_rating': risk_rating.value,
            'recommendation': self._get_recommendation(total_score, risk_rating)
        }
        
        return round(total_score, 2), risk_rating, breakdown
    
    def _calculate_cibil_factor(self, cibil_score: Optional[int]) -> Tuple[float, int]:
        """
        Calculate CIBIL score factor (40% weight)
        
        Scoring:
        - 750+: Excellent (100 points)
        - 700-749: Good (80 points)
        - 650-699: Fair (60 points)
        - 600-649: Poor (40 points)
        - <600: Very Poor (20 points)
        """
        if not cibil_score or cibil_score < 300:
            points = 0
        elif cibil_score >= 750:
            points = 100
        elif cibil_score >= 700:
            points = 80
        elif cibil_score >= 650:
            points = 60
        elif cibil_score >= 600:
            points = 40
        else:
            points = 20
        
        weighted_score = (points * 40) / 100
        return weighted_score, points
    
    def _calculate_income_factor(
        self,
        monthly_income: Decimal,
        loan_amount: Decimal,
        emi_amount: Decimal
    ) -> Tuple[float, int]:
        """
        Calculate income factor (25% weight)
        
        Considers:
        - EMI to income ratio (should be < 50%)
        - Loan amount to annual income ratio
        """
        if monthly_income <= 0:
            return 0.0, 0
        
        # EMI to income ratio
        emi_to_income = (float(emi_amount) / float(monthly_income)) * 100
        
        # Annual income
        annual_income = float(monthly_income) * 12
        
        # Loan to annual income ratio
        loan_to_income_ratio = float(loan_amount) / annual_income if annual_income > 0 else 999
        
        # Score based on EMI to income ratio
        if emi_to_income <= 30:
            points = 100  # Excellent
        elif emi_to_income <= 40:
            points = 80  # Good
        elif emi_to_income <= 50:
            points = 60  # Fair
        elif emi_to_income <= 60:
            points = 40  # Marginal
        else:
            points = 20  # Poor
        
        # Adjust for loan to income ratio
        if loan_to_income_ratio > 5:
            points = max(20, points - 20)  # Penalty for high loan amount
        
        weighted_score = (points * 25) / 100
        return weighted_score, points
    
    def _calculate_dti_factor(
        self,
        monthly_income: Decimal,
        emi_amount: Decimal,
        existing_obligations: Decimal
    ) -> Tuple[float, float, int]:
        """
        Calculate debt-to-income ratio factor (20% weight)
        
        DTI = (Total Monthly Obligations / Monthly Income) * 100
        """
        if monthly_income <= 0:
            return 0.0, 0.0, 0
        
        total_obligations = float(emi_amount) + float(existing_obligations)
        dti_ratio = (total_obligations / float(monthly_income)) * 100
        
        # Score based on DTI
        if dti_ratio <= 30:
            points = 100  # Excellent
        elif dti_ratio <= 40:
            points = 80  # Good
        elif dti_ratio <= 50:
            points = 60  # Fair
        elif dti_ratio <= 60:
            points = 40  # Marginal
        else:
            points = 20  # Poor
        
        weighted_score = (points * 20) / 100
        return weighted_score, dti_ratio, points
    
    def _calculate_employment_factor(
        self,
        employment_type: Optional[str],
        years_in_business: Optional[int]
    ) -> Tuple[float, int]:
        """
        Calculate employment stability factor (10% weight)
        
        Considers:
        - Employment type (Salaried > Self-Employed > Business)
        - Years of stability
        """
        points = 50  # Base points
        
        # Type bonus
        if employment_type:
            if employment_type.lower() in ['permanent', 'salaried']:
                points += 30
            elif employment_type.lower() in ['self_employed', 'professional']:
                points += 20
            elif employment_type.lower() in ['contract', 'business']:
                points += 10
        
        # Stability bonus
        if years_in_business:
            if years_in_business >= 10:
                points += 20
            elif years_in_business >= 5:
                points += 15
            elif years_in_business >= 3:
                points += 10
            elif years_in_business >= 1:
                points += 5
        
        points = min(100, points)  # Cap at 100
        
        weighted_score = (points * 10) / 100
        return weighted_score, points
    
    def _calculate_age_factor(self, age: int) -> Tuple[float, int]:
        """
        Calculate age factor (5% weight)
        
        Optimal age range: 25-55 years
        """
        if age == 0:
            return 0.0, 0
        
        if 25 <= age <= 55:
            points = 100  # Optimal age range
        elif (21 <= age < 25) or (55 < age <= 65):
            points = 70  # Acceptable
        elif (18 <= age < 21) or (65 < age <= 70):
            points = 40  # Risky
        else:
            points = 20  # Very risky
        
        weighted_score = (points * 5) / 100
        return weighted_score, points
    
    def _determine_risk_rating(self, credit_score: float) -> RiskRating:
        """Determine risk rating based on credit score"""
        if credit_score >= 75:
            return RiskRating.LOW
        elif credit_score >= 50:
            return RiskRating.MEDIUM
        elif credit_score >= 25:
            return RiskRating.HIGH
        else:
            return RiskRating.VERY_HIGH
    
    def _get_recommendation(
        self,
        credit_score: float,
        risk_rating: RiskRating
    ) -> str:
        """Get recommendation based on score and rating"""
        if risk_rating == RiskRating.LOW:
            return "Recommended for approval. Low risk borrower with strong credit profile."
        elif risk_rating == RiskRating.MEDIUM:
            return "Conditionally recommended. Moderate risk with acceptable credit profile."
        elif risk_rating == RiskRating.HIGH:
            return "Requires careful review. Higher risk profile, consider additional security."
        else:
            return "Not recommended. Very high risk profile. Approval requires senior management."
    
    def assess_application(
        self,
        application_id: int
    ) -> Dict[str, any]:
        """
        Perform complete credit assessment for application
        
        Updates application with:
        - Credit score
        - Risk rating
        - Debt-to-income ratio
        - Assessment breakdown
        """
        # Get application with related data
        application = self.db.query(LoanApplication).filter(
            LoanApplication.id == application_id,
            LoanApplication.tenant_id == self.tenant_id
        ).first()
        
        if not application:
            raise ValueError("Application not found")
        
        # Get customer
        customer = self.db.query(Customer).filter(
            Customer.id == application.customer_id
        ).first()
        
        if not customer:
            raise ValueError("Customer not found")
        
        # Get product
        product = self.db.query(LoanProduct).filter(
            LoanProduct.id == application.loan_product_id
        ).first()
        
        if not product:
            raise ValueError("Product not found")
        
        # Calculate credit score
        credit_score, risk_rating, breakdown = self.calculate_credit_score(
            application, customer, product
        )
        
        # Update application
        application.credit_score = int(credit_score)
        application.risk_rating = risk_rating.value
        application.monthly_income = customer.monthly_income
        
        # Calculate and update DTI
        if breakdown.get('debt_to_income'):
            dti = breakdown['debt_to_income']['ratio']
            application.debt_to_income_ratio = Decimal(str(round(dti, 2)))
        
        # Update status if submitted
        if application.status == 'submitted':
            application.status = 'credit_assessment'
            application.sub_status = 'auto_assessment_complete'
        
        application.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(application)
        
        return {
            'application_id': application.id,
            'application_number': application.application_number,
            'credit_score': credit_score,
            'risk_rating': risk_rating.value,
            'breakdown': breakdown,
            'recommendation': breakdown['total']['recommendation'],
            'status_updated': True
        }
    
    def bulk_assess_pending_applications(self) -> Dict[str, any]:
        """
        Assess all pending applications that need credit scoring
        
        Returns summary of assessments
        """
        # Get pending applications
        pending_apps = self.db.query(LoanApplication).filter(
            LoanApplication.tenant_id == self.tenant_id,
            LoanApplication.status.in_(['submitted', 'under_review']),
            LoanApplication.credit_score.is_(None),
            LoanApplication.is_deleted == False
        ).all()
        
        results = {
            'total_assessed': 0,
            'by_risk_rating': {
                'low': 0,
                'medium': 0,
                'high': 0,
                'very_high': 0
            },
            'errors': []
        }
        
        for app in pending_apps:
            try:
                assessment = self.assess_application(app.id)
                results['total_assessed'] += 1
                risk_rating = assessment['risk_rating']
                results['by_risk_rating'][risk_rating] += 1
            except Exception as e:
                results['errors'].append({
                    'application_id': app.id,
                    'application_number': app.application_number,
                    'error': str(e)
                })
        
        return results
