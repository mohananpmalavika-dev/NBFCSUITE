"""
Pre-built Workflow Templates

Common workflow patterns for NBFC operations:
- Loan Approval Workflow
- Deposit Account Approval
- Customer KYC Verification
- Document Review Workflow
- Sequential Approval Chain
- Parallel Review Process
"""

from typing import Dict, Any, List


class WorkflowTemplates:
    """Pre-built workflow template library"""
    
    @staticmethod
    def get_loan_approval_workflow() -> Dict[str, Any]:
        """
        Loan Approval Workflow
        
        Flow:
        Start → Credit Check → Risk Assessment → Gateway (Amount) 
        → High Amount: Manager Approval → Committee Approval
        → Low Amount: Officer Approval
        → End
        """
        return {
            "workflow_id": "loan_approval_workflow",
            "workflow_name": "Loan Approval Workflow",
            "workflow_description": "Multi-level loan approval with credit check and risk assessment",
            "category": "lending",
            "process": {
                "id": "loan_approval_process",
                "name": "Loan Approval Process",
                "version": "1.0",
                "is_executable": True,
                "process_type": "None",
                
                # Start Event
                "start_events": [{
                    "id": "start_loan",
                    "name": "Start Loan Approval",
                    "type": "start_none",
                    "event_type": "none",
                    "position": {"x": 100, "y": 200}
                }],
                
                # Service Tasks
                "service_tasks": [
                    {
                        "id": "credit_check",
                        "name": "Credit Bureau Check",
                        "type": "service_task",
                        "description": "Fetch credit report from bureau",
                        "position": {"x": 250, "y": 200},
                        "config": {
                            "implementation": "api",
                            "api_endpoint": "/api/integration/bureau/pull-report",
                            "api_method": "POST",
                            "result_variable": "credit_report",
                            "retry_enabled": True,
                            "max_retries": 3
                        }
                    },
                    {
                        "id": "risk_assessment",
                        "name": "Risk Assessment",
                        "type": "service_task",
                        "description": "Calculate risk score",
                        "position": {"x": 400, "y": 200},
                        "config": {
                            "implementation": "api",
                            "api_endpoint": "/api/risk/calculate-score",
                            "api_method": "POST",
                            "result_variable": "risk_score",
                            "retry_enabled": False
                        }
                    }
                ],
                
                # User Tasks
                "user_tasks": [
                    {
                        "id": "officer_approval",
                        "name": "Loan Officer Approval",
                        "type": "user_task",
                        "description": "Review and approve loan application",
                        "position": {"x": 700, "y": 100},
                        "config": {
                            "assignment_type": "role",
                            "assigned_role": "loan_officer",
                            "priority": "normal",
                            "due_date": "+2d",
                            "form_fields": [
                                {"name": "approved", "type": "boolean", "label": "Approve Loan?"},
                                {"name": "comments", "type": "text", "label": "Comments"}
                            ]
                        }
                    },
                    {
                        "id": "manager_approval",
                        "name": "Manager Approval",
                        "type": "user_task",
                        "description": "Manager review for high-value loans",
                        "position": {"x": 700, "y": 300},
                        "config": {
                            "assignment_type": "role",
                            "assigned_role": "branch_manager",
                            "priority": "high",
                            "due_date": "+1d",
                            "form_fields": [
                                {"name": "approved", "type": "boolean", "label": "Approve Loan?"},
                                {"name": "comments", "type": "text", "label": "Comments"}
                            ]
                        }
                    },
                    {
                        "id": "committee_approval",
                        "name": "Credit Committee Approval",
                        "type": "user_task",
                        "description": "Final committee review",
                        "position": {"x": 850, "y": 300},
                        "config": {
                            "assignment_type": "role",
                            "assigned_role": "credit_committee",
                            "priority": "urgent",
                            "due_date": "+3d",
                            "form_fields": [
                                {"name": "approved", "type": "boolean", "label": "Approve Loan?"},
                                {"name": "conditions", "type": "text", "label": "Conditions"}
                            ]
                        }
                    }
                ],
                
                # Gateways
                "gateways": [
                    {
                        "id": "amount_gateway",
                        "name": "Check Loan Amount",
                        "type": "exclusive_gateway",
                        "gateway_type": "exclusive",
                        "description": "Route based on loan amount",
                        "position": {"x": 550, "y": 200}
                    },
                    {
                        "id": "merge_gateway",
                        "name": "Merge Approvals",
                        "type": "exclusive_gateway",
                        "gateway_type": "exclusive",
                        "description": "Merge approval paths",
                        "position": {"x": 1000, "y": 200}
                    }
                ],
                
                # End Events
                "end_events": [{
                    "id": "end_loan",
                    "name": "Loan Approved/Rejected",
                    "type": "end_none",
                    "event_type": "none",
                    "position": {"x": 1150, "y": 200}
                }],
                
                # Sequence Flows
                "sequence_flows": [
                    {
                        "id": "flow_start_credit",
                        "source_ref": "start_loan",
                        "target_ref": "credit_check"
                    },
                    {
                        "id": "flow_credit_risk",
                        "source_ref": "credit_check",
                        "target_ref": "risk_assessment"
                    },
                    {
                        "id": "flow_risk_gateway",
                        "source_ref": "risk_assessment",
                        "target_ref": "amount_gateway"
                    },
                    {
                        "id": "flow_low_amount",
                        "name": "Amount < 500000",
                        "source_ref": "amount_gateway",
                        "target_ref": "officer_approval",
                        "condition": {
                            "type": "simple",
                            "variable": "loan_amount",
                            "operator": "<",
                            "value": 500000
                        }
                    },
                    {
                        "id": "flow_high_amount",
                        "name": "Amount >= 500000",
                        "source_ref": "amount_gateway",
                        "target_ref": "manager_approval",
                        "condition": {
                            "type": "simple",
                            "variable": "loan_amount",
                            "operator": ">=",
                            "value": 500000
                        }
                    },
                    {
                        "id": "flow_manager_committee",
                        "source_ref": "manager_approval",
                        "target_ref": "committee_approval"
                    },
                    {
                        "id": "flow_officer_merge",
                        "source_ref": "officer_approval",
                        "target_ref": "merge_gateway"
                    },
                    {
                        "id": "flow_committee_merge",
                        "source_ref": "committee_approval",
                        "target_ref": "merge_gateway"
                    },
                    {
                        "id": "flow_merge_end",
                        "source_ref": "merge_gateway",
                        "target_ref": "end_loan"
                    }
                ],
                
                "intermediate_events": [],
                "script_tasks": [],
                "send_tasks": [],
                "variables": {
                    "loan_amount": 0,
                    "credit_report": None,
                    "risk_score": 0,
                    "approval_status": "pending"
                }
            }
        }
    
    @staticmethod
    def get_kyc_verification_workflow() -> Dict[str, Any]:
        """
        KYC Verification Workflow
        
        Flow:
        Start → Document Collection → Parallel (Identity Check, Address Check, Photo Check)
        → Compliance Review → End
        """
        return {
            "workflow_id": "kyc_verification_workflow",
            "workflow_name": "KYC Verification Workflow",
            "workflow_description": "Customer KYC document verification with parallel checks",
            "category": "compliance",
            "process": {
                "id": "kyc_verification_process",
                "name": "KYC Verification Process",
                "version": "1.0",
                "is_executable": True,
                
                "start_events": [{
                    "id": "start_kyc",
                    "name": "Start KYC",
                    "type": "start_none",
                    "event_type": "none",
                    "position": {"x": 100, "y": 300}
                }],
                
                "user_tasks": [
                    {
                        "id": "doc_collection",
                        "name": "Document Collection",
                        "type": "user_task",
                        "description": "Collect KYC documents from customer",
                        "position": {"x": 250, "y": 300},
                        "config": {
                            "assignment_type": "role",
                            "assigned_role": "kyc_officer",
                            "priority": "normal",
                            "due_date": "+1d"
                        }
                    },
                    {
                        "id": "identity_check",
                        "name": "Identity Verification",
                        "type": "user_task",
                        "position": {"x": 550, "y": 150},
                        "config": {
                            "assignment_type": "role",
                            "assigned_role": "kyc_verifier",
                            "priority": "high"
                        }
                    },
                    {
                        "id": "address_check",
                        "name": "Address Verification",
                        "type": "user_task",
                        "position": {"x": 550, "y": 300},
                        "config": {
                            "assignment_type": "role",
                            "assigned_role": "kyc_verifier",
                            "priority": "high"
                        }
                    },
                    {
                        "id": "photo_check",
                        "name": "Photo Verification",
                        "type": "user_task",
                        "position": {"x": 550, "y": 450},
                        "config": {
                            "assignment_type": "role",
                            "assigned_role": "kyc_verifier",
                            "priority": "high"
                        }
                    },
                    {
                        "id": "compliance_review",
                        "name": "Compliance Review",
                        "type": "user_task",
                        "description": "Final compliance check",
                        "position": {"x": 850, "y": 300},
                        "config": {
                            "assignment_type": "role",
                            "assigned_role": "compliance_officer",
                            "priority": "urgent",
                            "due_date": "+2d"
                        }
                    }
                ],
                
                "gateways": [
                    {
                        "id": "parallel_split",
                        "name": "Split Verification",
                        "type": "parallel_gateway",
                        "gateway_type": "parallel",
                        "position": {"x": 400, "y": 300}
                    },
                    {
                        "id": "parallel_join",
                        "name": "Join Verification",
                        "type": "parallel_gateway",
                        "gateway_type": "parallel",
                        "position": {"x": 700, "y": 300}
                    }
                ],
                
                "end_events": [{
                    "id": "end_kyc",
                    "name": "KYC Complete",
                    "type": "end_none",
                    "event_type": "none",
                    "position": {"x": 1000, "y": 300}
                }],
                
                "sequence_flows": [
                    {
                        "id": "flow_start_doc",
                        "source_ref": "start_kyc",
                        "target_ref": "doc_collection"
                    },
                    {
                        "id": "flow_doc_split",
                        "source_ref": "doc_collection",
                        "target_ref": "parallel_split"
                    },
                    {
                        "id": "flow_split_identity",
                        "source_ref": "parallel_split",
                        "target_ref": "identity_check"
                    },
                    {
                        "id": "flow_split_address",
                        "source_ref": "parallel_split",
                        "target_ref": "address_check"
                    },
                    {
                        "id": "flow_split_photo",
                        "source_ref": "parallel_split",
                        "target_ref": "photo_check"
                    },
                    {
                        "id": "flow_identity_join",
                        "source_ref": "identity_check",
                        "target_ref": "parallel_join"
                    },
                    {
                        "id": "flow_address_join",
                        "source_ref": "address_check",
                        "target_ref": "parallel_join"
                    },
                    {
                        "id": "flow_photo_join",
                        "source_ref": "photo_check",
                        "target_ref": "parallel_join"
                    },
                    {
                        "id": "flow_join_compliance",
                        "source_ref": "parallel_join",
                        "target_ref": "compliance_review"
                    },
                    {
                        "id": "flow_compliance_end",
                        "source_ref": "compliance_review",
                        "target_ref": "end_kyc"
                    }
                ],
                
                "service_tasks": [],
                "script_tasks": [],
                "send_tasks": [],
                "intermediate_events": [],
                "variables": {
                    "customer_id": 0,
                    "documents_verified": False,
                    "kyc_status": "pending"
                }
            }
        }
    
    @staticmethod
    def get_deposit_approval_workflow() -> Dict[str, Any]:
        """
        Deposit Account Approval Workflow
        
        Simple sequential approval workflow
        """
        return {
            "workflow_id": "deposit_approval_workflow",
            "workflow_name": "Deposit Account Approval",
            "workflow_description": "Sequential approval for new deposit accounts",
            "category": "deposits",
            "process": {
                "id": "deposit_approval_process",
                "name": "Deposit Approval Process",
                "version": "1.0",
                "is_executable": True,
                
                "start_events": [{
                    "id": "start_deposit",
                    "name": "Start",
                    "type": "start_none",
                    "event_type": "none",
                    "position": {"x": 100, "y": 200}
                }],
                
                "user_tasks": [
                    {
                        "id": "ops_review",
                        "name": "Operations Review",
                        "type": "user_task",
                        "description": "Review account details",
                        "position": {"x": 250, "y": 200},
                        "config": {
                            "assignment_type": "role",
                            "assigned_role": "operations_officer",
                            "priority": "normal",
                            "due_date": "+1d"
                        }
                    },
                    {
                        "id": "manager_approval",
                        "name": "Manager Approval",
                        "type": "user_task",
                        "description": "Manager final approval",
                        "position": {"x": 400, "y": 200},
                        "config": {
                            "assignment_type": "role",
                            "assigned_role": "branch_manager",
                            "priority": "normal",
                            "due_date": "+1d"
                        }
                    }
                ],
                
                "send_tasks": [{
                    "id": "send_notification",
                    "name": "Send Approval Email",
                    "type": "send_task",
                    "description": "Notify customer of approval",
                    "position": {"x": 550, "y": 200},
                    "config": {
                        "send_type": "email",
                        "to": "${customer_email}",
                        "subject": "Deposit Account Approved",
                        "template": "deposit_approval_email"
                    }
                }],
                
                "end_events": [{
                    "id": "end_deposit",
                    "name": "Complete",
                    "type": "end_none",
                    "event_type": "none",
                    "position": {"x": 700, "y": 200}
                }],
                
                "sequence_flows": [
                    {
                        "id": "flow_start_ops",
                        "source_ref": "start_deposit",
                        "target_ref": "ops_review"
                    },
                    {
                        "id": "flow_ops_manager",
                        "source_ref": "ops_review",
                        "target_ref": "manager_approval"
                    },
                    {
                        "id": "flow_manager_notify",
                        "source_ref": "manager_approval",
                        "target_ref": "send_notification"
                    },
                    {
                        "id": "flow_notify_end",
                        "source_ref": "send_notification",
                        "target_ref": "end_deposit"
                    }
                ],
                
                "gateways": [],
                "service_tasks": [],
                "script_tasks": [],
                "intermediate_events": [],
                "variables": {
                    "account_id": 0,
                    "customer_email": "",
                    "approval_status": "pending"
                }
            }
        }
    
    @staticmethod
    def get_all_templates() -> List[Dict[str, Any]]:
        """Get all available workflow templates"""
        return [
            WorkflowTemplates.get_loan_approval_workflow(),
            WorkflowTemplates.get_kyc_verification_workflow(),
            WorkflowTemplates.get_deposit_approval_workflow()
        ]
    
    @staticmethod
    def get_template_by_id(template_id: str) -> Dict[str, Any]:
        """Get specific template by ID"""
        templates = {
            "loan_approval_workflow": WorkflowTemplates.get_loan_approval_workflow(),
            "kyc_verification_workflow": WorkflowTemplates.get_kyc_verification_workflow(),
            "deposit_approval_workflow": WorkflowTemplates.get_deposit_approval_workflow()
        }
        return templates.get(template_id)
