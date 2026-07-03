"""Gold service models"""
from .product import (
    GoldProduct,
    GoldProductInterest,
    GoldProductTenure,
    GoldProductLimits,
    GoldProductCharge,
    GoldProductDocument,
    GoldProductEligibility,
    GoldProductWorkflow,
    GoldProductChannel,
    GoldProductTax
)
from .journey import (
    GoldCustomerSession,
    GoldCustomerSearchLog,
    GoldProductSelection,
    GoldEligibilityCheck,
    GoldKYCVerification,
    GoldJourneyStep,
    GoldCustomerInteraction
)
from .appraisal import (
    GoldOrnamentType,
    GoldMarketRate,
    GoldAppraisalSession,
    GoldOrnament,
    GoldPurityTest,
    GoldWeightVerification,
    GoldAppraisalAnomaly,
    GoldAppraisalPhoto
)
from .catalog import (
    GoldOrnamentPhoto,
    GoldOrnamentStone,
    GoldOrnamentStatusHistory,
    GoldOrnamentMovement,
    GoldOrnamentCondition,
    GoldOrnamentTag,
    GoldOrnamentComparison,
    GoldOrnamentCertificate,
    GoldOrnamentInsurance,
    GoldOrnamentGroup,
    GoldOrnamentGroupMember
)
from .vault import (
    GoldVault,
    GoldVaultRack,
    GoldVaultLocker,
    GoldVaultTray,
    GoldPacket,
    GoldPacketOrnament,
    GoldPacketMovement,
    GoldVaultAudit,
    GoldAuditFinding,
    GoldVaultAccessLog,
    GoldSecuritySeal
)
from .loan import (
    LoanApplication,
    ApplicationOrnament,
    CreditEvaluation,
    LoanApproval,
    LoanAccount,
    Disbursement,
    LoanDocument,
    LoanCharge,
    LoanStatusHistory,
    LMSIntegrationLog
)
from .repayment import (
    EMISchedule,
    RepaymentTransaction,
    InterestAccrual,
    LoanAdjustment,
    LoanPrepayment,
    LoanStatement,
    AutoDebitMandate,
    LoanPenalty,
    LoanRenewal,
    RepaymentAllocationRule
)

__all__ = [
    # Product models
    "GoldProduct",
    "GoldProductInterest",
    "GoldProductTenure",
    "GoldProductLimits",
    "GoldProductCharge",
    "GoldProductDocument",
    "GoldProductEligibility",
    "GoldProductWorkflow",
    "GoldProductChannel",
    "GoldProductTax",
    # Journey models
    "GoldCustomerSession",
    "GoldCustomerSearchLog",
    "GoldProductSelection",
    "GoldEligibilityCheck",
    "GoldKYCVerification",
    "GoldJourneyStep",
    "GoldCustomerInteraction",
    # Appraisal models
    "GoldOrnamentType",
    "GoldMarketRate",
    "GoldAppraisalSession",
    "GoldOrnament",
    "GoldPurityTest",
    "GoldWeightVerification",
    "GoldAppraisalAnomaly",
    "GoldAppraisalPhoto",
    # Catalog models
    "GoldOrnamentPhoto",
    "GoldOrnamentStone",
    "GoldOrnamentStatusHistory",
    "GoldOrnamentMovement",
    "GoldOrnamentCondition",
    "GoldOrnamentTag",
    "GoldOrnamentComparison",
    "GoldOrnamentCertificate",
    "GoldOrnamentInsurance",
    "GoldOrnamentGroup",
    "GoldOrnamentGroupMember",
    # Vault models
    "GoldVault",
    "GoldVaultRack",
    "GoldVaultLocker",
    "GoldVaultTray",
    "GoldPacket",
    "GoldPacketOrnament",
    "GoldPacketMovement",
    "GoldVaultAudit",
    "GoldAuditFinding",
    "GoldVaultAccessLog",
    "GoldSecuritySeal",
    # Loan models
    "LoanApplication",
    "ApplicationOrnament",
    "CreditEvaluation",
    "LoanApproval",
    "LoanAccount",
    "Disbursement",
    "LoanDocument",
    "LoanCharge",
    "LoanStatusHistory",
    "LMSIntegrationLog",
    # Repayment models
    "EMISchedule",
    "RepaymentTransaction",
    "InterestAccrual",
    "LoanAdjustment",
    "LoanPrepayment",
    "LoanStatement",
    "AutoDebitMandate",
    "LoanPenalty",
    "LoanRenewal",
    "RepaymentAllocationRule",
]
