#!/usr/bin/env python3
import ctypes, os, platform, math
from ctypes import c_double, c_int, c_ulonglong

system = platform.system()
if system == "Linux":
    lib_name = "libmathlib.so"
elif system == "Darwin":
    lib_name = "libmathlib.dylib"
elif system == "Windows":
    lib_name = "mathlib.dll"
else:
    raise RuntimeError("Unsupported OS: " + system)

lib_path = os.path.join(os.path.dirname(__file__), lib_name)
if not os.path.exists(lib_path):
    if os.path.exists(lib_name):
        lib_path = lib_name
    else:
        raise FileNotFoundError(f"Shared library not found: {lib_path}")

mathlib = ctypes.CDLL(lib_path)

mathlib.add_double.argtypes = (c_double, c_double); mathlib.add_double.restype = c_double
mathlib.sub_double.argtypes = (c_double, c_double); mathlib.sub_double.restype = c_double
mathlib.mul_double.argtypes = (c_double, c_double); mathlib.mul_double.restype = c_double
mathlib.div_double.argtypes = (c_double, c_double); mathlib.div_double.restype = c_double
mathlib.pow_double.argtypes = (c_double, c_double); mathlib.pow_double.restype = c_double
mathlib.factorial_int.argtypes = (c_int,); mathlib.factorial_int.restype = c_ulonglong

def safe_div(a,b):
    res = mathlib.div_double(a,b)
    return res if math.isfinite(res) else float('inf')

def main():
    print("Using native library:", lib_path)
    a,b = 10.5, 2.0
    print("add_double:", mathlib.add_double(a,b))
    print("sub_double:", mathlib.sub_double(a,b))
    print("mul_double:", mathlib.mul_double(a,b))
    print("div_double:", safe_div(a,b))
    print("div_double by zero:", safe_div(a,0.0))
    print("pow_double:", mathlib.pow_double(a,b))
    for n in (0,1,5,10,20):
        print(f"factorial_int({n}) =", mathlib.factorial_int(n))

if __name__ == '__main__':
    main()
