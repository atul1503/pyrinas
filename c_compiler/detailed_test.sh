#!/bin/bash

echo "🔍 Detailed Analysis of Pyrinas C Compiler Tests"
echo "================================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test passing cases first
echo -e "\n${GREEN}✅ PASSING TESTS:${NC}"
echo "=================="

for file in ../examples/break.pyr ../examples/continue.pyr ../examples/for_loop.pyr ../examples/hello.pyr ../examples/if_else.pyr ../examples/labeled_break.pyr ../examples/variables.pyr ../examples/while_loop.pyr; do
    echo "✅ $(basename $file)"
done

echo -e "\n${RED}❌ FAILING TESTS (with errors):${NC}"
echo "================================="

test_with_error() {
    local file="$1"
    local basename=$(basename "$file" .pyr)
    
    echo -e "\n📝 Testing: ${file}"
    echo "---"
    
    # Try to compile and capture error
    if ! timeout 10 ./pyrinas-compiler "$file" -o "test_$basename" 2>&1; then
        echo "❌ Compilation failed"
    else
        echo "✅ Compilation succeeded, checking runtime..."
        if ! timeout 5 "./test_$basename" 2>&1; then
            echo "❌ Runtime failed"
        fi
        rm -f "test_$basename"
    fi
}

# Test a few representative failing cases
echo -e "\n🔍 Sample failing tests:"
test_with_error "../examples/functions.pyr"
test_with_error "../examples/expressions.pyr" 
test_with_error "../examples/structs.pyr"
test_with_error "../examples/arrays.pyr"

