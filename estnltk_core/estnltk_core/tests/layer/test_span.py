import pytest
import re

from estnltk_core.layer.base_layer import BaseLayer
from estnltk_core import ElementaryBaseSpan, EnvelopingBaseSpan
from estnltk_core import Span, Annotation
from estnltk_core.layer import AttributeList

from estnltk_core.common import load_text_class

def test_add_annotation():
    span_1 = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))

    span_1.add_annotation(Annotation(span_1, attr_1=0))
    span_1.add_annotation(Annotation(span_1, attr_1=3))
    span_1.add_annotation(Annotation(span_1, attr_1=3))

    assert len(span_1.annotations) == 2

    span_2 = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))

    span_2.add_annotation(Annotation(span_2, attr_1=3))
    span_2.add_annotation(Annotation(span_2, attr_1=0))
    span_2.add_annotation(Annotation(span_2, attr_1=0))
    span_2.add_annotation(Annotation(span_2, attr_1=0))

    assert span_1 == span_2


def test_getattr():
    span_1 = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))

    span_1.add_annotation(Annotation(span_1, attr_1=0))
    span_1.add_annotation(Annotation(span_1, attr_1=3))

    assert span_1.attr_1 == AttributeList([0, 3], 'attr_1')

    with pytest.raises(AttributeError):
        span_1.__getstate__
    with pytest.raises(AttributeError):
        span_1.__setstate__
    with pytest.raises(AttributeError):
        span_1._ipython_canary_method_should_not_exist_
    with pytest.raises(AttributeError):
        span_1.blabla

    assert hasattr(span_1, 'attr_1')
    assert not hasattr(span_1, 'blabla')


def test_getitem():
    span_1 = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))

    span_1.add_annotation(Annotation(span_1, attr_1=0))
    span_1.add_annotation(Annotation(span_1, attr_1=3))

    assert isinstance(span_1.annotations[0], Annotation)
    assert span_1.annotations[0].attr_1 == 0
    assert span_1.annotations[1].attr_1 == 3

    assert span_1['attr_1'] == AttributeList([0, 3], 'attr_1')

    with pytest.raises(KeyError):
        span_1[:]

    with pytest.raises(KeyError):
        span_1['bla']

    with pytest.raises(KeyError):
        span_1[0]


def test_base_spans():
    span_1 = Span(ElementaryBaseSpan(0, 1), layer=BaseLayer('test', attributes=['attr_1'], ambiguous=True))

    assert ElementaryBaseSpan(0, 1) == span_1.base_span


def test_text_properties_and_text_object():
    # Tests from:
    #   https://github.com/estnltk/estnltk/blob/5bacff50072f9415814aee4f369c28db0e8d7789/estnltk/tests/test_layer/span/test_properties.py#L59-L142
    
    # Span with elementary base span and no layer
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)
    assert span.text is None
    assert span.enclosing_text is None
    assert span.text_object is None

    # Span with enveloping base span and no layer
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(8, 12)])
    span = Span(base_span=base_span, layer=None)
    assert span.text is None
    assert span.enclosing_text is None
    assert span.text_object is None

    # Span with elementary base span and no text object
    layer = BaseLayer('test_layer')
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    assert span.text is None
    assert span.enclosing_text is None
    assert span.text_object is None

    # Span with enveloping base span and no text object
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(8, 12)])
    span = Span(base_span=base_span, layer=layer)
    assert span.text is None
    assert span.enclosing_text is None
    assert span.text_object is None

    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # Valid span with elementary base span that is attached to text
    text = Text('0123456789abcdef')
    layer = BaseLayer('test_layer', text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    assert span.text == '0123'
    assert span.enclosing_text == '0123'
    assert span.text_object is text

    # Valid span with enveloping base span that is attached to text
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(8, 12)])
    span = Span(base_span=base_span, layer=layer)
    assert span.text == ['0123', '89ab']
    assert span.enclosing_text == '0123456789ab'
    assert span.text_object is text

    # Valid span with enveloping base span that is attached to text and is continuous
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(4, 8), ElementaryBaseSpan(8, 12)])
    span = Span(base_span=base_span, layer=layer)
    assert span.text == ['0123', '4567', '89ab']
    assert span.enclosing_text == '0123456789ab'
    assert span.text_object is text

    # Invalid span with elementary base span that is attached to text
    # We cannot check whether span is valid during its creation as text might be unreachable.
    # Thus natural truncation is the only sane solution to the problem.
    text = Text('01')
    layer = BaseLayer('test_layer', text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    assert span.text == '01'
    assert span.enclosing_text == '01'
    assert span.text_object is text
    # Invalid span that is completely outside of text
    # The outcome is an empty string
    span = Span(base_span=ElementaryBaseSpan(3, 8), layer=layer)
    assert span.text == ''
    assert span.enclosing_text == ''
    assert span.text_object is text

    # Invalid span with enveloping base span that is attached to text
    # Natural truncation is the only sane solution to the problem.
    # We do not omit empty texts to preserve the number of leafs
    text = Text('0123456789a')
    layer = BaseLayer('test_layer', text_object=text)
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(8, 12)])
    span = Span(base_span=base_span, layer=layer)
    assert span.text == ['0123', '89a']
    assert span.enclosing_text == '0123456789a'
    assert span.text_object is text
    text = Text('')
    layer = BaseLayer('test_layer', text_object=text)
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(8, 12)])
    span = Span(base_span=base_span, layer=layer)
    assert span.text == ['', '']
    assert span.enclosing_text == ''
    assert span.text_object is text


