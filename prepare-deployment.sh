#!/bin/bash
# ============================================
# NBFC Suite - Deployment Preparation Script
# ============================================

echo "============================================"
echo "  NBFC Suite - Deployment Preparation"
echo "============================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to generate random string
generate_random_string() {
    cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
}

# Step 1: Check Git status
echo -e "${YELLOW}[1/6] Checking Git status...${NC}"
if [ -d .git ]; then
    echo -e "${GREEN}  ✓ Git repository found${NC}"
else
    echo -e "${YELLOW}  ! Git repository not found. Initializing...${NC}"
    git init
    echo -e "${GREEN}  ✓ Git initialized${NC}"
fi

# Step 2: Generate secret keys
echo ""
echo -e "${YELLOW}[2/6] Generating secure keys...${NC}"
SECRET_KEY=$(generate_random_string)
JWT_SECRET_KEY=$(generate_random_string)

echo -e "${GREEN}  ✓ SECRET_KEY generated: $SECRET_KEY${NC}"
echo -e "${GREEN}  ✓ JWT_SECRET_KEY generated: $JWT_SECRET_KEY${NC}"

# Save to file
cat > .deployment-keys.txt << EOF
# NBFC Suite - Generated Secret Keys
# Generated on: $(date "+%Y-%m-%d %H:%M:%S")
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
EOF

echo -e "${GREEN}  ✓ Keys saved to .deployment-keys.txt${NC}"

# Step 3: Check required files
echo ""
echo -e "${YELLOW}[3/6] Checking deployment files...${NC}"

required_files=(
    "backend/runtime.txt"
    "backend/requirements.txt"
    "render.yaml"
    "Dockerfile.backend"
    ".dockerignore"
    ".gitignore"
)

all_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}  ✓ $file exists${NC}"
    else
        echo -e "${RED}  ✗ $file missing${NC}"
        all_exist=false
    fi
done

# Step 4: Create .gitignore if missing
echo ""
echo -e "${YELLOW}[4/6] Checking .gitignore...${NC}"
if [ ! -f ".gitignore" ]; then
    echo -e "${YELLOW}  ! Creating .gitignore...${NC}"
    cat > .gitignore << 'EOF'
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
EOF
    echo -e "${GREEN}  ✓ .gitignore created${NC}"
else
    echo -e "${GREEN}  ✓ .gitignore exists${NC}"
fi

# Step 5: Stage files
echo ""
echo -e "${YELLOW}[5/6] Staging files for Git...${NC}"
git add .
if git status --short | grep -q .; then
    echo -e "${CYAN}  Files to commit:${NC}"
    git status --short
else
    echo -e "${GREEN}  ✓ No changes to commit${NC}"
fi

# Step 6: Display next steps
echo ""
echo -e "${GREEN}[6/6] Preparation complete!${NC}"
echo ""
echo "============================================"
echo "  NEXT STEPS"
echo "============================================"
echo ""
echo -e "${YELLOW}1. COMMIT YOUR CHANGES${NC}"
echo "   git commit -m 'Deploy: Ready for production deployment'"
echo ""
echo -e "${YELLOW}2. CREATE GITHUB REPOSITORY${NC}"
echo "   • Go to: https://github.com/new"
echo "   • Name: nbfc-suite"
echo "   • Make it private (recommended)"
echo "   • Don't add README, .gitignore, or license"
echo ""
echo -e "${YELLOW}3. PUSH TO GITHUB${NC}"
echo "   git remote add origin https://github.com/YOUR_USERNAME/nbfc-suite.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo -e "${YELLOW}4. DEPLOY ON RENDER${NC}"
echo "   • Visit: https://dashboard.render.com/"
echo "   • Click: New + → Blueprint"
echo "   • Select: Your GitHub repository"
echo "   • Add these environment variables:"
echo ""
echo -e "${CYAN}   SECRET_KEY=$SECRET_KEY${NC}"
echo -e "${CYAN}   JWT_SECRET_KEY=$JWT_SECRET_KEY${NC}"
echo ""
echo -e "${YELLOW}5. SAVE YOUR KEYS${NC}"
echo "   • Keys saved in: .deployment-keys.txt"
echo -e "${RED}   • Keep this file secure!${NC}"
echo -e "${RED}   • DO NOT commit it to Git!${NC}"
echo ""
echo "============================================"
echo ""
echo -e "${GREEN}✅ Preparation complete! Ready to deploy.${NC}"
echo ""

# Make keys file viewable
chmod 600 .deployment-keys.txt 2>/dev/null || true
