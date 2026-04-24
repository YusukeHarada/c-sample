/**
 * @file main.c
 * @brief Implementation of main functions
 *
 * This file contains the implementation of basic arithmetic operations
 * and the main program function for the c-sample project.
 */

#include <stdio.h>

/**
 * @brief Adds two integers
 *
 * @param a The first integer operand
 * @param b The second integer operand
 * @return The sum of a and b
 *
 * @note This function performs simple integer addition without overflow checking
 */
int add(int a, int b)
{
    return a + b;
}

/**
 * @brief Multiplies two integers
 *
 * @param a The first integer operand
 * @param b The second integer operand
 * @return The product of a and b
 *
 * @note This function performs simple integer multiplication without overflow checking
 */
int multiply(int a, int b)
{
    return a * b;
}

/**
 * @brief Main program execution
 *
 * Displays a greeting and demonstrates the arithmetic functions.
 * - Prints "Hello world!"
 * - Prints the result of add(2, 3)
 * - Prints the result of multiply(2, 3)
 */
void run_program()
{
    printf("Hello world!\n");
    printf("add(2, 3) = %d\n", add(2, 3));
    printf("multiply(2, 3) = %d\n", multiply(2, 3));
}

/**
 * @brief Application entry point
 *
 * Calls run_program() to execute the main program logic.
 *
 * @return 0 on successful execution
 */
#ifndef TESTING
int main()
{
    run_program();
    return 0;
}
#endif // TESTING