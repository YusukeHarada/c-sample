#include<stdio.h>

int add(int a, int b)
{
    return a + b;
}

int multiply(int a, int b)
{
    return a * b;
}

void run_program()
{
    printf("Hello world!\n");
    printf("add(2, 3) = %d\n", add(2, 3));
    printf("multiply(2, 3) = %d\n", multiply(2, 3));
}

int main()
{
    run_program();
    return 0;
}