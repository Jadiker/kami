import time
from contextlib import contextmanager

@contextmanager
def timing(l: list[float] | None = None):
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    if l is None:
        print(f"Elapsed time: {end - start:.6f} seconds")
    else:
        l.append(end - start)