def test_parent_property_access_and_assignment():
    # Tests based on:
    #   https://github.com/estnltk/estnltk/blob/5bacff50072f9415814aee4f369c28db0e8d7789/estnltk/tests/test_layer/span/test_properties.py#L145-L239
    #
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # Computation of parent property succeeds if we do everything right
    text = Text('Tere!')
    parent_layer = BaseLayer('parent_layer', attributes=['attr'], text_object=text)
    parent_layer.add_annotation(base_span=ElementaryBaseSpan(0, 4), attr=42)
    text.add_layer(parent_layer)
    layer = BaseLayer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], parent='parent_layer', text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    # Parent attribute is computed and cached
    assert span.parent is parent_layer[0]
    assert span._parent is parent_layer[0]
    
    # span.parent cannot be directly assigned. 
    with pytest.raises(AttributeError):
        span.parent = span
    #
    #  Note: span._parent can be assigned, but that is an internal 
    #  property, not to be considered as a part of the public interface.
    #  In the old version, there were lot of guards for span.parent 
    #  assignment which have been omitted
    #
    
    # Computation of parent property fails if span does not have a layer
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)
    assert span.parent is None
    assert span._parent is None

    # Computation of parent property fails if a layer does not have a parent
    layer = BaseLayer('test_layer')
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    assert span.parent is None
    assert span._parent is None

    # Computation of parent property fails if a layer does not reference a text object
    layer = BaseLayer('test_layer', parent="parent_layer")
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    assert span.parent is None
    assert span._parent is None

    # Computation of parent property fails if the parent layer is not attached to the text
    text = Text('Tere!')
    parent_layer = BaseLayer('parent_layer', attributes=['attr'], text_object=text)
    parent_layer.add_annotation(base_span=ElementaryBaseSpan(0, 4), attr=42)
    layer = BaseLayer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], parent='parent_layer', text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    # Parent attribute is not computed and cached
    assert span.parent is None
    assert span._parent is None

    # Computation of parent property fails if the base span is not in parent layer that is attached to the text
    text = Text('Tere!')
    parent_layer = BaseLayer('parent_layer', attributes=['attr'], text_object=text)
    parent_layer.add_annotation(base_span=ElementaryBaseSpan(0, 2), attr=42)
    text.add_layer(parent_layer)
    layer = BaseLayer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], parent='parent_layer', text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    # Parent attribute is not computed and cached
    assert span.parent is None
    assert span._parent is None


