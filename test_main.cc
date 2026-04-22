#include <gtest/gtest.h>
#include <cstdio>
#include <cstdlib>
#include <unistd.h>
#include <sys/wait.h>

extern "C" {
    int add(int a, int b);
    int multiply(int a, int b);
    void run_program();
}

// add関数のテスト
TEST(AddTest, PositiveNumbers)
{
    EXPECT_EQ(add(2, 3), 5);
}

TEST(AddTest, NegativeNumbers)
{
    EXPECT_EQ(add(-2, -3), -5);
}

TEST(AddTest, MixedNumbers)
{
    EXPECT_EQ(add(5, -3), 2);
}

TEST(AddTest, Zero)
{
    EXPECT_EQ(add(0, 0), 0);
}

// multiply関数のテスト
TEST(MultiplyTest, PositiveNumbers)
{
    EXPECT_EQ(multiply(2, 3), 6);
}

TEST(MultiplyTest, Zero)
{
    EXPECT_EQ(multiply(5, 0), 0);
}

TEST(MultiplyTest, NegativeNumbers)
{
    EXPECT_EQ(multiply(-2, 3), -6);
}

TEST(MultiplyTest, One)
{
    EXPECT_EQ(multiply(5, 1), 5);
}

// run_program関数のテスト（標準出力のキャプチャ）
TEST(ProgramTest, RunProgram)
{
    // Redirect stdout to capture output
    fflush(stdout);
    int old_stdout = dup(STDOUT_FILENO);
    
    int pipefd[2];
    pipe(pipefd);
    dup2(pipefd[1], STDOUT_FILENO);
    close(pipefd[1]);
    
    // Run the program
    run_program();
    fflush(stdout);
    
    // Restore stdout
    dup2(old_stdout, STDOUT_FILENO);
    close(old_stdout);
    
    // Read captured output
    char buffer[256] = {0};
    read(pipefd[0], buffer, sizeof(buffer) - 1);
    close(pipefd[0]);
    
    // Verify output contains expected strings
    std::string output(buffer);
    EXPECT_TRUE(output.find("Hello world!") != std::string::npos);
    EXPECT_TRUE(output.find("add(2, 3) = 5") != std::string::npos);
    EXPECT_TRUE(output.find("multiply(2, 3) = 6") != std::string::npos);
}

int main(int argc, char **argv)
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
