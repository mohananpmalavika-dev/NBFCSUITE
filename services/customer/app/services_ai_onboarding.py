"""
AI-Powered Conversational Customer Onboarding
Reduces manual work through intelligent conversation and document extraction
"""

from typing import Optional, Dict, List, Any
from enum import Enum


class OnboardingConversationState(str, Enum):
    """Conversation flow states"""
    GREETING = "greeting"
    CUSTOMER_SEARCH = "customer_search"
    PROSPECT_CREATE = "prospect_create"
    BASIC_INFO = "basic_info"
    IDENTITY_UPLOAD = "identity_upload"
    ADDRESS = "address"
    EMPLOYMENT = "employment"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"
    REVIEW = "review"
    APPROVAL = "approval"
    COMPLETE = "complete"


class AIOnboardingService:
    """
    AI-powered conversational onboarding
    Instead of long forms: AI asks follow-up questions conversationally
    """

    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.current_state = OnboardingConversationState.GREETING
        self.extracted_data = {}

    def get_initial_greeting(self) -> str:
        """Initial greeting"""
        return """
        👋 Welcome to our Banking Platform!
        
        I'm your AI Onboarding Assistant. I'll help you open an account and get ready 
        to access all our financial products.
        
        To get started, could you please tell me:
        1️⃣ What is your primary product interest? (Savings, Deposits, Gold Loan, Forex, etc.)
        2️⃣ Have you been a customer with us before?
        """

    def search_existing_customer(self, response: str) -> Dict[str, Any]:
        """
        User says: "I want to open a gold loan."
        
        AI:
        - Checks if customer exists
        - Extracts product intent
        - Routes to right flow
        """
        return {
            "state": OnboardingConversationState.CUSTOMER_SEARCH,
            "message": "Let me search our records to see if you're an existing customer...",
            "next_questions": [
                "What's your mobile number? (I'll use this to find your existing account, if any)",
                "Or, do you have your Aadhaar or PAN handy?"
            ],
            "product_intent": "gold_loan"
        }

    def ask_next_question(self, current_stage: str, collected_data: Dict[str, Any]) -> str:
        """
        Smart questioning based on data collected so far
        Only ask what's missing
        """
        responses = {
            OnboardingConversationState.BASIC_INFO: self._ask_basic_info(collected_data),
            OnboardingConversationState.IDENTITY_UPLOAD: self._ask_identity(collected_data),
            OnboardingConversationState.ADDRESS: self._ask_address(collected_data),
            OnboardingConversationState.EMPLOYMENT: self._ask_employment(collected_data),
            OnboardingConversationState.FINANCIAL: self._ask_financial(collected_data),
        }
        return responses.get(current_stage, "What would you like to do next?")

    def _ask_basic_info(self, data: Dict[str, Any]) -> str:
        """Ask for basic details"""
        questions = []

        if "full_name" not in data:
            questions.append("What's your full name? (First and Last name)")
        
        if "dob" not in data:
            questions.append("What's your date of birth? (DD/MM/YYYY)")
        
        if "gender" not in data:
            questions.append("What's your gender? (Male/Female/Other)")
        
        if "occupation" not in data:
            questions.append("What do you do for a living? (e.g., Software Engineer, Business Owner, Homemaker, etc.)")

        return "\n".join([f"{i+1}. {q}" for i, q in questions])

    def _ask_identity(self, data: Dict[str, Any]) -> str:
        """Ask for identity documents"""
        return """
        📋 Let's verify your identity.
        
        Please upload or share one of these:
        - PAN (Permanent Account Number)
        - Aadhaar
        - Passport
        - Driving License
        
        📸 Tip: Take a clear photo of the document. I'll extract all details automatically!
        """

    def _ask_address(self, data: Dict[str, Any]) -> str:
        """Ask for address"""
        return """
        📍 Now, let's confirm your address.
        
        What's your current residential address?
        (You can say it naturally or paste it)
        
        Do you have an address proof document? (Electricity bill, Internet bill, Lease agreement, etc.)
        I can extract the address from it automatically!
        """

    def _ask_employment(self, data: Dict[str, Any]) -> str:
        """Ask for employment details"""
        return """
        💼 Tell me about your employment:
        
        1. Are you:
           - Employed (Full-time/Part-time)
           - Self-employed / Business Owner
           - Retired
           - Student
           - Housewife/Homemaker
           - Other
        
        2. If employed:
           - Company name?
           - Your designation?
           - How long have you been there?
        
        3. Your approximate monthly income?
        """

    def _ask_financial(self, data: Dict[str, Any]) -> str:
        """Ask for financial details"""
        return """
        💰 Let's understand your financial profile:
        
        1. Approximate annual income?
        2. Monthly expenses? (rough estimate)
        3. Do you have savings? (Yes/No)
        4. Any existing loans or credit cards? (Tell me briefly)
        5. Do you have investments? (Stocks, Mutual Funds, etc.)
        
        Don't worry if you don't remember exact numbers - estimates are fine!
        """

    def extract_and_validate(self, user_input: str, current_field: str) -> Dict[str, Any]:
        """
        Extract structured data from natural language
        Example:
        User says: "I'm a software engineer at TCS, been there 5 years, earning 80k per month"
        AI extracts: {
            "occupation": "software engineer",
            "employer": "TCS",
            "experience_years": 5,
            "monthly_salary": 80000
        }
        """
        return {
            "extracted": True,
            "field": current_field,
            "confidence": 0.95,
            "extracted_data": self._parse_natural_language(user_input, current_field),
            "missing_fields": self._identify_missing_fields(user_input, current_field)
        }

    def _parse_natural_language(self, text: str, field: str) -> Dict[str, Any]:
        """Parse natural language to structured data"""
        # TODO: Use NLP/LLM to parse
        return {}

    def _identify_missing_fields(self, text: str, field: str) -> List[str]:
        """Identify what data is still missing"""
        # TODO: Use NLP to identify gaps
        return []

    def document_extraction(self, document_type: str, file_path: str) -> Dict[str, Any]:
        """
        User uploads a document
        AI extracts relevant fields
        No manual typing required!
        """
        return {
            "document_type": document_type,
            "extraction_status": "processing",
            "message": f"Reading your {document_type}... extracting details automatically",
            "extracted_fields": {
                # These would come from OCR/Document AI service
                "name": "John Doe",
                "document_number": "XXXXXX",
                "expiry_date": "2030-01-01",
                "confidence_score": 0.98
            },
            "next_step": "Please verify the extracted information above"
        }

    def validate_completeness(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate if all required information is collected
        Return what's missing
        """
        required_fields = {
            "personal": ["full_name", "dob", "gender", "occupation"],
            "identity": ["pan", "aadhar"],  # At least one
            "address": ["residential_address", "address_proof"],
            "employment": ["employment_type", "employer", "salary"],
            "financial": ["annual_income", "monthly_expenses"],
            "compliance": ["pan_verified", "aadhar_verified", "aml_checked"]
        }

        missing = {}
        for category, fields in required_fields.items():
            missing[category] = [f for f in fields if f not in customer_data]

        completion_percentage = (
            (len(customer_data) / sum(len(v) for v in required_fields.values())) * 100
        )

        return {
            "is_complete": sum(len(v) for v in missing.values()) == 0,
            "completion_percentage": min(100, int(completion_percentage)),
            "missing_fields": missing,
            "message": self._generate_completion_message(missing, completion_percentage)
        }

    def _generate_completion_message(self, missing: Dict[str, List[str]], 
                                     completion_pct: float) -> str:
        """Generate user-friendly completion message"""
        if completion_pct == 100:
            return """
            ✅ Excellent! Your profile is complete!
            
            Next steps:
            1. Review your information
            2. Approve submission
            3. We'll process your application
            4. Get your CIF (Customer ID)
            """
        else:
            return f"""
            📊 You're {completion_pct:.0f}% through the process!
            
            Still need:
            {chr(10).join(f"- {cat}: {', '.join(fields)}" for cat, fields in missing.items() if fields)}
            
            Let's continue! 👇
            """

    def detect_missing_info(self) -> Dict[str, Any]:
        """
        Employee only reviews exceptions
        AI finds and flags missing info
        """
        return {
            "missing_documents": [
                "Address Proof",
                "Income Verification (Salary Slip)"
            ],
            "incomplete_sections": [
                "Family Details",
                "Business Profile (if applicable)"
            ],
            "compliance_pending": [
                "Video KYC",
                "Address Verification"
            ],
            "action_required": "Please upload the missing documents to proceed"
        }

    def prepare_for_approval(self, customer_id: str) -> Dict[str, Any]:
        """
        Prepare customer for approval workflow
        Generate summary for checker/manager
        """
        return {
            "customer_id": customer_id,
            "summary": {
                "profile_completeness": 100,
                "compliance_status": "all_checks_passed",
                "risk_assessment": "medium",
                "financial_health": "good",
                "behavior_score": 85
            },
            "ready_for_approval": True,
            "routing": {
                "workflow": "standard_approval",
                "levels": ["checker", "manager", "compliance", "final_approver"],
                "estimated_time": "24-48 hours"
            },
            "message": "✅ Ready for approval workflow!"
        }

    def get_conversation_summary(self, conversation: List[Dict[str, str]]) -> str:
        """
        Generate conversation summary for employee review
        Shows what AI extracted, what needs clarification
        """
        return """
        📝 ONBOARDING CONVERSATION SUMMARY
        
        Customer: John Doe (New)
        Mobile: +91-XXXX-XXXX-XXXX
        Product Interest: Gold Loan
        
        ✅ Completed Sections:
        - Personal Details (100%)
        - Identity Documents (100% - PAN & Aadhaar verified)
        - Address (100%)
        - Employment (95%)
        - Financial Profile (90%)
        - Compliance (All checks passed)
        
        ⚠️ Needs Review:
        - Income verification document pending (Salary slip not uploaded yet)
        - Family details incomplete
        
        🤖 AI Confidence:
        - Data extraction: 98%
        - Risk assessment: 85%
        
        ⏭️ Next Step: Checker review for final approval
        """


class ConversationalUIFlow:
    """
    Example conversational flow
    Shows how the AI would interact with the user
    """

    @staticmethod
    def example_flow():
        """
        Example of a complete onboarding conversation
        """
        return """
        ============================================================================
        CONVERSATIONAL CUSTOMER ONBOARDING FLOW - EXAMPLE
        ============================================================================
        
        🤖 AI: "Welcome! I'm your onboarding assistant. What brings you here today?"
        👤 User: "I want to open a gold loan account"
        
        🤖 AI: "Great! Gold loans are perfect for flexible financing. 
                Let me check if you're already a customer with us...
                What's your mobile number?"
        👤 User: "+91-9876543210"
        
        🤖 AI: "Thanks! I found no existing account on this number.
                I'll create a new profile for you.
                
                First, tell me about yourself:
                What's your full name?"
        👤 User: "John Doe"
        
        🤖 AI: "Nice to meet you, John! 
                Your date of birth? (DD/MM/YYYY)"
        👤 User: "15/05/1985"
        
        🤖 AI: "Great! Now, to verify your identity, 
                could you upload a copy of your PAN or Aadhaar?
                📸 You can just take a photo - I'll extract everything"
        👤 User: [Uploads PAN image]
        
        🤖 AI: "✅ Perfect! I extracted:
                Name: John Doe
                PAN: XXXXX1234K
                DOB: 15/05/1985
                
                Does this look correct? (Yes/No)"
        👤 User: "Yes, looks good"
        
        🤖 AI: "Excellent! Now, what's your current address?
                Do you have a recent utility bill or lease agreement?"
        👤 User: "I live at Flat 5, Green Valley Apartments, Delhi.
                  I have my internet bill"
        
        🤖 AI: "Could you share that bill? I can read the address from it"
        👤 User: [Uploads utility bill]
        
        🤖 AI: "✅ Address extracted and verified!
                
                Now, tell me about your work:
                What's your occupation?"
        👤 User: "I'm a software engineer at TCS"
        
        🤖 AI: "Excellent! How long have you been at TCS?
                And roughly, what's your monthly take-home?"
        👤 User: "6 years, about 85k per month"
        
        🤖 AI: "Great income! Do you have a recent salary slip?
                I can quickly verify your employment"
        👤 User: [Uploads salary slip]
        
        🤖 AI: "✅ Income verified!
                
                Let me ask a few financial questions:
                - Do you have any existing loans? (Car, Home, Personal)
                - Do you invest in stocks or mutual funds?
                - Any credit cards?"
        👤 User: "One car loan with HDFC for 5 lakh, 
                  50k in mutual funds"
        
        🤖 AI: "Perfect! 📊 Here's what I've learned about you:
                
                ✅ PROFILE COMPLETENESS: 95%
                ✅ COMPLIANCE: All checks passed
                ✅ RISK ASSESSMENT: Low-Medium
                
                Missing: Just your family details.
                Spouse? Kids? Any dependents?"
        👤 User: "Yes, married with 2 kids"
        
        🤖 AI: "Got it! 
                
                ✅ YOUR PROFILE IS NOW 100% COMPLETE!
                
                📋 VERIFICATION SUMMARY:
                - Personal Details: ✅
                - Identity (PAN): ✅
                - Address: ✅
                - Employment: ✅
                - Income: ✅
                - Compliance Checks: ✅ (AML, PEP, Sanction list - All PASSED)
                
                🎯 READY FOR APPROVAL!
                
                Your application will now go through a quick review.
                You'll get your CIF (Customer ID) within 24 hours.
                
                Thank you, John! 🙌"
        
        ============================================================================
        EMPLOYEE WORKFLOW (Checker):
        ============================================================================
        
        ✅ Application auto-routed as STANDARD APPROVAL
        ✅ All documents present
        ✅ All compliance passed
        ✅ Risk score: 65/100 (Good)
        ✅ Income verification: Confirmed
        
        👤 Checker's review: 15 seconds
        ✓ Approve ✓ Ask for clarification ✗ Reject
        
        Recommendation: APPROVE
        
        Result: CIF Generated: CIF0000001245
        Customer John Doe is now ready for any product!
        """
