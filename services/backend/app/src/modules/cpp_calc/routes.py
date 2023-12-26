import time
from typing import Dict
import ctypes
import pathlib

from fastapi import APIRouter, status
from numba import njit

from src.config import APP_SRC_FOLDER_ABS
from src.logging.service import logger
from src.versions import ApiVersion

# Load the shared library into ctypes
# (cd services/backend/app/src/modules/cpp_calc && ./build.sh)
libpath = pathlib.Path(APP_SRC_FOLDER_ABS) / "modules" / "cpp_calc" / 'libccalc.so'
c_lib = ctypes.CDLL(libpath)

# Calc function
c_lib.calc.restype = ctypes.c_float
c_lib.calc.argtypes = [ctypes.c_int, ctypes.c_float]

# Fib function
c_lib.fib.restype = ctypes.c_longlong
c_lib.fib.argtypes = [ctypes.c_longlong]


def pyfib(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    return pyfib(n - 1) + pyfib(n - 2)


@njit(fastmath=True, cache=True)
def nbfib(n: int):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    return nbfib(n - 1) + nbfib(n - 2)


router = APIRouter(
    tags=['CppCalc'],
)

@router.get(
    '/cpp_calc/calc',
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary='Test C++',
    description='Endpoint description. Will use the docstring if not provided.',
)
async def cpp_calc() -> Dict:
    # x, y = 6, 2.3
    # answer = c_lib.calc(x, ctypes.c_float(y))
    # answer = c_lib.calc(x, y)

    n = 35

    start = time.monotonic()
    answer = c_lib.fib(n)
    ctime = time.monotonic() - start

    start = time.monotonic()
    pyfib(n)
    pytime = time.monotonic() - start

    nbfib(5)    # Compile the function
    start = time.monotonic()
    nbfib(n)
    nbtime = time.monotonic() - start

    return {
        'message': 'Sandbox tasks enqueued.',
        # 'res': answer,
        'answer': answer,
        'ctime': ctime,
        'pytime': pytime,
        'nbtime': nbtime,
        'cspeedup': pytime / ctime,
        'nbspeedup': pytime / nbtime,
    }
