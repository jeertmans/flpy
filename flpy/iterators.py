import functools
import itertools
import typing
import re

STR_FUNC_RE = re.compile(r"\|([^\|]*)\|(.*)")


def parse_func(func: typing.Union[typing.Callable, str]) -> typing.Callable:
    """
    Parse a function into a callable.
    Input argument can either be a callable or a string with Rust-like syntax.
    """
    if isinstance(func, str):
        match = STR_FUNC_RE.match(func)
        if match:
            f = f"lambda {match.group(1)}: {match.group(2)}"
            return eval(f)
        else:
            raise ValueError(
                f"Argument {func} could not be parsed into a valid function."
            )
    elif isinstance(func, typing.Callable):
        return func
    else:
        pass  # Raise some error


def takes_function(func):
    @functools.wraps(func)
    def wrapper(self, f_or_str, *args, **kwargs):
        f = parse_func(f_or_str)
        return func(self, f, *args, **kwargs)

    return wrapper


def returns_iterator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)

        # Avoids nesting iterators
        if isinstance(ret, Iterator):
            return ret
        else:
            return Iterator(ret)

    return wrapper


def returns_self(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        return self

    return wrapper


def empty_iterable():
    return list()


class Iterable(object):
    """
    An Iterable can wrap Python object that implements __iter__,
    and re-implements many builtin features with a functionnal programming approach.


    """

    __slots__ = "x"

    @classmethod
    def empty(cls):
        return empty_iterable()

    def __init__(self, x=empty_iterable()):
        self.x = x

    def __str__(self):
        return str(self.x)

    def __repr__(self):
        return f"ItA<{repr(self.x)}>"

    def __len__(self):
        return len(self.x)

    def iter(self):
        return iter(self.x)

    def __iter__(self):
        return self.iter()

    def __next__(self):
        return next(self.x)

    def set_value(self, x):
        self.x = x

    def unwrap(self):
        return self.x

    @returns_iterator
    @takes_function
    def map(self, f):
        return map(f, self.x)

    @returns_iterator
    @takes_function
    def filter(self, f):
        return filter(f, self.x)

    @returns_iterator
    def collect(self, collector=list):
        return collector(self.x)

    @returns_iterator
    @takes_function
    def filter_map(self, f):
        return filter(None, self.map(f))

    @returns_self
    @takes_function
    def for_each(self, f):
        for e in self.x:
            f(e)

    @returns_iterator
    def chain(self, *its):
        return chain(self, *its)

    @returns_iterator
    def slice(self, *args):
        return itertools.islice(self.x, *args)

    @returns_iterator
    def skip(self, n):
        return self.slice(n, None)

    @returns_iterator
    def take(self, n):
        return self.slice(n)

    @returns_iterator
    def every(self, n):
        return self.slice(None, None, n)

    @returns_iterator
    def repeat(self, times=None):
        return repeat(self.x, times=times)

    @returns_iterator
    def __getitem__(self, slc):
        try:
            return self.x[slc]
        except TypeError:
            if slc is Ellipsis:
                return self
            if isinstance(slc, slice):
                return self.slice(slc.start, slc.stop, slc.step)
            elif isinstance(slc, int):
                return self.skip(slc).take(1)
            else:
                raise TypeError

    def max(self):
        return max(self.x)

    def min(self):
        return min(self.x)

    def min_max(self):
        return self.min(), self.max()

    @returns_iterator
    @takes_function
    def reduce(self, f, *args, **kwargs):
        return functools.reduce(f, self.x, *args, **kwargs)

    @returns_iterator
    @takes_function
    def accumulate(self, f, *args, **kwargs):
        return functools.accumulate(f, self.x, *args, **kwargs)

    @returns_iterator
    def zip(self, *args):
        return zip(self.x, *args)

    @returns_iterator
    def zip_longest(self, *args):
        return itertools.zip_longest(self.x, *args)

    @returns_self
    def to(self, template, safe=True):
        template.set_value(self.x)

        if safe:
            self.set_value(empty_iterable())


def empty_iterator():
    yield from ()


class Iterator(Iterable):
    """
    A subclass of Iterable where the wrapped argument also implements __next__ method, thus providing additional possibilities.
    """

    @classmethod
    def empty(cls):
        empty_iterator()

    def __init__(self, x: typing.Iterator = empty_iterator()):
        super().__init__(x)

    def __repr__(self):
        return f"ItO<{repr(self.x)}>"

    def __next__(self):
        return next(self.x)


def It(x: typing.Any) -> typing.Union[Iterable, Iterator]:
    """
    Create an instance of Iterable or Iterator object depending on if the argument implements __next__ or not.
    """
    if isinstance(x, Iterator):
        return Iterator(x)
    else:
        try:
            iter(x)
            return Iterable(x)
        except AttributeError:
            raise TypeError(f"Argument {x} is not an Iterable")
