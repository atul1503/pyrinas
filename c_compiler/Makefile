CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -g
TARGET = pyrinas-compiler
SOURCES = main.c ast.c lexer.c parser.c semantic.c codegen.c

# Build the compiler
$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCES)

# Clean build artifacts
clean:
	rm -f $(TARGET) *.o

# Build the runtime
runtime:
	cd ../runtime && $(CC) -c pyrinas.c -o pyrinas.o

# Install (build both compiler and runtime)
install: runtime $(TARGET)
	@echo "Pyrinas C compiler built successfully!"
	@echo "Usage: ./$(TARGET) <pyrinas_file> [-o output_name]"

# Test with a simple example
test: $(TARGET) runtime
	@echo "Testing with hello.pyr..."
	./$(TARGET) ../examples/hello.pyr -o hello_test
	@echo "Running generated executable:"
	./hello_test
	@echo "Test completed!"

# Debug build
debug: CFLAGS += -DDEBUG -O0
debug: $(TARGET)

.PHONY: clean runtime install test debug