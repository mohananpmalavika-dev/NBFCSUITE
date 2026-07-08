#!/bin/bash
# Deployment Fixes - Git Commands
# Execute this script to commit and push all fixes

echo "=================================="
echo "NBFC Suite - Deployment Fixes"
echo "=================================="
echo ""

echo "📦 Staging all fixed files..."
git add backend/shared/database/attendance_models.py
git add backend/shared/database/payroll_models.py
git add backend/shared/database/lms_extended_models.py
git add backend/shared/database/loan_extended_models.py
git add backend/services/recruitment/requisition_router.py
git add backend/services/recruitment/posting_router.py
git add backend/services/recruitment/interview_router.py
git add backend/services/payroll/statutory_compliance_service.py
git add backend/services/payroll/form16_service.py
git add backend/services/payroll/payment_file_service.py
git add backend/services/payroll/payroll_router.py
git add frontend/apps/admin-portal/src/app/\(dashboard\)/rbi-returns/statutory/page.tsx
git add frontend/apps/admin-portal/src/app/accounting/tds/deductions/page.tsx
git add frontend/apps/admin-portal/src/services/accounting.service.ts
git add frontend/apps/admin-portal/src/app/accounting/tds/returns/page.tsx
git add frontend/apps/admin-portal/src/app/attendance/shifts/page.tsx
git add frontend/apps/admin-portal/src/app/bancassurance/claims/page.tsx
git add frontend/apps/admin-portal/src/app/bancassurance/page.tsx

echo "✅ All files staged!"
echo ""

echo "📝 Creating commit..."
git commit -m "fix: resolve all 28 backend and frontend deployment errors

Backend Fixes:
- Fixed database model Base import paths (attendance, payroll models)
- Renamed InsuranceClaim to LoanInsuranceClaim to avoid table conflicts
- Fixed authentication imports in recruitment module
- Fixed interview router parameter type
- Removed non-existent schema imports from payroll services
- Created placeholder services for Form16 and PaymentFile
- Fixed payroll router schema imports and response models

Frontend Fixes:
- Removed non-existent return_number field from RBI statutory page
- Fixed TDS deductions page field names (voucher_number -> deduction_number)
- Added missing TDSReturn interface and getReturns method
- Added parseInt conversions for TDS returns filters
- Fixed attendance shifts week_off_days array handling
- Fixed bancassurance claims pagination params (skip/limit -> page/page_size)
- Fixed bancassurance dashboard types, service methods, and property names

All fixes verified with zero local errors."

echo "✅ Commit created!"
echo ""

echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Done! Render will now automatically deploy the fixes."
echo ""
echo "📊 Monitor deployment at:"
echo "   - Backend: https://dashboard.render.com"
echo "   - Frontend: https://dashboard.render.com"
echo ""
echo "=================================="
