""" Test removing segments of the Text object that should be ignored by the syntactic analyser;
"""

from estnltk import Text
from estnltk.converters import layer_to_dict, dict_to_layer
from estnltk.taggers.standard.syntax.preprocessing.syntax_ignore_tagger import SyntaxIgnoreTagger
from estnltk.taggers.standard.syntax.preprocessing.syntax_ignore_cutter import SyntaxIgnoreCutter

def test_syntax_ignore_cutter_smoke():
    # Test that SyntaxIgnoreCutter works with SyntaxIgnoreTagger off-the-shelf
    test_text = Text('Klubi sai kuus korda Inglismaa meistriks (1976, 1977, 1979, 1980, 1982, 1983). '+\
                     'Tallinna ( 21.-22. mai ) , Haapsalu ( 2.-3. juuli ) ja Liivimaa ( 30.-31. juuli ) '+\
                     'rallidel on vähemalt see probleem lahendatud . '+\
                     'Temaatikaga seondub veel teinegi äsja Postimehes ilmunud jutt '+\
                     '(Priit Pullerits «Džiibi kaitseks», PM 30.07.2010).')
    test_text.tag_layer('sentences')
    syntax_ignore_tagger = SyntaxIgnoreTagger()
    syntax_ignore_tagger.tag(test_text)
    assert 'syntax_ignore' in test_text.layers
    assert len(test_text['syntax_ignore']) > 0
    syntax_ignore_cutter = SyntaxIgnoreCutter(add_words_layer=True)
    cut_text = syntax_ignore_cutter.cut(test_text)
    assert cut_text.text == \
        'Klubi sai kuus korda Inglismaa meistriks . Tallinna  , Haapsalu  ja Liivimaa  rallidel '+\
        'on vähemalt see probleem lahendatud . Temaatikaga seondub veel teinegi äsja Postimehes ilmunud jutt .'
    #from pprint import pprint
    #pprint(layer_to_dict(cut_text['words']))
    expected_words_layer = \
        {'ambiguous': False,
         'attributes': ('original_start', 'original_end', 'original_index'),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'original_end': 5,
                                     'original_index': 0,
                                     'original_start': 0}],
                    'base_span': (0, 5)},
                   {'annotations': [{'original_end': 9,
                                     'original_index': 1,
                                     'original_start': 6}],
                    'base_span': (6, 9)},
                   {'annotations': [{'original_end': 14,
                                     'original_index': 2,
                                     'original_start': 10}],
                    'base_span': (10, 14)},
                   {'annotations': [{'original_end': 20,
                                     'original_index': 3,
                                     'original_start': 15}],
                    'base_span': (15, 20)},
                   {'annotations': [{'original_end': 30,
                                     'original_index': 4,
                                     'original_start': 21}],
                    'base_span': (21, 30)},
                   {'annotations': [{'original_end': 40,
                                     'original_index': 5,
                                     'original_start': 31}],
                    'base_span': (31, 40)},
                   {'annotations': [{'original_end': 78,
                                     'original_index': 19,
                                     'original_start': 77}],
                    'base_span': (41, 42)},
                   {'annotations': [{'original_end': 87,
                                     'original_index': 20,
                                     'original_start': 79}],
                    'base_span': (43, 51)},
                   {'annotations': [{'original_end': 105,
                                     'original_index': 27,
                                     'original_start': 104}],
                    'base_span': (53, 54)},
                   {'annotations': [{'original_end': 114,
                                     'original_index': 28,
                                     'original_start': 106}],
                    'base_span': (55, 63)},
                   {'annotations': [{'original_end': 133,
                                     'original_index': 35,
                                     'original_start': 131}],
                    'base_span': (65, 67)},
                   {'annotations': [{'original_end': 142,
                                     'original_index': 36,
                                     'original_start': 134}],
                    'base_span': (68, 76)},
                   {'annotations': [{'original_end': 169,
                                     'original_index': 43,
                                     'original_start': 161}],
                    'base_span': (78, 86)},
                   {'annotations': [{'original_end': 172,
                                     'original_index': 44,
                                     'original_start': 170}],
                    'base_span': (87, 89)},
                   {'annotations': [{'original_end': 181,
                                     'original_index': 45,
                                     'original_start': 173}],
                    'base_span': (90, 98)},
                   {'annotations': [{'original_end': 185,
                                     'original_index': 46,
                                     'original_start': 182}],
                    'base_span': (99, 102)},
                   {'annotations': [{'original_end': 194,
                                     'original_index': 47,
                                     'original_start': 186}],
                    'base_span': (103, 111)},
                   {'annotations': [{'original_end': 205,
                                     'original_index': 48,
                                     'original_start': 195}],
                    'base_span': (112, 122)},
                   {'annotations': [{'original_end': 207,
                                     'original_index': 49,
                                     'original_start': 206}],
                    'base_span': (123, 124)},
                   {'annotations': [{'original_end': 219,
                                     'original_index': 50,
                                     'original_start': 208}],
                    'base_span': (125, 136)},
                   {'annotations': [{'original_end': 227,
                                     'original_index': 51,
                                     'original_start': 220}],
                    'base_span': (137, 144)},
                   {'annotations': [{'original_end': 232,
                                     'original_index': 52,
                                     'original_start': 228}],
                    'base_span': (145, 149)},
                   {'annotations': [{'original_end': 240,
                                     'original_index': 53,
                                     'original_start': 233}],
                    'base_span': (150, 157)},
                   {'annotations': [{'original_end': 245,
                                     'original_index': 54,
                                     'original_start': 241}],
                    'base_span': (158, 162)},
                   {'annotations': [{'original_end': 256,
                                     'original_index': 55,
                                     'original_start': 246}],
                    'base_span': (163, 173)},
                   {'annotations': [{'original_end': 264,
                                     'original_index': 56,
                                     'original_start': 257}],
                    'base_span': (174, 181)},
                   {'annotations': [{'original_end': 269,
                                     'original_index': 57,
                                     'original_start': 265}],
                    'base_span': (182, 186)},
                   {'annotations': [{'original_end': 321,
                                     'original_index': 69,
                                     'original_start': 320}],
                    'base_span': (187, 188)}]}
    assert cut_text['words'] == dict_to_layer(expected_words_layer)

