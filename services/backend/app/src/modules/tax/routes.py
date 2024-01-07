from typing import Dict
import time

from fastapi import APIRouter, status

from src.config import DATABASE_URL
from src.logging.service import logger
from src.versions import ApiVersion
from rst_tax_calculator import sum_as_string, fib, is_prime, pgtc
from numba import njit


router = APIRouter(
    tags=['Rust Tax Calculator'],
)

def pyfib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def py_is_prime(n) -> int:
    if n <= 1:
        return 0
    for i in range(2, n):
        if n % i == 0:
            return 0
    return 1


@njit()
def nbfib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@njit()
def nb_is_prime(n) -> int:
    if n <= 1:
        return 0
    for i in range(2, n):
        if n % i == 0:
            return 0
    return 1


@router.get(
    '/rst_tax_calculator/dbtest',
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary='Test Rust Db endpoint',
    description='Endpoint description. Will use the docstring if not provided.',
)
async def dbtest() -> Dict:
    start = time.monotonic()
    res = pgtc(DATABASE_URL)
    return {
        'message': 'DB test complete.',
        'result': res,
        'duration': time.monotonic() - start,
    }

@router.get(
    '/rst_tax_calculator/sum',
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary='Test Rust Calc endpoint',
    description='Endpoint description. Will use the docstring if not provided.',
)
async def sum(a: int, b: int) -> Dict:
    n = 109000601

    # Time rust fib
    start = time.monotonic()
    rf = is_prime(n)
    rtime = time.monotonic() - start
    print(f'fib(35) took {rtime} seconds to produce {rf}')

    # Time numba fib
    nbfib(2)    # Compile
    start = time.monotonic()
    nbf = nb_is_prime(n)
    nbtime = time.monotonic() - start
    print(f'nbfib(35) took {nbtime} seconds to produce {nbf}')

    # Time pyfib
    start = time.monotonic()
    pf = py_is_prime(n)
    ptime = time.monotonic() - start
    print(f'pyfib(35) took {ptime} seconds to produce {pf}')

    # pgtc()
    assert pf == nbf == rf

    return {
        'message': 'Sandbox tasks enqueued.',
        'result': sum_as_string(a, b),
        'fib': nbf,
        'rust time': rtime,
        'nb time': nbtime,
        'py fime': ptime,
        'rust speedup': f"{ptime / rtime}x",
        'numba speedup': f"{ptime / nbtime}x",
    }

    # n = 80

    # # Time pyfib
    # start = time.monotonic()
    # pf = pyfib(n)
    # ptime = time.monotonic() - start
    # print(f'pyfib(35) took {ptime} seconds to produce {pf}')

    # # Time numba fib
    # nbfib(2)    # Compile
    # start = time.monotonic()
    # nbf = nbfib(n)
    # nbtime = time.monotonic() - start
    # print(f'nbfib(35) took {nbtime} seconds to produce {nbf}')

    # # Time rust fib
    # start = time.monotonic()
    # rf = fib(n)
    # # rf = pf
    # rtime = time.monotonic() - start
    # print(f'fib(35) took {rtime} seconds to produce {rf}')

    # # pgtc()
    # assert pf == nbf == rf

    # return {
    #     'message': 'Sandbox tasks enqueued.',
    #     'result': sum_as_string(a, b),
    #     'fib': nbf,
    #     'rust time': rtime,
    #     'py fime': ptime,
    #     'nb time': nbtime,
    #     'rust speedup': f"{ptime / rtime}x",
    #     'numba speedup': f"{ptime / nbtime}x",
    # }
