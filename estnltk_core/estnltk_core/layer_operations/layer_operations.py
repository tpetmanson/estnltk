"""
Operations for Estnltk Layer object.

"""
from operator import eq

from estnltk_core.layer.layer import Layer

# TODO: rename module

def diff_layer(a: Layer, b: Layer, comp=eq):
    """Generator of layer differences.

    Parameters
    ----------
    a: Layer
    b: Layer
    comp: compare function, default: operator.eq
        Function that returns True if layer elements are equal and False otherwise.
        Only layer elements with equal spans are compared.

    Yields
    ------
    tuple(Span)
        Pairs of different spans. In place of missing layer element,
        None is returned.
    """
    a = iter(a)
    b = iter(b)
    a_end = False
    b_end = False
    try:
        x = next(a)
    except StopIteration:
        a_end = True
    try:
        y = next(b)
    except StopIteration:
        b_end = True

    while not a_end and not b_end:
        if x < y:
            yield (x, None)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            continue
        if x.base_span == y.base_span:
            if not comp(x, y):
                yield (x, y)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            try:
                y = next(b)
            except StopIteration:
                b_end = True
            continue
        yield (None, y)
        try:
            y = next(b)
        except StopIteration:
            b_end = True

    if a_end and b_end:
        return

    if a_end:
        yield (None, y)
        yield from ((None, y) for y in b)

    if b_end:
        yield (x, None)
        yield from ((x, None) for x in a)