def test_span_annotations_repr():
    # Test span annotations rendering (as string)
    # Case 1: spans with annotation values consisting of basic types: None, str, int, float, bool
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_1=None) )
    assert str(span) == "Span(None, [{'attr_1': None}])"
    
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_1='my_value') )
    assert str(span) == "Span(None, [{'attr_1': 'my_value'}])"
    
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_1=42) )
    assert str(span) == "Span(None, [{'attr_1': 42}])"

    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_1=3.1415926535897) )
    assert str(span) == "Span(None, [{'attr_1': 3.1415926535897}])"
    
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_1=False) )
    assert str(span) == "Span(None, [{'attr_1': False}])"
    
    # Case 2: spans with annotation values consisting of sequences of basic types
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_seq'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_seq=(None, None, None, False)) )
    assert str(span) == "Span(None, [{'attr_seq': (None, None, None, False)}])"
    
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_seq'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_seq=[1, 2, 3.14, 'N/A']) )
    assert str(span) == "Span(None, [{'attr_seq': [1, 2, 3.14, 'N/A']}])"

    # Case 3: spans with annotation values consisting of dicts of basic types
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_dict'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_dict={"a": 1, "b": 2, "c": None}) )
    assert str(span) == "Span(None, [{'attr_dict': {'a': 1, 'b': 2, 'c': None}}])"

    # Case 4: repr of syntax layer (which has recursive span references)
    syntax_layer = BaseLayer( name='my_syntax', attributes=('id',
                                                            'lemma',
                                                            'head',
                                                            'parent_span',
                                                            'children') )
    syntax_layer.add_annotation( (0, 4), **{'head': 3,
                                            'id': 1,
                                            'lemma': 'tere',
                                            'parent_span': None,
                                            'children': None} )
    syntax_layer.add_annotation( (4, 5), **{'head': 3,
                                            'id': 2,
                                            'lemma': ',',
                                            'parent_span': None,
                                            'children': None} )
    syntax_layer.add_annotation( (6, 12), **{'head': 0,
                                             'id': 3,
                                             'lemma': 'Kerttu',
                                             'parent_span': None,
                                             'children': None} )
    syntax_layer.add_annotation( (12, 13), **{'head': 3,
                                              'id': 4,
                                              'lemma': '!',
                                              'parent_span': None,
                                              'children': None} )
    # Add parent/child references
    syntax_layer[0].annotations[0].parent_span = syntax_layer[2]
    syntax_layer[0].annotations[0].children = ()
    syntax_layer[1].annotations[0].parent_span = syntax_layer[2]
    syntax_layer[1].annotations[0].children = ()
    syntax_layer[2].annotations[0].parent_span = None
    syntax_layer[2].annotations[0].children = (syntax_layer[0], syntax_layer[1], syntax_layer[3])
    syntax_layer[3].annotations[0].parent_span = syntax_layer[2]
    syntax_layer[3].annotations[0].children = ()
    # Check span repr
    expected_span_0_repr = \
       "Span(None, [{'id': 1, 'lemma': 'tere', 'head': 3, 'parent_span': <class 'estnltk_core.layer.span.Span'>, 'children': ()}])"
    assert repr(syntax_layer[0]) == expected_span_0_repr
    assert str(syntax_layer[0]) == expected_span_0_repr
    expected_span_1_repr = \
       "Span(None, [{'id': 2, 'lemma': ',', 'head': 3, 'parent_span': <class 'estnltk_core.layer.span.Span'>, 'children': ()}])"
    assert repr(syntax_layer[1]) == expected_span_1_repr
    assert str(syntax_layer[1]) == expected_span_1_repr
    expected_span_2_repr = \
       "Span(None, [{'id': 3, 'lemma': 'Kerttu', 'head': 0, 'parent_span': None, 'children': <class 'tuple'>}])"
    assert repr(syntax_layer[2]) == expected_span_2_repr
    assert str(syntax_layer[2]) == expected_span_2_repr


def test_repr_html():
    # Test span rendering as HTML
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # Case 1: no text object -- return same output as str
    span_1 = Span(ElementaryBaseSpan(0, 1), layer=BaseLayer('test', attributes=['attr_1']))
    span_1.add_annotation(Annotation(span_1, attr_1=0))
    assert span_1._repr_html_() == str(span_1)

    # Case 2: with text object, return HTML
    text = Text('ABC')
    layer = BaseLayer('test', attributes=['attr_1'], text_object=text, ambiguous=True)
    span_1 = Span(ElementaryBaseSpan(0, 1), layer=layer)
    span_1.add_annotation(Annotation(span_1, attr_1=0))
    span_1.add_annotation(Annotation(span_1, attr_1=3))
    output_html_1 = span_1._repr_html_()
    output_html_2 = span_1._to_html()
    # This renders a HTML table. However, its formatting depends on pandas, so we don't
    # want to hardcode formatting into test. 
    # Instead, test loosely general properties
    assert output_html_1 == output_html_2
    assert output_html_1.startswith('<b>{}</b>'.format(span_1.__class__.__name__))
    assert '<table' in output_html_1
    assert '<th>text</th>' in output_html_1
    assert '<th>attr_1</th>' in output_html_1
    assert re.search( '<td>.*?A.*?</td>', output_html_1 ) is not None
    assert re.search( '<td>.*?0.*?</td>', output_html_1 ) is not None
    assert re.search( '<td></td>', output_html_1 ) is not None
    assert re.search( '<td>.*?3.*?</td>', output_html_1 ) is not None
    assert '</table>' in output_html_1

