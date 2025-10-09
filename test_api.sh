#!/bin/bash

# Test API Endpoints
# Usage: ./test_api.sh [BASE_URL] [SECRET]
# Example: ./test_api.sh http://localhost:8000 your_secret

BASE_URL=${1:-http://localhost:8000}
SECRET=${2:-your_secret}

echo "🧪 Testing API Endpoints"
echo "Base URL: $BASE_URL"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url")
    fi
    
    if [ "$response" -eq 200 ] || [ "$response" -eq 404 ]; then
        echo -e "${GREEN}✓${NC} (HTTP $response)"
    else
        echo -e "${RED}✗${NC} (HTTP $response)"
    fi
}

echo "=== Core Endpoints ==="
test_endpoint "Health Check" "$BASE_URL/health"
test_endpoint "Root" "$BASE_URL/"
echo ""

echo "=== CRUD Endpoints ==="
test_endpoint "Documents List" "$BASE_URL/api/documents"
test_endpoint "Query Logs List" "$BASE_URL/api/query-logs"
test_endpoint "Feedback List" "$BASE_URL/api/feedback"
test_endpoint "Chunks List" "$BASE_URL/api/chunks"
echo ""

echo "=== Admin Endpoints ==="
test_endpoint "DB Info" "$BASE_URL/api/v1/admin/db-info?secret=$SECRET"
echo ""

echo "=== Detailed Check ==="
echo "Fetching documents..."
curl -s "$BASE_URL/api/documents" | python3 -m json.tool | head -20
echo ""

echo "Fetching query logs..."
curl -s "$BASE_URL/api/query-logs?limit=5" | python3 -m json.tool | head -20
echo ""

echo "✅ Testing complete!"

