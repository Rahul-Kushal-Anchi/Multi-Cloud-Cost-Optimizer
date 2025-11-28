#!/bin/bash
# Test script for production data availability endpoint

PROD_URL="http://aws-cost-optimizer-dev-alb-2097253605.us-east-1.elb.amazonaws.com"
ENDPOINT="/api/ml/data-availability"

echo "🧪 Testing Production Data Availability Endpoint"
echo "================================================"
echo ""

# Check if token is provided
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <auth_token>"
    echo ""
    echo "💡 To get your token:"
    echo "   1. Login to: $PROD_URL/login"
    echo "   2. Open browser console (F12)"
    echo "   3. Run: localStorage.getItem('token')"
    echo "   4. Copy the token and run: $0 YOUR_TOKEN"
    exit 1
fi

TOKEN=$1

echo "📡 Testing endpoint: $PROD_URL$ENDPOINT"
echo ""

# Test the endpoint
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$PROD_URL$ENDPOINT" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo "HTTP Status: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" == "200" ]; then
    echo "✅ Success! Response:"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    echo ""
    echo "📊 Summary:"
    echo "$BODY" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"   Days Available: {data.get('days_available', 'N/A')}\")
    print(f\"   Unique Days: {data.get('unique_days', 'N/A')}\")
    print(f\"   Date Range: {data.get('earliest_date', 'N/A')} to {data.get('latest_date', 'N/A')}\")
    print(f\"   Sufficient for ML: {'✅ YES' if data.get('sufficient_for_training') else '⚠️  NO'}\")
    print(f\"   Recommendation: {data.get('recommendation', 'N/A')}\")
    print(f\"   Message: {data.get('message', 'N/A')}\")
except:
    pass
" 2>/dev/null
elif [ "$HTTP_CODE" == "401" ]; then
    echo "❌ Authentication failed. Token may be invalid or expired."
    echo "   Please login again and get a fresh token."
elif [ "$HTTP_CODE" == "404" ]; then
    echo "⚠️  Endpoint not found. Code may not be deployed yet."
    echo "   Please deploy the latest code first."
else
    echo "❌ Error: $HTTP_CODE"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
fi


# Test script for production data availability endpoint

PROD_URL="http://aws-cost-optimizer-dev-alb-2097253605.us-east-1.elb.amazonaws.com"
ENDPOINT="/api/ml/data-availability"

echo "🧪 Testing Production Data Availability Endpoint"
echo "================================================"
echo ""

# Check if token is provided
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <auth_token>"
    echo ""
    echo "💡 To get your token:"
    echo "   1. Login to: $PROD_URL/login"
    echo "   2. Open browser console (F12)"
    echo "   3. Run: localStorage.getItem('token')"
    echo "   4. Copy the token and run: $0 YOUR_TOKEN"
    exit 1
fi

TOKEN=$1

echo "📡 Testing endpoint: $PROD_URL$ENDPOINT"
echo ""

# Test the endpoint
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$PROD_URL$ENDPOINT" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo "HTTP Status: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" == "200" ]; then
    echo "✅ Success! Response:"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    echo ""
    echo "📊 Summary:"
    echo "$BODY" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"   Days Available: {data.get('days_available', 'N/A')}\")
    print(f\"   Unique Days: {data.get('unique_days', 'N/A')}\")
    print(f\"   Date Range: {data.get('earliest_date', 'N/A')} to {data.get('latest_date', 'N/A')}\")
    print(f\"   Sufficient for ML: {'✅ YES' if data.get('sufficient_for_training') else '⚠️  NO'}\")
    print(f\"   Recommendation: {data.get('recommendation', 'N/A')}\")
    print(f\"   Message: {data.get('message', 'N/A')}\")
except:
    pass
" 2>/dev/null
elif [ "$HTTP_CODE" == "401" ]; then
    echo "❌ Authentication failed. Token may be invalid or expired."
    echo "   Please login again and get a fresh token."
elif [ "$HTTP_CODE" == "404" ]; then
    echo "⚠️  Endpoint not found. Code may not be deployed yet."
    echo "   Please deploy the latest code first."
else
    echo "❌ Error: $HTTP_CODE"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
fi



