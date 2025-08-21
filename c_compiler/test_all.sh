#!/bin/bash

echo "🧪 Testing Pyrinas C Compiler with all examples..."
echo "=================================================="

PASSED=0
FAILED=0
TOTAL=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_file() {
    local file="$1"
    local basename=$(basename "$file" .pyr)
    
    echo -n "Testing $file... "
    TOTAL=$((TOTAL + 1))
    
    # Try to compile with 10 second timeout
    if timeout 10 ./pyrinas-compiler "$file" -o "test_$basename" 2>/dev/null >/dev/null; then
        # If compilation succeeded, try to run it
        if timeout 5 "./test_$basename" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ PASS${NC}"
            PASSED=$((PASSED + 1))
        else
            echo -e "${YELLOW}⚠️  COMPILE_OK_RUN_FAIL${NC}"
            FAILED=$((FAILED + 1))
        fi
        # Clean up the executable
        rm -f "test_$basename"
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAILED=$((FAILED + 1))
    fi
}

# Test all .pyr files in examples directory
for file in ../examples/*.pyr; do
    if [ -f "$file" ]; then
        test_file "$file"
    fi
done

# Test all .pyr files in examples/modules directory  
for file in ../examples/modules/*.pyr; do
    if [ -f "$file" ]; then
        test_file "$file"
    fi
done

echo ""
echo "📊 RESULTS:"
echo "==========="
echo -e "Total tests: ${TOTAL}"
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"
echo -e "Success rate: $(( PASSED * 100 / TOTAL ))%"

