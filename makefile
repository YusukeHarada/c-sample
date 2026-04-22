CC = gcc
CXX = g++
CFLAGS = -Wall -Wextra
CXXFLAGS = -Wall -Wextra
TARGET = main
SRC = main.c
OUT_DIR = out
OBJ = $(OUT_DIR)/main.o

# Google test flags
GTEST_FLAGS = -lgtest -lgtest_main -pthread

# Coverage flags
COVERAGE_FLAGS = --coverage -fprofile-arcs -ftest-coverage

# Test targets
TEST_TARGET = test_main
TEST_SRC = test_main.cc

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJ)

$(OBJ): $(SRC)
	@mkdir -p $(OUT_DIR)
	$(CC) $(CFLAGS) -c $(SRC) -o $(OBJ)

# Build and run tests
test: $(OUT_DIR)/$(TEST_TARGET)
	./$(OUT_DIR)/$(TEST_TARGET)

$(OUT_DIR)/$(TEST_TARGET): $(OUT_DIR)/main_obj.o $(OUT_DIR)/main_test.o
	@mkdir -p $(OUT_DIR)
	$(CXX) $(CXXFLAGS) -o $(OUT_DIR)/$(TEST_TARGET) $(OUT_DIR)/main_obj.o $(OUT_DIR)/main_test.o $(GTEST_FLAGS)

$(OUT_DIR)/main_obj.o: $(SRC)
	@mkdir -p $(OUT_DIR)
	$(CC) $(CFLAGS) -c $(SRC) -o $(OUT_DIR)/main_obj.o

$(OUT_DIR)/main_test.o: $(TEST_SRC)
	@mkdir -p $(OUT_DIR)
	$(CXX) $(CXXFLAGS) -c $(TEST_SRC) -o $(OUT_DIR)/main_test.o

# Coverage measurement
coverage: CXXFLAGS += $(COVERAGE_FLAGS)
coverage: clean
	@mkdir -p $(OUT_DIR)
	@echo "Building with coverage instrumentation..."
	$(CXX) $(CXXFLAGS) -c $(SRC) -o $(OUT_DIR)/main_obj.o
	$(CXX) $(CXXFLAGS) -c $(TEST_SRC) -o $(OUT_DIR)/main_test.o
	$(CXX) $(CXXFLAGS) -o $(OUT_DIR)/$(TEST_TARGET) $(OUT_DIR)/main_obj.o $(OUT_DIR)/main_test.o $(GTEST_FLAGS)
	@echo "Running tests with coverage..."
	./$(OUT_DIR)/$(TEST_TARGET)
	@echo "Generating coverage report..."
	@mkdir -p $(OUT_DIR)/coverage
	gcov $(SRC) -o $(OUT_DIR)/ 2>/dev/null || true
	@echo ""
	@echo "C0 (Line) Coverage Report:"
	@echo "================================"
	@gcovr --filter=$(SRC) --print-summary 2>/dev/null || (echo "Note: gcovr not installed. Using gcov output:" && cat $(SRC:.c=.c.gcov) 2>/dev/null || echo "No coverage data available")

# HTML coverage report
coverage-html: coverage
	@echo "Generating HTML coverage report..."
	lcov --directory $(OUT_DIR) --capture --output-file $(OUT_DIR)/coverage/coverage.info 2>/dev/null || true
	lcov --remove $(OUT_DIR)/coverage/coverage.info '/usr/include/*' '/usr/local/*' --output-file $(OUT_DIR)/coverage/coverage_filtered.info 2>/dev/null || true
	genhtml $(OUT_DIR)/coverage/coverage_filtered.info --output-directory $(OUT_DIR)/coverage/html 2>/dev/null || echo "Note: genhtml not available. Install lcov for HTML reports."
	@echo "HTML report generated at: $(OUT_DIR)/coverage/html/index.html"

# Static code analysis
check:
	@echo "Running cppcheck..."
	cppcheck --enable=all --suppress=missingIncludeSystem $(SRC) main.h
	@echo "Checking with strict compiler warnings..."
	$(CC) -Wall -Wextra -Werror -c $(SRC) -o /tmp/check.o
	@echo "Static analysis completed successfully!"

clean:
	rm -rf $(OUT_DIR) $(TARGET)
	rm -f *.gcov *.gcda *.gcno

.PHONY: clean test check coverage coverage-html

