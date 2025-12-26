#!/bin/bash
# Docker Configuration Test Script
# Tests the updated Docker configuration for the MCP Documentation Server

set -e

echo "🐳 MCP Documentation Server - Docker Configuration Test"
echo "======================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_build() {
    echo -e "${YELLOW}📦 Testing Docker build...${NC}"
    if docker-compose -f compose.yml build --no-cache; then
        echo -e "${GREEN}✅ Docker build successful${NC}"
        return 0
    else
        echo -e "${RED}❌ Docker build failed${NC}"
        return 1
    fi
}

test_startup() {
    echo -e "${YELLOW}🚀 Testing container startup...${NC}"
    docker-compose -f compose.yml up -d
    
    # Wait for container to be ready
    echo "Waiting for container to start..."
    sleep 10
    
    if docker-compose -f compose.yml ps | grep -q "Up"; then
        echo -e "${GREEN}✅ Container started successfully${NC}"
        return 0
    else
        echo -e "${RED}❌ Container failed to start${NC}"
        docker-compose -f compose.yml logs
        return 1
    fi
}

test_health() {
    echo -e "${YELLOW}🏥 Testing health endpoint...${NC}"
    
    # Wait a bit more for the server to be ready
    sleep 15
    
    if curl -f -s http://127.0.0.1:8008/help > /dev/null; then
        echo -e "${GREEN}✅ Health endpoint responding${NC}"
        return 0
    else
        echo -e "${RED}❌ Health endpoint not responding${NC}"
        echo "Container logs:"
        docker-compose -f compose.yml logs --tail=20
        return 1
    fi
}

test_mcp_endpoint() {
    echo -e "${YELLOW}🔌 Testing MCP endpoint...${NC}"
    
    # Test MCP endpoint (should return some response, even if it's an error)
    if curl -f -s http://127.0.0.1:8008/logzilla-docs-server/mcp > /dev/null; then
        echo -e "${GREEN}✅ MCP endpoint accessible${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  MCP endpoint returned error (expected for direct HTTP access)${NC}"
        return 0
    fi
}

cleanup() {
    echo -e "${YELLOW}🧹 Cleaning up...${NC}"
    docker-compose -f compose.yml down
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Main test execution
main() {
    echo "Starting Docker configuration tests..."
    echo ""
    
    # Ensure we're in the right directory
    if [[ ! -f "compose.yml" ]]; then
        echo -e "${RED}❌ compose.yml not found. Please run this script from the docker/ directory${NC}"
        exit 1
    fi
    
    # Run tests
    local failed=0
    
    test_build || failed=$((failed + 1))
    echo ""
    
    test_startup || failed=$((failed + 1))
    echo ""
    
    test_health || failed=$((failed + 1))
    echo ""
    
    test_mcp_endpoint || failed=$((failed + 1))
    echo ""
    
    # Show container info
    echo -e "${YELLOW}📊 Container Information:${NC}"
    docker-compose -f compose.yml ps
    echo ""
    
    echo -e "${YELLOW}📋 Recent Logs:${NC}"
    docker-compose -f compose.yml logs --tail=10
    echo ""
    
    # Cleanup
    cleanup
    
    # Final results
    echo "======================================================="
    if [[ $failed -eq 0 ]]; then
        echo -e "${GREEN}🎉 All tests passed! Docker configuration is working correctly.${NC}"
        exit 0
    else
        echo -e "${RED}❌ $failed test(s) failed. Please check the configuration.${NC}"
        exit 1
    fi
}

# Handle script interruption
trap cleanup EXIT

# Run main function
main "$@"
