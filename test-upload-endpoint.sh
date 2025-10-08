#!/bin/bash
# Test script for the /api/ingest/upload endpoint
# Usage: ./test-upload-endpoint.sh [your-app-url]

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default to localhost if no URL provided
APP_URL="${1:-http://localhost:3000}"

echo -e "${YELLOW}Testing upload endpoint at: ${APP_URL}/api/ingest/upload${NC}\n"

# Create a test CSV file
echo "Creating test CSV file..."
cat > test-data.csv << 'EOF'
id,product,sales,date
1,Widget A,1500,2024-01-15
2,Widget B,2300,2024-01-16
3,Widget C,1800,2024-01-17
4,Widget A,2100,2024-01-18
5,Widget B,1900,2024-01-19
EOF

echo -e "${GREEN}✓ Test file created: test-data.csv${NC}\n"

# Test the endpoint
echo "Testing upload endpoint..."
echo "----------------------------------------"

RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  -X POST "${APP_URL}/api/ingest/upload" \
  -F "file=@test-data.csv" \
  -F "user_id=test-user-123")

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

echo "Response:"
echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
echo ""
echo "HTTP Status Code: $HTTP_CODE"
echo "----------------------------------------"

# Check result
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "\n${GREEN}✓ SUCCESS! Upload endpoint is working correctly.${NC}"
    exit 0
elif [ "$HTTP_CODE" = "404" ]; then
    echo -e "\n${RED}✗ ERROR: 404 Not Found${NC}"
    echo -e "${YELLOW}The endpoint is still not found. This usually means:${NC}"
    echo "  1. The deployment hasn't been triggered yet"
    echo "  2. The vercel.json changes haven't been deployed"
    echo "  3. The API route is not being built correctly"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Make sure you've committed and pushed the vercel.json changes"
    echo "  2. Trigger a new deployment on Vercel"
    echo "  3. Check Vercel build logs for any errors"
    exit 1
else
    echo -e "\n${YELLOW}⚠ Warning: Got HTTP $HTTP_CODE${NC}"
    echo "This might indicate an issue with the backend or configuration."
    exit 1
fi
