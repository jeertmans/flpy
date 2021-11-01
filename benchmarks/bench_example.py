from flpy import It
from timeit import timeit
from functools import wraps

benches = []


def register(bench):
    benches.append(bench)

    @wraps(bench)
    def wrapper(*args, **kwargs):
        return bench(*args, **kwargs)

    return wrapper


@register
def bench_flpy(n):
    x = range(n)
    y = It(x).map("|v| v * v").filter("|v| v % 3 == 0").skip(n // 2).collect()
    return y


@register
def bench_flpy_lambdas(n):
    x = range(n)
    y = It(x).map(lambda v: v * v).filter(lambda v: v % 3 == 0).skip(n // 2).collect()
    return y


@register
def bench_python(n):
    x = range(n)
    y = map(lambda v: v * v, x)
    y = filter(lambda v: v % 3 == 0, y)
    for i in range(n // 2):
        next(y, None)
    return list(y)


@register
def bench_python_comp(n):
    x = range(n)
    seq = (y for y in (v * v for v in x) if y % 3 == 0)
    for i in range(n // 2):
        next(seq, None)
    return list(seq)


def main():
    n = 1000
    k = 10000
    for func in benches:
        t = timeit(lambda: func(n), number=k)
        print(f"Bench {func} took {t} seconds.")


if __name__ == "__main__":
    main()
