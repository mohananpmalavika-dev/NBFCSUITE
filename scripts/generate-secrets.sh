#!/bin/bash

# ================================================================
# Generate Secure Secrets for NBFC Suite Deployment
# ================================================================

echo "========================================"
echo "  NBFC Suite - Secret Key Generator"
echo "========================================"
echo ""

# Function to generate random string
generate_key() {
    local length=$1
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# Generate keys
echo "Generating secure keys..."
echo ""

SECRET_KEY=$(generate_key 64)
JWT_SECRET_KEY=$(generate_key 64)
DB_PASSWORD=$(generate_key 32)
REDIS_PASSWORD=$(generate_key 32)

# Display keys
echo "✅ Keys generated successfully!"
echo ""
echo "================================================"
echo "  COPY THESE VALUES - SAVE THEM SECURELY!"
echo "================================================"
echo ""

echo -e "\033[1;37mSECRET_KEY=\033[1;32m$SECRET_KEY\033[0m"
echo ""
echo -e "\033[1;37mJWT_SECRET_KEY=\033[1;32m$JWT_SECRET_KEY\033[0m"
echo ""
echo -e "\033[1;37mDB_PASSWORD=\033[1;32m$DB_PASSWORD\033[0m"
echo ""
echo -e "\033[1;37mREDIS_PASSWORD=\033[1;32m$REDIS_PASSWORD\033[0m"
echo ""

# Save to file
OUTPUT_FILE=".env.production.generated"

cat > $OUTPUT_FILE << EOF
# ================================================================
# NBFC Suite - Production Environment Variables
# Generated: $(date '+%Y-%m-%d %H:%M:%S')
# ================================================================

# Security Keys (REQUIRED)
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database (REQUIRED - Update host and user)
DATABASE_URL=postgresql://nbfc_user:$DB_PASSWORD@localhost:5432/nbfc_suite
DB_PASSWORD=$DB_PASSWORD

# Redis (Optional)
REDIS_URL=redis://:$REDIS_PASSWORD@localhost:6379/0
REDIS_PASSWORD=$REDIS_PASSWORD

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
SESSION_SECRET=$JWT_SECRET_KEY
SESSION_TIMEOUT=3600

EOF

echo "================================================"
echo "✅ Environment file saved to: $OUTPUT_FILE"
echo "================================================"
echo ""

echo -e "\033[1;33mNEXT STEPS:\033[0m"
echo "1. Review and update $OUTPUT_FILE with your settings"
echo "2. Update DATABASE_URL with correct host/user"
echo "3. Update CORS_ORIGINS with your domain"
echo "4. Update NEXT_PUBLIC_API_URL with your backend URL"
echo "5. Copy to .env file or add to deployment platform"
echo ""

echo -e "\033[1;36mFor Render.com deployment:\033[0m"
echo "- Copy each variable to Render Dashboard → Environment"
echo ""

echo -e "\033[1;36mFor DigitalOcean/AWS deployment:\033[0m"
echo -e "- Rename to .env.production: \033[1;32mmv $OUTPUT_FILE .env.production\033[0m"
echo ""

echo "================================================"
echo -e "\033[1;31m⚠️  SECURITY WARNING:\033[0m"
echo "- Keep these keys secret and secure"
echo "- Never commit .env files to Git"
echo "- Use different keys for each environment"
echo "================================================"
echo ""

echo "Done! 🚀"
