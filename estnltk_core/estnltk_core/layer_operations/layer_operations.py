"""
Operations for Estnltk Layer object.

"""
from typing import Container
from operator import eq

from collections import Counter, defaultdict

from estnltk_core.layer.layer import Layer


def apply_filter(layer: Layer, function: callable, preserve_spans: bool = False, drop_immediately: bool = False):
    if drop_immediately:
        i = 0
        while i < len(layer):
            j = 0
            while j < len(layer[i].annotations):
                if preserve_spans and len(layer[i].annotations) == 1:
                    break
                if function(layer, i, j):
                    j += 1
                    continue
                if len(layer[i].annotations) == 1:
                    del layer[i].annotations[j]
                    i -= 1
                    break
                else:
                    del layer[i].annotations[j]
            i += 1
    else:
        to_remove = []
        for i, span in enumerate(layer):
            for j, annotation in enumerate(span.annotations):
                if not function(layer, i, j):
                    to_remove.append((i, j))
        for i, j in reversed(to_remove):
            if not preserve_spans or len(layer[i].annotations) > 1:
                del layer[i].annotations[j]


def drop_annotations(layer: Layer, attribute: str, values: Container, preserve_spans=False):
    to_remove = []

    for i, span in enumerate(layer):
        for j, annotation in enumerate(span.annotations):
            if getattr(annotation, attribute) in values:
                to_remove.append((i, j))
    for i, j in reversed(to_remove):
        if not preserve_spans or len(layer[i].annotations) > 1:
            del layer[i].annotations[j]


def keep_annotations(layer: Layer, attribute: str, values: Container, preserve_spans=False):
    to_remove = []

    for i, span in enumerate(layer):
        for j, annotation in enumerate(span.annotations):
            if getattr(annotation, attribute) not in values:
                to_remove.append((i, j))
    for i, j in reversed(to_remove):
        if not preserve_spans or len(layer[i].annotations) > 1:
            del layer[i].annotations[j]


def apply_to_annotations(layer: Layer, function: callable):
    for span in layer:
        for annotation in span:
            function(annotation)


def apply_to_spans(layer: Layer, function: callable):
    for span in layer:
        function(span)


def unique_texts(layer: Layer, order=None):
    """Retrive unique texts of layer optionally ordered.

    Parameters
    ----------
    layer: Text Layer
    order: {None, 'asc', 'desc'} (default: None)
        If 'asc', then the texts are returned in ascending order by unicode lowercase.
        If 'desc', then the texts are returned in descending order by unicode lowercase.
        The ordering is nondeterministic if the lowercase versions of words are equal. 
        For example the list ['On', 'on'] is both in ascending and descending order. 
        Else, the texts returned have no particular order.

    Returns
    -------
    list of str
        List of unique texts of given layer.
    """
    texts = layer.text
    if order == None:
        return list(set(texts))
    if order == 'asc':
        return sorted(set(texts), reverse=False, key=str.lower)
    if order == 'desc':
        return sorted(set(texts), reverse=True, key=str.lower)
    raise ValueError('Incorrect order type.')


def count_by(layer: Layer, attributes, counter=None):
    """Create table of counts for every *layer* *attributes* value combination.
    
    Parameters
    ----------
    layer: Layer
        The layer which elements have the keys listed in *attributes*.
    attributes: list of str or str
        Name of *layer*'s key or list of *layer*'s key names.
        If *attributes* contains 'text', then the *layer*'s text is found using spans.
    table: collections.Counter, None, default: None
        If table==None, then new 
        If table!=None, then the table is updated and returned.
    
    Returns
    -------
    collections.Counter
        The keys are tuples of values of attributes. 
        The values are corresponding counts.
    """
    if isinstance(attributes, str):
        attributes = [attributes]

    if counter is None:
        counter = Counter()

    for span in layer:
        key = []
        for a in attributes:
            if a == 'text':
                key.append(span.text)
            else:
                for annotation in span.annotations:
                    key.append(getattr(annotation, a))
        key = tuple(key)
        counter[key] += 1

    return counter


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


def get_enclosing_spans(layer: Layer, span):
    base_span = span.base_span
    end = span.end
    for sp in layer:
        if base_span in sp.base_span:
            yield sp
        if end < sp.start:
            break

