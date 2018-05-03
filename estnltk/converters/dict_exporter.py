def layer_to_dict(layer, text):
    assert '_index_' not in layer.attributes
    layer_dict = {'name':layer.name,
                  'attributes': layer.attributes,
                  'parent': layer.parent,
                  '_base': layer._base,
                  'enveloping': layer.enveloping,
                  'ambiguous': layer.ambiguous,
                  'spans': []}
    if layer.parent:
        parent_spanlist = text[layer._base].span_list
        records = layer.to_records()
        last_index = 0
        for span, record in zip(layer, records):
            if layer.ambiguous:
                index = parent_spanlist.index(span.parent, last_index)
                for rec in record:
                    rec['_index_'] = index
            else:
                index = parent_spanlist.index(span, last_index)
                record['_index_'] = index
            last_index = index
            layer_dict['spans'].append(record)
    elif layer.enveloping:
        enveloped_spanlist = text[layer.enveloping].span_list
        
        records = []
        last_index = 0
        for spanlist in layer:
            index = [enveloped_spanlist.index(span, last_index) for span in spanlist]
            last_index = index[0]
            if layer.ambiguous:
                pass
                # TODO:
            else:
                record = {attr:getattr(spanlist, attr) for attr in layer.attributes}
                record['_index_'] = index
                records.append(record)
        layer_dict['spans'] = records
    else:
        layer_dict['spans'] = layer.to_records()

    return layer_dict


def export_dict(text):
    text_dict = {'text': text.text,
                 'meta': text.meta,
                 'layers': []}
    for layer in text.list_layers():
        text_dict['layers'].append(layer_to_dict(layer, text))
    return text_dict
