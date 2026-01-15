#!/bin/bash
# Test script to verify all endpoints are working

echo "Testing Zebo API endpoints..."
echo ""

# You can run this locally with: uvicorn zebo.main:app --reload
# Or change BASE_URL to your deployed service

BASE_URL=${1:-"http://localhost:8000"}

echo "🔍 Testing $BASE_URL"
echo "================================"

echo ""
echo "1️⃣  Testing root endpoint (/)..."
curl -s "$BASE_URL/" | jq .

echo ""
echo "2️⃣  Testing health endpoint (/health)..."
curl -s "$BASE_URL/health" | jq .

echo ""
echo "3️⃣  Testing ready endpoint (/ready)..."
curl -s "$BASE_URL/ready" | jq .

echo ""
echo "================================"
echo "✅ All endpoints tested!"
echo ""
echo "To test the CrewAI flow:"
echo "curl -X POST $BASE_URL/run -H 'Content-Type: application/json' -d '{\"sentence_count\": 3}'"
