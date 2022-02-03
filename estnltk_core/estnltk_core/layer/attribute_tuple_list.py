from typing import Iterable, Union, List
from estnltk_core.layer import AmbiguousAttributeTupleList


class AttributeTupleList(AmbiguousAttributeTupleList):
    """Immutable lists for representing values of multiple attributes.
       
       The source of attributes can be:
       *) A single span, which has ambiguous annotations, e.g.
          >>> t=Text('mis').tag_layer()
          >>> t['morph_analysis'][0]['lemma', 'form']
          AttributeTupleList([['mis', 'sg n'], ['mis', 'pl n']], ('lemma', 'form'))
       
       *) Multiple spans of an unambiguous layer, e.g.
          >>> t=Text('Tere mis teet').tag_layer()
          >>> t['tokens']['text', 'text']
          AttributeTupleList([['Tere', 'Tere'], ['mis', 'mis'], ['teet', 'teet']], ('text', 'text'))
    """

    def __init__(self, span_or_spanlist:Union['Span', List['Span']], attribute_names:List[str], index_type:str='spans'):
        super().__init__(span_or_spanlist, attribute_names, index_type=index_type)

    def __eq__(self, other):
        if isinstance(other, AttributeTupleList):
            return super().__eq__(other)
        return False

    def __getitem__(self, item):
        if isinstance(item, slice):
            return AttributeTupleList([a[0] for a in self.amb_attr_tuple_list[item]], self.attribute_names)
        return self.amb_attr_tuple_list[item][0]
