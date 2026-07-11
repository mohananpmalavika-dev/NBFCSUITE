"""
CRM Initial Data Loader
Loads scoring rules and assignment rules
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.shared.database.connection import AsyncSessionLocal
from backend.shared.database.crm_lead_models import (
    LeadScoringRule, LeadAssignmentRule
)


async def load_initial_data():
    """Load initial scoring and assignment rules"""
    
    print("=" * 60)
    print("CRM Lead Management - Initial Data Loader")
    print("=" * 60)
    
    try:
        async with AsyncSessionLocal() as session:
            
            # ========================================
            # SCORING RULES
            # ========================================
            
            print("\n1. Loading Lead Scoring Rules...")
            
            scoring_rules = [
                # Income-based rules
                {"rule_name": "High Income - Premium", "rule_description": "Monthly income above 1 lakh", "rule_category": "demographics", "field_name": "monthly_income", "operator": "greater_than", "field_value": "100000", "score_points": 20, "priority": 1},
                {"rule_name": "High Income", "rule_description": "Monthly income above 75K", "rule_category": "demographics", "field_name": "monthly_income", "operator": "greater_than", "field_value": "75000", "score_points": 15, "priority": 2},
                {"rule_name": "Medium Income", "rule_description": "Monthly income above 50K", "rule_category": "demographics", "field_name": "monthly_income", "operator": "greater_than", "field_value": "50000", "score_points": 10, "priority": 3},
                {"rule_name": "Basic Income", "rule_description": "Monthly income above 25K", "rule_category": "demographics", "field_name": "monthly_income", "operator": "greater_than", "field_value": "25000", "score_points": 5, "priority": 4},
                
                # Loan amount rules
                {"rule_name": "Large Loan Requirement", "rule_description": "Loan amount above 10 lakhs", "rule_category": "product", "field_name": "loan_amount_required", "operator": "greater_than", "field_value": "1000000", "score_points": 15, "priority": 1},
                {"rule_name": "Medium Loan Requirement", "rule_description": "Loan amount above 5 lakhs", "rule_category": "product", "field_name": "loan_amount_required", "operator": "greater_than", "field_value": "500000", "score_points": 10, "priority": 2},
                {"rule_name": "Small Loan Requirement", "rule_description": "Loan amount above 2 lakhs", "rule_category": "product", "field_name": "loan_amount_required", "operator": "greater_than", "field_value": "200000", "score_points": 5, "priority": 3},
                
                # Occupation rules
                {"rule_name": "Professional - Doctor", "rule_description": "Medical professional", "rule_category": "demographics", "field_name": "occupation", "operator": "contains", "field_value": "doctor", "score_points": 15, "priority": 1},
                {"rule_name": "Professional - Engineer", "rule_description": "Engineering professional", "rule_category": "demographics", "field_name": "occupation", "operator": "contains", "field_value": "engineer", "score_points": 15, "priority": 1},
                {"rule_name": "Professional - Manager", "rule_description": "Management professional", "rule_category": "demographics", "field_name": "occupation", "operator": "contains", "field_value": "manager", "score_points": 15, "priority": 1},
                {"rule_name": "Professional - Director", "rule_description": "Senior management", "rule_category": "demographics", "field_name": "occupation", "operator": "contains", "field_value": "director", "score_points": 15, "priority": 1},
                {"rule_name": "Business Owner", "rule_description": "Self-employed business owner", "rule_category": "demographics", "field_name": "occupation", "operator": "contains", "field_value": "business", "score_points": 10, "priority": 2},
                {"rule_name": "Self-Employed", "rule_description": "Self-employed professional", "rule_category": "demographics", "field_name": "occupation", "operator": "contains", "field_value": "self", "score_points": 10, "priority": 2},
                
                # Completeness rules
                {"rule_name": "Email Provided", "rule_description": "Lead provided email address", "rule_category": "completeness", "field_name": "email", "operator": "is_not_empty", "field_value": None, "score_points": 5, "priority": 1},
                {"rule_name": "Company Details", "rule_description": "Company name provided", "rule_category": "completeness", "field_name": "company_name", "operator": "is_not_empty", "field_value": None, "score_points": 5, "priority": 1},
                {"rule_name": "Location Details", "rule_description": "Pincode provided", "rule_category": "completeness", "field_name": "pincode", "operator": "is_not_empty", "field_value": None, "score_points": 3, "priority": 2},
                
                # Source quality rules
                {"rule_name": "Quality Source - Referral", "rule_description": "Lead from referral source", "rule_category": "source", "field_name": "source", "operator": "equals", "field_value": "referral", "score_points": 10, "priority": 1},
                {"rule_name": "Quality Source - Partner", "rule_description": "Lead from partner", "rule_category": "source", "field_name": "source", "operator": "equals", "field_value": "partner", "score_points": 10, "priority": 1},
                {"rule_name": "Good Source - Website", "rule_description": "Lead from website", "rule_category": "source", "field_name": "source", "operator": "equals", "field_value": "website", "score_points": 5, "priority": 2},
                {"rule_name": "Good Source - Walk-in", "rule_description": "Walk-in lead", "rule_category": "source", "field_name": "source", "operator": "equals", "field_value": "walk_in", "score_points": 5, "priority": 2},
            ]
            
            for rule_data in scoring_rules:
                rule = LeadScoringRule(
                    **rule_data,
                    is_active=True,
                    tenant_id="default"
                )
                session.add(rule)
            
            print(f"✅ Added {len(scoring_rules)} scoring rules")
            
            # ========================================
            # ASSIGNMENT RULES
            # ========================================
            
            print("\n2. Loading Lead Assignment Rules...")
            
            assignment_rules = [
                {
                    "rule_name": "Default Round Robin",
                    "rule_description": "Distribute all new leads equally across active sales team",
                    "priority": 1,
                    "conditions": {},
                    "assignment_type": "round_robin",
                },
                {
                    "rule_name": "High Value Leads - Senior Team",
                    "rule_description": "Assign high-value leads (>10L) to senior sales representatives",
                    "priority": 1,
                    "conditions": {"loan_amount_required__gte": 1000000},
                    "assignment_type": "round_robin",
                },
                {
                    "rule_name": "Hot Leads Priority",
                    "rule_description": "Immediately assign hot leads (score >= 70) to available team",
                    "priority": 1,
                    "conditions": {"lead_score__gte": 70},
                    "assignment_type": "load_balanced",
                },
                {
                    "rule_name": "Load Balanced Distribution",
                    "rule_description": "Balance lead distribution with max 20 leads per user",
                    "priority": 2,
                    "conditions": {},
                    "assignment_type": "load_balanced",
                    "max_leads_per_user": 20,
                },
            ]
            
            for rule_data in assignment_rules:
                rule = LeadAssignmentRule(
                    **rule_data,
                    is_active=True,
                    tenant_id="default"
                )
                session.add(rule)
            
            print(f"✅ Added {len(assignment_rules)} assignment rules")
            
            # Commit all changes
            await session.commit()
            
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Initial data loaded.")
            print("=" * 60)
            print("\nSummary:")
            print(f"  - {len(scoring_rules)} scoring rules")
            print(f"  - {len(assignment_rules)} assignment rules")
            print("\nNext steps:")
            print("1. Restart backend server")
            print("2. Visit http://localhost:8000/docs")
            print("3. Test: POST /api/crm/leads to create a lead")
            print("4. Lead should get auto-scored and auto-assigned!")
            
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\nLoading CRM initial data...")
    success = asyncio.run(load_initial_data())
    sys.exit(0 if success else 1)
