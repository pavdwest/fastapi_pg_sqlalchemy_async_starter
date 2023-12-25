// calc.cpp
float calc(int int_param, float float_param) {
    float return_value = int_param * float_param;
    return return_value;
}

int fib(long long n) {
    if (n <= 0)
        return 0;
    else if (n == 1){
        return 1;
    }
    return fib(n - 1) + fib(n - 2);
}
