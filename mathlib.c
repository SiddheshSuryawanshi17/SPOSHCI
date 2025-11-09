#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

#if defined(_WIN32) || defined(_WIN64)
  #define EXPORT __declspec(dllexport)
#else
  #define EXPORT
#endif

EXPORT double add_double(double a, double b) { return a + b; }
EXPORT double sub_double(double a, double b) { return a - b; }
EXPORT double mul_double(double a, double b) { return a * b; }
EXPORT double div_double(double a, double b) { if (b == 0.0) return HUGE_VAL; return a / b; }
EXPORT double pow_double(double a, double b) { return pow(a,b); }
EXPORT unsigned long long factorial_int(int n) {
    if (n < 0) return 0;
    unsigned long long res = 1ULL;
    for (int i = 2; i <= n; ++i) res *= (unsigned long long)i;
    return res;
}
