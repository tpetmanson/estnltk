from copy import deepcopy
from reprlib import recursive_repr
from typing import Any, Mapping, Sequence

from estnltk_core.common import _create_attr_val_repr

class Annotation(Mapping):
    """Mapping for Span attribute values.

    Annotation is the object that contains information about the attribute values. Annotations are
    tied to a Span which hold the information about the location of the annotation. The attributes
    of an Annotation are formatted as a dictionary and they can be passed as arguments to the
    Annotation.

    Once the Annotation has a Span, it can not be changed.
    """
    __slots__ = ['__dict__', '_span']

    def __init__(self, span, **attributes):
        self._span = span
        self.__dict__ = attributes

    def __deepcopy__(self, memo=None):
        """
        Makes a deep copy of all annotation attributes but detaches annotation from span.
        RATIONALE: One copies an annotation only to attach the copy to a different span.
        Based on: 
          https://github.com/estnltk/estnltk/blob/974c666b2da3e89dc42d570aad4b66ef060a6742/estnltk/layer/annotation.py#L44
        """
        memo = memo or {}
        result = self.__class__(span=None)
        # Add newly created valid mutable objects to memo
        memo[id(self)] = result
        # Perform deep copy with a valid memo dict
        result.__dict__ = deepcopy(self.__dict__, memo)
        return result

    @property
    def span(self):
        return self._span

    @property
    def start(self) -> int:
        if self._span:
            return self._span.start

    @property
    def end(self) -> int:
        if self._span:
            return self._span.end

    @property
    def layer(self):
        if self._span:
            return self._span.layer

    @property
    def legal_attribute_names(self) -> Sequence[str]:
        if self.layer is not None:
            return self.layer.attributes

    @property
    def text_object(self):
        if self._span is not None:
            return self._span.text_object

    @property
    def text(self):
        if self._span:
            return self._span.text

    def __setattr__(self, key, value):
        if key in self.__slots__:
            super().__setattr__(key, value)
        elif key == 'span':
            if self._span is None:
                super().__setattr__('_span', value)
            else:
                raise AttributeError('this Annotation object already has a span')
        else:
            self.__dict__[key] = value

    def __contains__(self, item):
        return item in self.__dict__

    def __len__(self):
        return len(self.__dict__)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.__dict__[item]
        if isinstance(item, tuple):
            return tuple(self.__dict__[i] for i in item)
        raise TypeError(item)

    def __iter__(self):
        yield from self.__dict__

    def __delitem__(self, key):
        del self.__dict__[key]

    def __delattr__(self, item):
        try:
            del self[item]
        except KeyError as key_error:
            raise AttributeError(key_error.args[0]) from key_error

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Annotation) and self.__dict__ == other.__dict__

    @recursive_repr()
    def __repr__(self):
        # Output key-value pairs in an ordered way
        # (to assure a consistent output, e.g. for automated testing)

        if self.legal_attribute_names is None:
            attribute_names = sorted(self.__dict__)
        else:
            attribute_names = self.legal_attribute_names

        attr_val_repr = _create_attr_val_repr( [(k, self.__dict__[k]) for k in attribute_names] )

        return '{class_name}({text!r}, {attributes})'.format(class_name=self.__class__.__name__, 
                                                             text=self.text,
                                                             attributes=attr_val_repr)

