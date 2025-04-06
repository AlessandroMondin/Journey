#!/bin/bash
set -e

# Terminal colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================ RAG Service API Test =================${NC}"

# Generate a test token
echo -e "${BLUE}Generating JWT token...${NC}"
TOKEN=$(python test_token.py)
echo "$TOKEN" | tail -n 1 > token.txt
TEST_TOKEN=$(cat token.txt)
echo -e "${GREEN}Token generated: ${TEST_TOKEN:0:20}...${NC}"

# API Service base URL
API_URL="http://localhost:8000"
# Embedder Service base URL (for direct testing)
EMBEDDER_URL="http://localhost:8001"
# Service API key from .env
SERVICE_API_KEY=$(grep SERVICE_API_KEY .env | cut -d "=" -f2 || echo "internal-service-api-key")
# Test user ID for direct embedder service tests
TEST_USER_ID="direct-test-user"

echo -e "\n${BLUE}Testing health endpoints...${NC}"
echo -e "API Service:"
RESPONSE=$(curl -s "$API_URL/")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Connected to API Service: $RESPONSE${NC}"
else
    echo -e "${RED}Failed to connect to API Service${NC}"
fi

echo -e "\nEmbedder Service:"
RESPONSE=$(curl -s "$EMBEDDER_URL/")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Connected to Embedder Service: $RESPONSE${NC}"
else
    echo -e "${RED}Failed to connect to Embedder Service${NC}"
fi

echo -e "\n${BLUE}Testing API Service endpoints (requires JWT token)...${NC}"

echo -e "\n1. Storing a document:"
RESPONSE=$(curl -s -X POST "$API_URL/rag/store?text=This%20is%20a%20test%20document%20for%20RAG%20service" \
  -H "Authorization: Bearer $TEST_TOKEN")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Document stored: $RESPONSE${NC}"
else
    echo -e "${RED}Failed to store document${NC}"
fi

echo -e "\n2. Querying for similar documents:"
RESPONSE=$(curl -s -X POST "$API_URL/rag/query?query=test%20document&limit=3" \
  -H "Authorization: Bearer $TEST_TOKEN")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Query results: $RESPONSE${NC}"
else
    echo -e "${RED}Failed to query documents${NC}"
fi

echo -e "\n3. Storing another document:"
RESPONSE=$(curl -s -X POST "$API_URL/rag/store?text=This%20is%20a%20second%20test%20document%20with%20different%20content" \
  -H "Authorization: Bearer $TEST_TOKEN")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Document stored: $RESPONSE${NC}"
else
    echo -e "${RED}Failed to store document${NC}"
fi

echo -e "\n4. Querying again to see both documents:"
RESPONSE=$(curl -s -X POST "$API_URL/rag/query?query=test%20document&limit=5" \
  -H "Authorization: Bearer $TEST_TOKEN")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Query results: $RESPONSE${NC}"
else
    echo -e "${RED}Failed to query documents${NC}"
fi

echo -e "\n5. Deleting all documents for the user:"
RESPONSE=$(curl -s -X DELETE "$API_URL/rag/documents" \
  -H "Authorization: Bearer $TEST_TOKEN")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Documents deleted: $RESPONSE${NC}"
else
    echo -e "${RED}Failed to delete documents${NC}"
fi

echo -e "\n${BLUE}Testing Embedder Service endpoints directly (requires API key)...${NC}"

echo -e "\n1. Direct embedding request:"
RESPONSE=$(curl -s -X POST "$EMBEDDER_URL/embed" \
  -H "X-API-Key: $SERVICE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a direct test for the embedder service", "owner_id": "direct-test-user"}')
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Embedding created: $RESPONSE${NC}"
else
    echo -e "${RED}Failed to call embedder service directly${NC}"
fi

echo -e "\n2. Direct query request:"
RESPONSE=$(curl -s -X POST "$EMBEDDER_URL/query/$TEST_USER_ID" \
  -H "X-API-Key: $SERVICE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test embedder", "limit": 3}')
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Query results: $RESPONSE${NC}"
else
    echo -e "${RED}Failed to query embedder service directly${NC}"
fi

echo -e "\n${GREEN}Tests completed!${NC}"
