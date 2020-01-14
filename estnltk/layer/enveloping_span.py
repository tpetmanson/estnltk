from typing import Any, Iterable

from estnltk.layer.span import Span, Annotation
from estnltk import BaseSpan, EnvelopingBaseSpan


class EnvelopingSpan(Span):

    def __init__(self, base_span: BaseSpan, layer):
        super().__init__(base_span, layer)

    @classmethod
    def from_spans(cls, spans: Iterable[Span], layer, records):
        span = cls(base_span=EnvelopingBaseSpan(s.base_span for s in spans), layer=layer)
        for record in records:
            span.add_annotation(Annotation(span, **record))
        return span

    # TODO: Push down to Span
    @property
    def spans(self):
        if self._spans is None:
            get_from_enveloped = self.layer.text_object[self.layer.enveloping].get
            self._spans = tuple(get_from_enveloped(base) for base in self.base_span)

        return self._spans

    def to_records(self, with_text=False):
        return [i.to_records(with_text) for i in self.spans]

    @property
    def _html_text(self):
        rt = self.raw_text
        result = []
        for a, b in zip(self.spans, self.spans[1:]):
            result.extend(('<b>', rt[a.start:a.end], '</b>', rt[a.end:b.start]))
        result.extend(('<b>', rt[self.spans[-1].start:self.spans[-1].end], '</b>'))
        return ''.join(result)

    # TODO: Push down to Span
    def __iter__(self):
        yield from self.spans

    def __len__(self) -> int:
        return len(self.base_span)

    def __contains__(self, item: Any) -> bool:
        return item in self.spans

    def __setattr__(self, key, value):
        if key == '_spans':
            object.__setattr__(self, key, value)
        else:
            super().__setattr__(key, value)
    # TODO: ------------------

    def resolve_attribute(self, item):
        if item not in self.text_object.layers:
            attribute_mapping = self.text_object.attribute_mapping_for_enveloping_layers
            return self.layer.text_object[attribute_mapping[item]].get(self.base_span)[item]

        target_layer = self.text_object[item]

        if len(target_layer) == 0:
            return

        if target_layer[0].base_span.level >= self.base_span.level:
            raise AttributeError('target layer level {} should be lower than {}'.format(
                    target_layer[0].base_span.level, self.base_span.level))

        return target_layer.get(self.base_span)

    # TODO: Push down to Span
    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.spans[idx]

        return super().__getitem__(idx)
