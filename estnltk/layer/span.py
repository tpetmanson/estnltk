from typing import MutableMapping, Any, List


class Span:
    def __init__(self, start: int=None, end: int=None, parent=None, *,
                 layer=None, legal_attributes=None, **attributes) -> None:

        # this is set up first, because attribute access depends on knowing attribute names as early as possible
        self._legal_attribute_names = legal_attributes
        if isinstance(self._legal_attribute_names, list):
            # TODO: remove this if
            self._legal_attribute_names = tuple(self._legal_attribute_names)
        self.is_dependant = parent is None

        # Placeholder, set when span added to spanlist
        self.layer = layer  # type: Layer
        self.parent = parent  # type: Span

        if isinstance(start, int) and isinstance(end, int):
            assert start < end

            self._start = start
            self._end = end
            self.is_dependant = False

        # parent is a Span of dependant Layer
        elif parent is not None:
            assert start is None
            assert end is None
            self.is_dependant = True

            # The _base of a root-layer Span is the span itself.
            # So, if the parent is a root-layer the following must hold (self._base == self.parent == self.parent._base)
            # If the parent is not a root-layer Span, (self._base == self.parent._base)
            self._base = parent._base  # type: Span

        else:
            assert 0, 'What?'

        if not self.is_dependant:
            self._base = self  # type:Span

        for k, v in attributes.items():
            if k in legal_attributes:
                self.__setattr__(k, v)

    @property
    def legal_attribute_names(self) -> List[str]:
        if self.__getattribute__('_legal_attribute_names') is not None:
            return self.__getattribute__('_legal_attribute_names')
        else:
            return self.__getattribute__('layer').__getattribute__('attributes')

    def to_record(self, with_text=False) -> MutableMapping[str, Any]:
        return {
        **{k: self.__getattribute__(k) for k in list(self.legal_attribute_names) + (['text'] if with_text else [])},
            **{'start': self.start, 'end': self.end}}

    def mark(self, mark_layer: str) -> 'Span':
        base_layer = self.text_object.layers[mark_layer]  # type: Layer
        base = base_layer._base

        assert base == self.layer._base, "Expected '{self.layer._base}' got '{base}'".format(self=self, base=base)
        res = base_layer.add_span(
            Span(
                parent=self._base  # this is the base span
            )
        )
        return res

    @property
    def start(self) -> int:
        if not self.is_dependant:
            return self._start
        else:
            return self.parent.start

    @start.setter
    def start(self, value: int):
        assert not self.is_bound, 'setting start is allowed on special occasions only'
        self._start = value

    @property
    def end(self) -> int:
        if not self.is_dependant:
            return self._end
        else:
            return self.parent.end

    @end.setter
    def end(self, value: int):
        assert not self.is_bound, 'setting end is allowed on special occasions only'
        self._end = value

    @property
    def text(self):
        return self.text_object.text[self.start:self.end]

    @property
    def text_object(self):
        return self.layer.text_object

    @property
    def raw_text(self):
        return self.text_object.text

    @property
    def html_text(self):
        return '<b>' + self.raw_text[self.start:self.end] + '</b>'

    # --------------------------------------
    
    #  Layer operations are ported from:
    #    https://github.com/estnltk/estnltk/blob/master/estnltk/single_layer_operations/layer_positions.py
    
    def touching_right(self, y:Any) -> bool:
        """ 
        Tests if Span y is touching this Span (x) from the right.
        Pictorial example:
        xxxxxxxx
                yyyyy
        """
        assert isinstance(y, Span)
        return self.end == y.start

    def touching_left(self, y:Any) -> bool:
        """ 
        Tests if Span y is touching this Span (x) from the left.
        Pictorial example:
             xxxxxxxx
        yyyyy
        """
        assert isinstance(y, Span)
        return y.touching_right(self)

    def hovering_right(self, y:Any) -> bool:
        """
        Tests if Span y is hovering right from this Span (x).
        Pictorial example:
        xxxxxxxx
                  yyyyy
        """
        assert isinstance(y, Span)
        return self.end < y.start

    def hovering_left(self, y:Any) -> bool:
        """
        Tests if Span y is hovering left from this Span (x).
        Pictorial example:
                xxxxxxxx
        yyyyy
        """
        assert isinstance(y, Span)
        return y.hovering_right(self)

    def right(self, y:Any) -> bool:
        '''
        Tests if Span y is either touching or hovering right with respect to this Span.
        '''
        assert isinstance(y, Span)
        return self.touching_right(y) or self.hovering_right(y)

    def left(self, y:Any) -> bool:
        '''
        Tests if Span y is either touching or hovering left with respect to this Span.
        '''
        assert isinstance(y, Span)
        return y.right(self)

    def nested(self, y:Any) -> bool:
        """
        Tests if Span y is nested inside this Span (x).
        Pictorial example:
        xxxxxxxx
          yyyyy
        """
        assert isinstance(y, Span)
        return self.start <= y.start <= y.end <= self.end

    def equal(self, y:Any) -> bool:
        """
        Tests if Span y is positionally equal to this Span (x). 
        (Both are nested within each other).
        Pictorial example:
        xxxxxxxx
        yyyyyyyy
        """
        assert isinstance(y, Span)
        return self.nested(y) and y.nested(self)

    def nested_aligned_right(self, y:Any) -> bool:
        """
        Tests if Span y is nested inside this Span (x), and 
        Span y is aligned with the right ending of this Span.
        Pictorial example:
        xxxxxxxx
           yyyyy
        """
        assert isinstance(y, Span)
        return self.nested(y) and self.end == y.end

    def nested_aligned_left(self, y:Any) -> bool:
        """
        Tests if Span y is nested inside this Span (x), and 
        Span y is aligned with the left ending of this Span.
        Pictorial example:
        xxxxxxxx
        yyyyy
        """
        assert isinstance(y, Span)
        return self.nested(y) and self.start == y.start

    def overlapping_left(self, y:Any) -> bool:
        """
        Tests if left side of this Span (x) overlaps with 
        the Span y, but y is not nested within this Span.
        Pictorial example:
          xxxxxxxx
        yyyyy
        """
        assert isinstance(y, Span)
        return y.start < self.start < y.end

    def overlapping_right(self, y:Any) -> bool:
        """
        Tests if right side of this Span (x) overlaps with
        the Span y, but y is not nested within this Span.
        Pictorial example:
        xxxxxxxx
              yyyyy
        """
        assert isinstance(y, Span)
        return y.start < self.end < y.end

    def conflict(self, y:Any) -> bool:
        """
        Tests if there is a conflict between this Span and the 
        Span y: one of the Spans is either nested within other, 
        or there is an overlapping from right or left side.
        """
        assert isinstance(y, Span)
        return self.nested(y) or y.nested(self) or \
               self.overlapping_left(y) or self.overlapping_right(y)

    # --------------------------------------
    
    def __getattr__(self, item):
        if item in {'start', 'end', 'layer', 'text'}:
            return self.__getattribute__(item)

        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError

        if item in self.__getattribute__('legal_attribute_names'):
            try:
                return self.__getattribute__(item)
            except AttributeError:
                return None

        elif item == getattr(self.layer, 'parent', None):
            return self.parent

        elif self.layer is not None and self.layer.text_object is not None and self.layer.text_object._path_exists(
                self.layer.name, item):
            # there exists an unambiguous path from this span to the target (attribute)

            looking_for_layer = False
            if item in self.layer.text_object.layers.keys():
                looking_for_layer = True
                target_layer_name = self.text_object._get_path(self.layer.name, item)[-1]
            else:
                target_layer_name = self.text_object._get_path(self.layer.name, item)[-2]

            for i in self.text_object.layers[target_layer_name].span_list:
                if i.__getattribute__('parent') == self or self.__getattribute__('parent') == i:
                    if looking_for_layer:
                        return i
                    else:
                        return getattr(i, item)

        else:
            return self.__getattribute__('__class__').__getattribute__(self, item)

    def __lt__(self, other: Any) -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Span):
            return False
        if self.start != other.start or self.end != other.end:
            return False
        if self.legal_attribute_names != other.legal_attribute_names:
            return False
        return all(self.__getattribute__(i) == other.__getattribute__(i) for i in self.legal_attribute_names)

    def __le__(self, other: Any) -> bool:
        return self < other or self == other

    def __hash__(self):
        return hash((self.start, self.end))

    def __str__(self):
        if self.layer is None:
            return 'Span(start={self.start}, end={self.end}, layer={self.layer}, parent={self.parent})'.\
                format(self=self)
        if self.layer.text_object is None:
            return 'Span(start={self.start}, end={self.end}, layer_name={self.layer.name}, parent={self.parent})'.\
                format(self=self)
        legal_attribute_names = self.__getattribute__('layer').__getattribute__('attributes')

        # Output key-value pairs in a sorted way
        # (to assure a consistent output, e.g. for automated testing)
        mapping_sorted = []

        for k in sorted(legal_attribute_names):
            key_value_str = "{key_val}".format(key_val = {k:self.__getattribute__(k)})
            # Hack: Remove surrounding '{' and '}'
            key_value_str = key_value_str[:-1]
            key_value_str = key_value_str[1:]
            mapping_sorted.append(key_value_str)

        # Hack: Put back surrounding '{' and '}' (mimic dict's representation)
        mapping_sorted_str = '{'+ (', '.join(mapping_sorted)) + '}'
        return 'Span({text}, {attributes})'.format(text=self.text, attributes=mapping_sorted_str)

    def __repr__(self):
        return str(self)

