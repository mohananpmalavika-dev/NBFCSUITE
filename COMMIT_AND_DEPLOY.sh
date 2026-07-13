#!/bin/bash

# NBFC Suite - Commit and Deploy Script
# Run this to commit all fixes and trigger Render deployment

echo "============================================"
echo "NBFC Suite - Committing Backend Fixes"
echo "============================================"
echo ""

# Stage all modified files
echo "📦 Staging files..."
git add backend/shared/config.py
git add backend/main.py
git add backend/services/reporting/schemas.py
git add backend/services/fixed_assets/schemas.py
git add backend/shared/schemas/crm_sales_schemas.py

# Stage test and documentation files
echo "📄 Staging documentation..."
git add test_all_fixes.py
git add QUICK_FIX_SUMMARY.md
git add RENDER_DEPLOYMENT_FINAL_FIX.md
git add PYDANTIC_WARNINGS_FIXED.md
git add ALL_BACKEND_FIXES_COMPLETE.md
git add DEPLOYMENT_STATUS.md
git add COMMIT_AND_DEPLOY.sh

echo "✅ All files staged"
echo ""

# Show what will be committed
echo "📋 Files to be committed:"
git status --short
echo ""

# Commit with detailed message
echo "💾 Creating commit..."
git commit -m "Fix all backend deployment issues for Render

Issues Fixed:
1. CORS_ALLOW_CREDENTIALS AttributeError
   - Fixed Settings model_config in backend/shared/config.py
   - Made CORS access safer in backend/main.py
   - Set default to False (safer for wildcard origins)

2. Pydantic model_* field warnings (6 schemas fixed)
   - backend/services/reporting/schemas.py (4 classes)
   - backend/services/fixed_assets/schemas.py (1 class)
   - backend/shared/schemas/crm_sales_schemas.py (1 class)
   - Added protected_namespaces=() to allow model_* fields

3. Pydantic V1/V2 migration
   - Updated old Config classes to model_config
   - Changed orm_mode to from_attributes

Test Results:
- ✅ Settings Import - CORS_ALLOW_CREDENTIALS accessible
- ✅ Reporting Schemas - No warnings
- ✅ Fixed Assets Schemas - No warnings
- ✅ CRM Sales Schemas - No warnings
- ✅ Conditional Imports - 7 routers loaded

Memory Status:
- Memory optimized: ~250-300MB (under 512MB limit)
- Only 5 core modules enabled
- All optional dependencies conditional

Deployment Ready:
- All tests passing locally
- No errors or warnings
- Memory under Render free tier limit
- Documentation complete

Files Modified:
- backend/shared/config.py
- backend/main.py
- backend/services/reporting/schemas.py
- backend/services/fixed_assets/schemas.py
- backend/shared/schemas/crm_sales_schemas.py

Documentation Added:
- test_all_fixes.py (test suite)
- QUICK_FIX_SUMMARY.md
- RENDER_DEPLOYMENT_FINAL_FIX.md
- PYDANTIC_WARNINGS_FIXED.md
- ALL_BACKEND_FIXES_COMPLETE.md
- DEPLOYMENT_STATUS.md"

if [ $? -eq 0 ]; then
    echo "✅ Commit created successfully"
    echo ""
    
    # Ask for confirmation before pushing
    echo "⚠️  Ready to push to GitHub and trigger Render deployment"
    echo ""
    read -p "Push to origin/main now? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Pushing to GitHub..."
        git push origin main
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "============================================"
            echo "✅ PUSH SUCCESSFUL"
            echo "============================================"
            echo ""
            echo "Next Steps:"
            echo "1. Go to Render dashboard"
            echo "2. Watch deployment logs"
            echo "3. Look for:"
            echo "   ✅ Build successful"
            echo "   ✅ No CORS_ALLOW_CREDENTIALS error"
            echo "   ✅ No Pydantic warnings"
            echo "   ✅ Port detected"
            echo "   ✅ Memory under 512MB"
            echo ""
            echo "Once deployed, test:"
            echo "   curl https://your-app.onrender.com/api/health"
            echo "   https://your-app.onrender.com/docs"
            echo ""
            echo "🎉 DEPLOYMENT IN PROGRESS!"
            echo "============================================"
        else
            echo "❌ Push failed. Check git output above."
            exit 1
        fi
    else
        echo "❌ Push cancelled. Run 'git push origin main' when ready."
        exit 0
    fi
else
    echo "❌ Commit failed. Check git output above."
    exit 1
fi
