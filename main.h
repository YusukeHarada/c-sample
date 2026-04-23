/**
 * @file main.h
 * @brief Main header file for the c-sample project
 *
 * This file contains function declarations for basic arithmetic operations
 * and the main program function.
 *
 * @author Yusuke Harada
 * @version 1.0.0
 * @date 2026-04-23
 */

#ifndef MAIN_H
#define MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Adds two integers
 *
 * Performs addition of two input integers and returns the result.
 *
 * @param a The first integer operand
 * @param b The second integer operand
 * @return int The sum of a and b
 *
 * @example
 * @code
 * int result = add(2, 3); // result is 5
 * @endcode
 */
int add(int a, int b);

/**
 * @brief Multiplies two integers
 *
 * Performs multiplication of two input integers and returns the result.
 *
 * @param a The first integer operand
 * @param b The second integer operand
 * @return int The product of a and b
 *
 * @example
 * @code
 * int result = multiply(2, 3); // result is 6
 * @endcode
 */
int multiply(int a, int b);

/**
 * @brief Runs the main program
 *
 * Displays a greeting message and demonstrates the add and multiply functions.
 * Prints:
 * - "Hello world!"
 * - The result of add(2, 3)
 * - The result of multiply(2, 3)
 *
 * @return void
 */
void run_program();

#ifdef __cplusplus
}
#endif

#endif // MAIN_H
