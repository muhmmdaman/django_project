#!/bin/bash

# PythonAnywhere Pre-Deployment Verification Script
# Run this script to verify your project is ready for deployment

echo "=================================="
echo "PythonAnywhere Pre-Deployment Check"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

passed=0
failed=0

# Helper functions
check_pass() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
    ((passed++))
}

check_fail() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    ((failed++))
}

check_warn() {
    echo -e "${YELLOW}⚠ WARN:${NC} $1"
}

echo "1. Checking Repository..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    check_pass "Git repository found"
else
    check_fail "Not a git repository"
fi

if [ -z "$(git status --porcelain)" ]; then
    check_pass "No uncommitted changes"
else
    check_warn "Uncommitted changes exist (may be OK)"
fi

echo ""
echo "2. Checking Requirements..."
if [ -f "requirements.txt" ]; then
    check_pass "requirements.txt exists"
    line_count=$(wc -l < requirements.txt)
    echo "  → Contains $line_count packages"
else
    check_fail "requirements.txt not found"
fi

echo ""
echo "3. Checking Django Configuration..."
if [ -f "Django-Project/config/config/settings.py" ]; then
    check_pass "Django settings.py found"

    if grep -q "os.getenv" Django-Project/config/config/settings.py; then
        check_pass "Using environment variables for configuration"
    else
        check_fail "Not using environment variables"
    fi
else
    check_fail "Django settings.py not found"
fi

if [ -f ".env.example" ]; then
    check_pass ".env.example exists"
else
    check_fail ".env.example not found"
fi

echo ""
echo "4. Checking .gitignore..."
if grep -q "venv/" .gitignore; then
    check_pass "venv/ in .gitignore"
else
    check_fail "venv/ NOT in .gitignore"
fi

if grep -q "__pycache__" .gitignore; then
    check_pass "__pycache__/ in .gitignore"
else
    check_fail "__pycache__/ NOT in .gitignore"
fi

if grep -q "\.env" .gitignore; then
    check_pass ".env in .gitignore"
else
    check_fail ".env NOT in .gitignore"
fi

if grep -q "db.sqlite3" .gitignore; then
    check_pass "db.sqlite3 in .gitignore"
else
    check_fail "db.sqlite3 NOT in .gitignore"
fi

echo ""
echo "5. Checking Static Files Configuration..."
if [ -d "Django-Project/config/static" ]; then
    check_pass "Static files directory exists"
else
    check_warn "Static files directory not found (may create during collectstatic)"
fi

if grep -q "STATIC_URL" Django-Project/config/config/settings.py; then
    check_pass "STATIC_URL configured"
else
    check_fail "STATIC_URL not found"
fi

if grep -q "STATICFILES_STORAGE" Django-Project/config/config/settings.py; then
    check_pass "STATICFILES_STORAGE configured"
else
    check_warn "STATICFILES_STORAGE not configured"
fi

echo ""
echo "6. Checking Media Files Configuration..."
if grep -q "MEDIA_URL" Django-Project/config/config/settings.py; then
    check_pass "MEDIA_URL configured"
else
    check_warn "MEDIA_URL not configured"
fi

echo ""
echo "7. Checking WSGI..."
if [ -f "wsgi.py" ]; then
    check_pass "wsgi.py exists"
    if grep -q "get_wsgi_application()" wsgi.py; then
        check_pass "WSGI application returned"
    else
        check_fail "WSGI application not returned"
    fi
else
    check_fail "wsgi.py not found"
fi

echo ""
echo "8. Checking Deployment Documentation..."
if [ -f "PYTHONANYWHERE_DEPLOYMENT.md" ]; then
    check_pass "PYTHONANYWHERE_DEPLOYMENT.md exists"
else
    check_fail "PYTHONANYWHERE_DEPLOYMENT.md not found"
fi

if [ -f "PYTHONANYWHERE_CHECKLIST.md" ]; then
    check_pass "PYTHONANYWHERE_CHECKLIST.md exists"
else
    check_fail "PYTHONANYWHERE_CHECKLIST.md not found"
fi

if [ -f "PYTHONANYWHERE_QUICK_REFERENCE.md" ]; then
    check_pass "PYTHONANYWHERE_QUICK_REFERENCE.md exists"
else
    check_fail "PYTHONANYWHERE_QUICK_REFERENCE.md not found"
fi

echo ""
echo "9. Checking for Unwanted Files..."
if [ -f "Procfile" ]; then
    check_fail "Procfile found (for other platforms)"
fi

if [ -f "Dockerfile" ]; then
    check_fail "Dockerfile found (for other platforms)"
fi

if [ -f "render.yaml" ]; then
    check_fail "render.yaml found (for other platforms)"
fi

if [ -f "vercel.json" ]; then
    check_fail "vercel.json found (for other platforms)"
fi

if [ ! -f "Procfile" ] && [ ! -f "Dockerfile" ] && [ ! -f "render.yaml" ] && [ ! -f "vercel.json" ]; then
    check_pass "No conflicting deployment files found"
fi

echo ""
echo "10. Checking Django Project Structure..."
if [ -f "Django-Project/config/manage.py" ]; then
    check_pass "manage.py found"
else
    check_fail "manage.py not found"
fi

migrations_count=$(find Django-Project/config/apps -name "migrations" -type d | wc -l)
if [ $migrations_count -gt 0 ]; then
    check_pass "Migration directories found ($migrations_count)"
else
    check_warn "No migration directories found"
fi

echo ""
echo "=================================="
echo "Summary"
echo "=================================="
total=$((passed + failed))
echo "Passed: $passed"
echo "Failed: $failed"
echo "Total:  $total"

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Project is ready for PythonAnywhere deployment.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Read PYTHONANYWHERE_DEPLOYMENT.md"
    echo "2. Go through PYTHONANYWHERE_CHECKLIST.md"
    echo "3. Follow deployment steps"
    exit 0
else
    echo -e "${RED}✗ $failed check(s) failed. Please fix issues before deployment.${NC}"
    exit 1
fi
