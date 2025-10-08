#!/bin/bash
# Comprehensive test suite runner for the entire project
# This script runs all tests: YAML validation, integration tests, and backend tests

set -e  # Exit on first error

echo "=========================================="
echo "  COMPREHENSIVE TEST SUITE"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall success
ALL_PASSED=true

echo "1️⃣  Running YAML Syntax Validation..."
echo "--------------------------------------"
if yamllint render.yaml; then
    echo -e "${GREEN}✅ YAML syntax validation passed${NC}"
else
    echo -e "${RED}❌ YAML syntax validation failed${NC}"
    ALL_PASSED=false
fi
echo ""

echo "2️⃣  Running YAML Structure Tests..."
echo "--------------------------------------"
if python3 test_render_yaml.py; then
    echo -e "${GREEN}✅ YAML structure tests passed${NC}"
else
    echo -e "${RED}❌ YAML structure tests failed${NC}"
    ALL_PASSED=false
fi
echo ""

echo "3️⃣  Running Integration Tests..."
echo "--------------------------------------"
if python3 test_render_integration.py; then
    echo -e "${GREEN}✅ Integration tests passed${NC}"
else
    echo -e "${RED}❌ Integration tests failed${NC}"
    ALL_PASSED=false
fi
echo ""

echo "4️⃣  Running Backend Unit Tests..."
echo "--------------------------------------"
cd backend
if python3 -m pytest tests/ -v; then
    echo -e "${GREEN}✅ Backend tests passed${NC}"
else
    echo -e "${RED}❌ Backend tests failed${NC}"
    ALL_PASSED=false
fi
cd ..
echo ""

echo "=========================================="
echo "  TEST SUMMARY"
echo "=========================================="

if [ "$ALL_PASSED" = true ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    echo "Your configuration is ready for deployment:"
    echo "  ✓ YAML syntax is valid"
    echo "  ✓ Render.yaml structure is correct"
    echo "  ✓ Service dependencies are configured"
    echo "  ✓ Backend health checks pass"
    echo ""
    echo "Next steps:"
    echo "  1. Commit your changes: git add render.yaml && git commit -m 'Fix: Updated render.yaml configuration'"
    echo "  2. Push to deploy: git push origin main"
    echo "  3. Monitor deployment at: https://dashboard.render.com"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review the errors above and fix them before deploying."
    exit 1
fi
