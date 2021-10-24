# Functional, but Lazy Python

With **FLPy**, improve the readibility of your programs by leveraging functional programming.

### Installation
**FLPY** has no external dependencies, and can be installed using `pip`:
```
pip install flpy
```

### Examples

Given an input sequence `x`, print all, but the first, squared values that are divisible by 3 and collect the result into a list.
```python

>>> x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Input sequence

# Usual way

>>> squares = map(lambda v: v * v, x)
>>> squares_div_by_3 = filter(lambda v: v % 3 == 0, squares)
>>> y = list(squares_div_by_3)[1:]  # We skip one value
>>> for v in y:
...     print(v)
36
81
>>> y
[36, 81]

# FLPy way

>>> from flpy import It

>>> y = (
...     It(x)
...     .map('|v| v * v')  # You can also use lambda or any other Callable
...     .filter('|v| v % 3 == 0')
...     .skip(1)
...     .collect()  # Collects the iterator into a list
...     .for_each('|v| print(v)')  # Yet it still returns the list to `y`
... )
36
81
>>> y
ItO<[36, 81]>
```