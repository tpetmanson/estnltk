#
# Note: Serialisation of 'legacy_v0' layer is not part of 'estnltk_core', 
# but it is added later in 'estnltk'. 
# Test that converters are aware of the added serialisation module and 
# can convert a Text object with 'legacy_v0' layer.
#
from pprint import pprint

from estnltk_core.layer import AmbiguousAttributeList
from estnltk_core.converters import dict_to_text

test_legacy_v0_text_dict = \
    {'text': 'Varjatud Markovi mudelid',
     'meta': {'ajakirjanumber': 'Arvutustehnika ja andmetöötlus 02_4',
              'subcorpus': 'tea_',
              'file': 'tea_AA_02_4.tasak.xml_3.json',
              'title': 'A & A - Varjatud Markovi mudelid',
              'type': 'artikkel'},
     'layers': [{'_base': 'tokens',
                 'ambiguous': False,
                 'attributes': [],
                 'enveloping': None,
                 'name': 'tokens',
                 'parent': None,
                 'spans': [{'end': 8, 'start': 0},
                           {'end': 16, 'start': 9},
                           {'end': 24, 'start': 17}]},
                {'_base': 'compound_tokens',
                 'ambiguous': False,
                 'attributes': ['type', 'normalized'],
                 'enveloping': 'tokens',
                 'name': 'compound_tokens',
                 'parent': None,
                 'spans': []},
                {'_base': 'words',
                 'ambiguous': False,
                 'attributes': ['normalized_form'],
                 'enveloping': None,
                 'name': 'words',
                 'parent': None,
                 'spans': [{'end': 8, 'normalized_form': None, 'start': 0},
                           {'end': 16, 'normalized_form': None, 'start': 9},
                           {'end': 24, 'normalized_form': None, 'start': 17}]},
                {'_base': 'words',
                 'ambiguous': True,
                 'attributes': ['lemma',
                                'root',
                                'root_tokens',
                                'ending',
                                'clitic',
                                'form',
                                'partofspeech'],
                 'enveloping': None,
                 'name': 'morph_analysis',
                 'parent': 'words',
                 'spans': [[{'_index_': 0,
                             'clitic': '',
                             'end': 8,
                             'ending': '0',
                             'form': '',
                             'lemma': 'varjatud',
                             'partofspeech': 'A',
                             'root': 'varjatud',
                             'root_tokens': ['varjatud'],
                             'start': 0},
                            {'_index_': 0,
                             'clitic': '',
                             'end': 8,
                             'ending': '0',
                             'form': 'sg n',
                             'lemma': 'varjatud',
                             'partofspeech': 'A',
                             'root': 'varjatud',
                             'root_tokens': ['varjatud'],
                             'start': 0},
                            {'_index_': 0,
                             'clitic': '',
                             'end': 8,
                             'ending': 'tud',
                             'form': 'tud',
                             'lemma': 'varjama',
                             'partofspeech': 'V',
                             'root': 'varja',
                             'root_tokens': ['varja'],
                             'start': 0},
                            {'_index_': 0,
                             'clitic': '',
                             'end': 8,
                             'ending': 'd',
                             'form': 'pl n',
                             'lemma': 'varjatud',
                             'partofspeech': 'A',
                             'root': 'varjatud',
                             'root_tokens': ['varjatud'],
                             'start': 0}],
                           [{'_index_': 1,
                             'clitic': '',
                             'end': 16,
                             'ending': '0',
                             'form': 'sg g',
                             'lemma': 'Markov',
                             'partofspeech': 'H',
                             'root': 'Markov',
                             'root_tokens': ['Markov'],
                             'start': 9}],
                           [{'_index_': 2,
                             'clitic': '',
                             'end': 24,
                             'ending': 'd',
                             'form': 'pl n',
                             'lemma': 'mudel',
                             'partofspeech': 'S',
                             'root': 'mudel',
                             'root_tokens': ['mudel'],
                             'start': 17}]]},
                {'_base': 'words',
                 'ambiguous': True,
                 'attributes': ['lemma',
                                'root',
                                'root_tokens',
                                'ending',
                                'clitic',
                                'form',
                                'partofspeech'],
                 'enveloping': None,
                 'name': 'gt_morph_analysis',
                 'parent': 'morph_analysis',
                 'spans': [[{'_index_': 0,
                             'clitic': '',
                             'end': 8,
                             'ending': '0',
                             'form': '',
                             'lemma': 'varjatud',
                             'partofspeech': 'A',
                             'root': 'varjatud',
                             'root_tokens': ['varjatud'],
                             'start': 0},
                            {'_index_': 0,
                             'clitic': '',
                             'end': 8,
                             'ending': '0',
                             'form': 'Sg Nom',
                             'lemma': 'varjatud',
                             'partofspeech': 'A',
                             'root': 'varjatud',
                             'root_tokens': ['varjatud'],
                             'start': 0},
                            {'_index_': 0,
                             'clitic': '',
                             'end': 8,
                             'ending': 'tud',
                             'form': 'Impers Prt Prc',
                             'lemma': 'varjama',
                             'partofspeech': 'V',
                             'root': 'varja',
                             'root_tokens': ['varja'],
                             'start': 0},
                            {'_index_': 0,
                             'clitic': '',
                             'end': 8,
                             'ending': 'd',
                             'form': 'Pl Nom',
                             'lemma': 'varjatud',
                             'partofspeech': 'A',
                             'root': 'varjatud',
                             'root_tokens': ['varjatud'],
                             'start': 0}],
                           [{'_index_': 1,
                             'clitic': '',
                             'end': 16,
                             'ending': '0',
                             'form': 'Sg Gen',
                             'lemma': 'Markov',
                             'partofspeech': 'H',
                             'root': 'Markov',
                             'root_tokens': ['Markov'],
                             'start': 9}],
                           [{'_index_': 2,
                             'clitic': '',
                             'end': 24,
                             'ending': 'd',
                             'form': 'Pl Nom',
                             'lemma': 'mudel',
                             'partofspeech': 'S',
                             'root': 'mudel',
                             'root_tokens': ['mudel'],
                             'start': 17}]]},
                {'_base': 'syntax_ignore',
                 'ambiguous': False,
                 'attributes': ['type'],
                 'enveloping': 'words',
                 'name': 'syntax_ignore',
                 'parent': None,
                 'spans': []},
                {'_base': 'sentences',
                 'ambiguous': False,
                 'attributes': ['fix_types'],
                 'enveloping': 'words',
                 'name': 'sentences',
                 'parent': None,
                 'spans': [{'_index_': [0, 1, 2], 'fix_types': []}]},
                {'_base': 'paragraphs',
                 'ambiguous': False,
                 'attributes': [],
                 'enveloping': 'sentences',
                 'name': 'paragraphs',
                 'parent': None,
                 'spans': [{'_index_': [0]}]}]
        }

def test_restore_text_from_legacy_v0_dict():
    # Note: we first need to "preprocess" and specify 'serialisation_module' of each layer
    for layer in test_legacy_v0_text_dict['layers']:
        layer['serialisation_module'] = 'legacy_v0'
    # Then we can apply the conversion
    text_obj = dict_to_text( test_legacy_v0_text_dict )
    # Validate the results
    assert text_obj.text == 'Varjatud Markovi mudelid'
    assert text_obj.layers == {'tokens','compound_tokens','words','sentences',\
                               'paragraphs','morph_analysis','syntax_ignore','gt_morph_analysis'}
    assert len(text_obj['paragraphs']) == 1
    assert len(text_obj['sentences']) == 1
    assert len(text_obj['words']) == 3
    assert len(text_obj['morph_analysis']) == 3
    assert len(text_obj['gt_morph_analysis']) == 3

    assert text_obj['morph_analysis'].partofspeech == AmbiguousAttributeList([['A', 'A', 'V', 'A'], ['H'], ['S']], 'partofspeech')
    assert text_obj['morph_analysis'].lemma == AmbiguousAttributeList([['varjatud', 'varjatud', 'varjama', 'varjatud'], ['Markov'], ['mudel']], 'lemma')
    
