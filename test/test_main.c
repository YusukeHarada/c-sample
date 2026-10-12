/**
 * @file test_main.c
 * @brief main.c の単体テスト（Unity / Ceedling 版）
 *
 * Google Test 版（test_main.cc）と同じ観点を Unity で書いたもの。
 * 実行: ceedling test:all（カバレッジ付きは ceedling gcov:all）
 *
 * 依存先がある関数をテストする場合は、ヘッダを mock_xxx.h として include すると
 * CMock がモックを自動生成する（例: #include "mock_adc.h" → adc_read_ExpectAndReturn()）。
 */
#include "unity.h"
#include "main.h"

void setUp(void)
{
}

void tearDown(void)
{
}

/* add() */
void test_add_positive_numbers(void)
{
    TEST_ASSERT_EQUAL_INT(5, add(2, 3));
}

void test_add_negative_numbers(void)
{
    TEST_ASSERT_EQUAL_INT(-5, add(-2, -3));
}

void test_add_mixed_numbers(void)
{
    TEST_ASSERT_EQUAL_INT(2, add(5, -3));
}

void test_add_zero(void)
{
    TEST_ASSERT_EQUAL_INT(0, add(0, 0));
}

/* multiply() */
void test_multiply_positive_numbers(void)
{
    TEST_ASSERT_EQUAL_INT(6, multiply(2, 3));
}

void test_multiply_zero(void)
{
    TEST_ASSERT_EQUAL_INT(0, multiply(5, 0));
}

void test_multiply_negative_numbers(void)
{
    TEST_ASSERT_EQUAL_INT(-6, multiply(-2, 3));
}

void test_multiply_one(void)
{
    TEST_ASSERT_EQUAL_INT(5, multiply(5, 1));
}

/* run_program() は標準出力に書くだけなので、例外なく終了することだけ確認する */
void test_run_program_completes(void)
{
    run_program();
    TEST_PASS();
}
