# ============================================
# NBFC Suite - Deployment Preparation Script
# ============================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NBFC Suite - Deployment Preparation" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Function to generate random string
function Generate-RandomString {
    param([int]$length = 32)
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    $random = -join ((1..$length) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
    return $random
}

# Step 1: Check Git status
Write-Host "[1/6] Checking Git status..." -ForegroundColor Yellow
if (Test-Path .git) {
    Write-Host "  ✓ Git repository found" -ForegroundColor Green
} else {
    Write-Host "  ! Git repository not found. Initializing..." -ForegroundColor Yellow
    git init
    Write-Host "  ✓ Git initialized" -ForegroundColor Green
}

# Step 2: Generate secret keys
Write-Host ""
Write-Host "[2/6] Generating secure keys..." -ForegroundColor Yellow
$SECRET_KEY = Generate-RandomString -length 32
$JWT_SECRET_KEY = Generate-RandomString -length 32

Write-Host "  ✓ SECRET_KEY generated: $SECRET_KEY" -ForegroundColor Green
Write-Host "  ✓ JWT_SECRET_KEY generated: $JWT_SECRET_KEY" -ForegroundColor Green

# Save to file for reference
$keysContent = @"
# NBFC Suite - Generated Secret Keys
# Generated on: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# 
# IMPORTANT: Keep these keys secure!
# Add them to your deployment platform (Render, DigitalOcean, etc.)
#
# DO NOT commit this file to Git!

SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
"@

$keysContent | Out-File -FilePath ".deployment-keys.txt" -Encoding UTF8
Write-Host "  ✓ Keys saved to .deployment-keys.txt" -ForegroundColor Green

# Step 3: Check required files
Write-Host ""
Write-Host "[3/6] Checking deployment files..." -ForegroundColor Yellow

$requiredFiles = @(
    "backend/runtime.txt",
    "backend/requirements.txt",
    "render.yaml",
    "Dockerfile.backend",
    ".dockerignore",
    ".gitignore"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file missing" -ForegroundColor Red
        $allFilesExist = $false
    }
}

# Step 4: Create .gitignore if missing
Write-Host ""
Write-Host "[4/6] Checking .gitignore..." -ForegroundColor Yellow
if (-not (Test-Path ".gitignore")) {
    Write-Host "  ! Creating .gitignore..." -ForegroundColor Yellow
    @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
*.egg-info/
dist/
build/

# Node
node_modules/
.next/
out/
npm-debug.log*
yarn-error.log*

# Environment
.env
.env.local
.env.*.local
.deployment-keys.txt

# Database
*.db
*.sqlite

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Uploads
uploads/
logs/
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "  ✓ .gitignore created" -ForegroundColor Green
} else {
    Write-Host "  ✓ .gitignore exists" -ForegroundColor Green
}

# Step 5: Stage files for commit
Write-Host ""
Write-Host "[5/6] Staging files for Git..." -ForegroundColor Yellow
git add .
$status = git status --short
if ($status) {
    Write-Host "  Files to commit:" -ForegroundColor Cyan
    Write-Host $status
} else {
    Write-Host "  ✓ No changes to commit" -ForegroundColor Green
}

# Step 6: Display next steps
Write-Host ""
Write-Host "[6/6] Preparation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NEXT STEPS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. COMMIT YOUR CHANGES" -ForegroundColor Yellow
Write-Host "   git commit -m 'Deploy: Ready for production deployment'" -ForegroundColor White
Write-Host ""
Write-Host "2. CREATE GITHUB REPOSITORY" -ForegroundColor Yellow
Write-Host "   • Go to: https://github.com/new" -ForegroundColor White
Write-Host "   • Name: nbfc-suite" -ForegroundColor White
Write-Host "   • Make it private (recommended)" -ForegroundColor White
Write-Host "   • Don't add README, .gitignore, or license" -ForegroundColor White
Write-Host ""
Write-Host "3. PUSH TO GITHUB" -ForegroundColor Yellow
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/nbfc-suite.git" -ForegroundColor White
Write-Host "   git branch -M main" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "4. DEPLOY ON RENDER" -ForegroundColor Yellow
Write-Host "   • Visit: https://dashboard.render.com/" -ForegroundColor White
Write-Host "   • Click: New + → Blueprint" -ForegroundColor White
Write-Host "   • Select: Your GitHub repository" -ForegroundColor White
Write-Host "   • Add these environment variables:" -ForegroundColor White
Write-Host ""
Write-Host "   SECRET_KEY=$SECRET_KEY" -ForegroundColor Cyan
Write-Host "   JWT_SECRET_KEY=$JWT_SECRET_KEY" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. SAVE YOUR KEYS" -ForegroundColor Yellow
Write-Host "   • Keys saved in: .deployment-keys.txt" -ForegroundColor White
Write-Host "   • Keep this file secure!" -ForegroundColor Red
Write-Host "   • DO NOT commit it to Git!" -ForegroundColor Red
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Offer to open files
$openKeys = Read-Host "Open .deployment-keys.txt? (Y/N)"
if ($openKeys -eq "Y" -or $openKeys -eq "y") {
    notepad.exe ".deployment-keys.txt"
}

Write-Host ""
Write-Host "✅ Preparation complete! Ready to deploy." -ForegroundColor Green
Write-Host ""
