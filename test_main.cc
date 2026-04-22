#include <gtest/gtest.h>
#include <cstdio>
#include <cstdlib>

extern "C" {
    #include "main.h"
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

// run_program関数のテスト
TEST(ProgramTest, RunProgram)
{
    // run_program関数が正常に実行できることを確認
    // （通常は標準出力が表示される）
    run_program();
    SUCCEED();  // テストが正常に実行されたことを確認
}

