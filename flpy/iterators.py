import functools
import itertools
import typing
import re

STR_FUNC_RE = re.compile(r"\|([^\|]*)\|(.*)")


Function = typing.Union[typing.Callable, str, None]


def parse_func(func: Function) -> typing.Optional[typing.Callable]:
    """
    Parse a function into a callable.
    Input argument can either be a callable or a string with Rust-like syntax.

    Rust-like syntax assumes arguments are enclosed between | and are separated by commas: \|arg1, arg2, ..., argn\|.

    :Example:

    >>> from flpy.iterators import parse_func
    >>> f = parse_func(lambda x, y: x * y)
    >>> f(4, 5)
    20
    >>> f = parse_func('|x, y| x * y')
    >>> f(4, 5)
    20
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
    else:
        return func


def takes_function(func: typing.Callable) -> typing.Callable:
    """
    Wrapper around class method that takes a function or string as first argument that parses it using :py:func:`parse_func`.

    :param func: a function
    :return: a function
    """

    @functools.wraps(func)
    def wrapper(self, f_or_str, *args, **kwargs):
        f = parse_func(f_or_str)
        return func(self, f, *args, **kwargs)

    return wrapper


def empty_iterable() -> typing.Iterable:
    """
    Return an empty iterable, i.e., an empty list.

    :return: an iterable
    """
    return list()


class Iterable(object):
    """
    An Iterable can wrap Python object that implements :py:func:`iter`,
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

    def iter(self) -> "Iterator":
        """
        Return an iterator version of current object.

        :return: an Iterator

        :Example:

        >>> from flpy import It
        >>> it = It([1, 2, 3])
        >>> next(it.iter())
        1
        """
        return Iterator(iter(self.x))

    def __iter__(self):
        return self.iter()

    def set_value(self, x: typing.Iterable) -> "Iterable":
        """
        Change the content of current Iterable to be `x`.

        :param: an Iterable
        :return: self

        :Example:

        >>> from flpy import It
        >>> x = It([1, 2, 3])
        >>> x.set_value([4, 5, 6])
        ItA<[4, 5, 6]>
        """
        self.x = x

    def unwrap(self) -> typing.Iterable:
        """
        Return the iterable object hold by current Iterable instance.

        :return: an iterable
        """
        return self.x

    @takes_function
    def map(self, f) -> "Iterator":
        """
        Apply built-in :py:func:`.map` on current object.

        :param f: a :py:func:`parse_func` compatible function
        :return: an Iterator

        :Examples:

        >>> from flpy import It
        >>> It([1, 2, 3]).map('|x| x * x').collect()
        ItA<[1, 4, 9]>
        """
        return Iterator(map(f, self.x))

    @takes_function
    def filter(self, f) -> "Iterator":
        """
        Apply built-in :py:func:`.filter` on current object.

        :param f: a :py:func:`parse_func` compatible function
        :return: an Iterator

        :Examples:

        >>> from flpy import It
        >>> It([1, 2, 3]).filter('|x| x > 1').collect()
        ItA<[2, 3]>
        """
        return Iterator(filter(f, self.x))

    @takes_function
    def collect(self, collector: typing.Callable = list) -> "Iterable":
        """
        Collect the current Iterable into a new Iterable using `collector` function.
        By default, it will transform the content into a list.

        :param f: a :py:func:`parse_func` compatible function
        :return: an Iterable
        """
        return Iterable(collector(self.x))

    @takes_function
    def filter_map(self, f: Function) -> "Iterator":
        """
        Chain :py:meth:`Iterable.map` and :py:meth:`Iterable.filter` to only return non-None results.

        :param f: a :py:func:`parse_func` compatible function
        :return: an Iterator

        """
        return self.map(f).filter(None)

    @takes_function
    def for_each(self, f: Function) -> "Iteratable":
        """
        Apply a function on each element and return self.

        :param f: a :py:func:`parse_func` compatible function
        :return: self

        :Example:

        >>> from flpy import It
        >>> it = It([1, 2, 3]).for_each('|v| print(v)')
        1
        2
        3
        >>> it
        It<A>[1, 2, 3]>
        """
        for e in self.x:
            f(e)

        return self

    def chain(self, *its) -> "Iterator":
        """
        Chain current object with any number of objects that implements :py:func:`iter` using :py:func:`itertools.chain`.

        :param its: see :py:func:`itertools.chain` arguments
        :return: an Iterator

        :Example:

        >>> from flpy import It
        >>> It([1, 2, 3]).chain([4, 5, 6]).collect()
        ItA<[1, 2, 3, 4, 5, 6]>
        """
        return Iterator(itertools.chain(self, *its))

    def slice(self, *args: typing.Optional[int]) -> "Iterator":
        """
        Return a slice of current iterable using :py:func:`functools.islice`.

        :param args: see :py:func:`functools.islice` arguments
        :return: an Iterator
        """
        return Iterator(itertools.islice(self.x, *args))

    def skip(self, n: int) -> "Iterator":
        """
        Return current iterator, but with first `n` items are skipped.

        :param n: the number of items to skip
        :return: an Iterator
        """
        return self.slice(n, None)

    def take(self, n: int) -> "Iterator":
        """
        Return current iterator, but with max `n` items are kept.

        :param n: the number of items to keep
        :return: an Iterator
        """
        return self.slice(n)

    def every(self, n: int):
        """
        Return current iterator, but one 1 item every `n` is kept.

        :param n: the spacing between two items
        :return: an Iterator
        """
        return self.slice(None, None, n)

    def repeat(self, times: int = None) -> "Iterator":
        """
        Return current iterator, repeated `n` times.
        If `n` is None, the repetition is infinite.

        :param n: the number of repetitions
        :return: an Iterator
        """
        return Iterator(itertools.repeat(self.x, times=times))

    def __getitem__(self, slc):
        try:
            return It(self.x[slc])
        except TypeError:
            if slc is Ellipsis:
                return self
            if isinstance(slc, slice):
                return self.slice(slc.start, slc.stop, slc.step)
            elif isinstance(slc, int):
                return self.skip(slc).take(1)
            else:
                raise TypeError

    def max(self) -> typing.Any:
        """
        Apply built-in :py:func:`.max` on current object.

        :return: the maximum

        :Examples:

        >>> from flpy import It
        >>> It([1, 2, 3]).max()
        3
        """
        return max(self.x)

    def min(self) -> typing.Any:
        """
        Apply built-in :py:func:`.min` on current object.

        :return: the minimum

        :Examples:

        >>> from flpy import It
        >>> It([1, 2, 3]).min()
        1
        """
        return min(self.x)

    def min_max(self) -> typing.Tuple[typing.Any, typing.Any]:
        """
        Apply both :py:func:`min` and :py:func:`ax` on current object.

        :return: the minimum and the maximum

        :Examples:

        >>> from flpy import It
        >>> It([1, 2, 3]).min_max()
        (1, 3)
        """
        return self.min(), self.max()

    @takes_function
    def reduce(self, f, *args, **kwargs) -> typing.Any:
        """
        Apply built-in :py:func:`functools.reduce` on current object.

        :param f: a :py:func:`parse_func` compatible function
        :return: the reduction result
        """
        return functools.reduce(f, self.x, *args, **kwargs)

    @takes_function
    def accumulate(self, f) -> "Iterator":
        """
        Apply built-in :py:func:`functools.accumulate` on current object.

        :param f: a :py:func:`parse_func` compatible function
        :return: an Iterator
        """
        return Iterator(itertools.accumulate(f, self.x))

    def zip(self, *args) -> "Iterator":
        """
        Apply built-in :py:func:`.zip` on current object.

        :param args: see :py:func:`.zip` arguments
        :return: an Iterator
        """
        return Iterator(zip(self.x, *args))

    def zip_longest(self, *args):
        """
        Apply built-in :py:func:`itertools.zip_longest` on current object.

        :param args: see :py:func:`itertools.zip_longest` arguments
        :return: an Iterator
        """
        return Iterator(itertools.zip_longest(self.x, *args))

    def to(self, iterable: "Iterable", safe: bool = True) -> "Iterable":
        """
        Move current iterable value into argument object.
        By default (if `safe`), the content of self will be set to an empty value, to avoid two Iterable objects sharing the same content.

        :param iterable: target iterable
        :param safe: if safe, set content of self to an empty Iterable
        :return: self
        """
        iterable.set_value(self.x)

        if safe:
            self.set_value(empty_iterable())

        return self


def empty_iterator() -> typing.Iterator:
    """
    Return an empty iterator.

    :return: an iterator

    :Example:

    >>> from flpy.iterators import empty_iterator, It
    >>> It(empty_iterator()).collect()
    ItA<[]>
    """
    yield from ()


class Iterator(Iterable):
    """
    A subclass of Iterable where the wrapped argument also implements :py:func:`next` method, thus providing additional possibilities.
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
    Create an instance of Iterable or Iterator object depending on if the argument implements :py:func:`next` or not.
    """
    if isinstance(x, Iterator):
        return Iterator(x)
    else:
        try:
            iter(x)
            return Iterable(x)
        except AttributeError:
            raise TypeError(f"Argument {x} is not an Iterable")
