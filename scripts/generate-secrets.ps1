# ================================================================
# Generate Secure Secrets for NBFC Suite Deployment
# ================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NBFC Suite - Secret Key Generator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to generate random string
function Generate-RandomKey {
    param (
        [int]$Length = 64
    )
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:,.<>?"
    $key = -join ((1..$Length) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
    return $key
}

# Generate keys
Write-Host "Generating secure keys..." -ForegroundColor Yellow
Write-Host ""

$secretKey = Generate-RandomKey -Length 64
$jwtSecret = Generate-RandomKey -Length 64
$dbPassword = Generate-RandomKey -Length 32
$redisPassword = Generate-RandomKey -Length 32

# Display keys
Write-Host "✅ Keys generated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  COPY THESE VALUES - SAVE THEM SECURELY!" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "SECRET_KEY=" -NoNewline -ForegroundColor White
Write-Host $secretKey -ForegroundColor Green
Write-Host ""

Write-Host "JWT_SECRET_KEY=" -NoNewline -ForegroundColor White
Write-Host $jwtSecret -ForegroundColor Green
Write-Host ""

Write-Host "DB_PASSWORD=" -NoNewline -ForegroundColor White
Write-Host $dbPassword -ForegroundColor Green
Write-Host ""

Write-Host "REDIS_PASSWORD=" -NoNewline -ForegroundColor White
Write-Host $redisPassword -ForegroundColor Green
Write-Host ""

# Save to file
$envFile = @"
# ================================================================
# NBFC Suite - Production Environment Variables
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# ================================================================

# Security Keys (REQUIRED)
SECRET_KEY=$secretKey
JWT_SECRET_KEY=$jwtSecret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database (REQUIRED - Update host and user)
DATABASE_URL=postgresql://nbfc_user:$dbPassword@localhost:5432/nbfc_suite
DB_PASSWORD=$dbPassword

# Redis (Optional)
REDIS_URL=redis://:$redisPassword@localhost:6379/0
REDIS_PASSWORD=$redisPassword

# Application Settings
APP_ENV=production
LOG_LEVEL=INFO
ENABLE_SWAGGER=true
TENANT_ISOLATION_ENABLED=true
DEFAULT_TENANT=default

# CORS (Update with your domain)
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Frontend API URL (Update with your backend URL)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Email Settings (Optional - Configure for production)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourdomain.com

# File Upload Settings
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=./uploads

# Session Settings
SESSION_SECRET=$jwtSecret
SESSION_TIMEOUT=3600

"@

$outputFile = ".env.production.generated"
$envFile | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "✅ Environment file saved to: $outputFile" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Review and update $outputFile with your settings" -ForegroundColor White
Write-Host "2. Update DATABASE_URL with correct host/user" -ForegroundColor White
Write-Host "3. Update CORS_ORIGINS with your domain" -ForegroundColor White
Write-Host "4. Update NEXT_PUBLIC_API_URL with your backend URL" -ForegroundColor White
Write-Host "5. Copy to .env file or add to deployment platform" -ForegroundColor White
Write-Host ""

Write-Host "For Render.com deployment:" -ForegroundColor Cyan
Write-Host "- Copy each variable to Render Dashboard → Environment" -ForegroundColor White
Write-Host ""

Write-Host "For DigitalOcean/AWS deployment:" -ForegroundColor Cyan
Write-Host "- Rename to .env.production: " -NoNewline -ForegroundColor White
Write-Host "mv $outputFile .env.production" -ForegroundColor Green
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "⚠️  SECURITY WARNING:" -ForegroundColor Red
Write-Host "- Keep these keys secret and secure" -ForegroundColor White
Write-Host "- Never commit .env files to Git" -ForegroundColor White
Write-Host "- Use different keys for each environment" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Offer to copy to clipboard (Windows only)
$copyToClipboard = Read-Host "Copy SECRET_KEY to clipboard? (y/n)"
if ($copyToClipboard -eq 'y') {
    $secretKey | Set-Clipboard
    Write-Host "✅ SECRET_KEY copied to clipboard!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done! 🚀" -ForegroundColor Green
