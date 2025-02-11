import re
import os
import os.path 
import tempfile
import pytest

from estnltk.taggers.system.rule_taggers.regex_library.string_list import StringList
from estnltk.taggers.system.rule_taggers.regex_library.choice_group import ChoiceGroup
from estnltk.taggers.system.rule_taggers.regex_library.regex_element import RegexElement

#===================================
#   StringList
#===================================

def test_regex_string_list_to_str():
    # Regular StringList
    PALLITUS = StringList(['p', 'pall', 'punkt', 'palli', 'punkti', 'st', '-st', 'palli'])
    PALLITUS.full_match('p')
    PALLITUS.full_match('st')
    PALLITUS.full_match('-st')
    PALLITUS.full_match('palli')
    PALLITUS.full_match('pall')
    PALLITUS.full_match('punkt')
    PALLITUS.full_match('punkti')
    PALLITUS.partial_match('pallile','palli')
    PALLITUS.partial_match('pallist','palli')
    PALLITUS.test()
    assert str(PALLITUS) == r'(?:punkti|palli|punkt|pall|\-st|st|p)'


def test_regex_string_list_to_str_with_extras():
    # Regular StringList with (simple) replacement:  'p' -> '[Pp]'
    PALLITUS2 = StringList(['p', 'pall', 'punkt', 'palli', 'punkti'], \
                            replacements={'p':'[Pp]'})
    assert str(PALLITUS2) == \
        r'(?:(?:[Pp])unkti|(?:[Pp])alli|(?:[Pp])unkt|(?:[Pp])all|(?:[Pp]))'
    # replacements cannot be added afterwards
    with pytest.raises(AttributeError) as attrib_err:
        # 'changing of the attribute replacements after initialization not allowed in StringList'
        PALLITUS2.replacements = {'a':'[Aa]'}
    # Regular StringList with a bit more complex replacement: ' ' -> '\s+'
    PALLITUS3 = StringList([' p', ' pall', ' punkt', ' palli', ' punkti'], \
                            replacements={' ':r'\s+'})
    assert str(PALLITUS3) == \
        r'(?:(?:\s+)punkti|(?:\s+)palli|(?:\s+)punkt|(?:\s+)pall|(?:\s+)p)'
    # Regular StringList with a replacement and full case insensitivity
    PALLITUS4 = StringList([' p', ' pall', ' punkt', ' palli', ' punkti'], \
                            replacements={' ':r'\s+'}, ignore_case=True)
    assert str(PALLITUS4) == \
        r'(?:(?:\s+)[Pp][Uu][Nn][Kk][Tt][Ii]|(?:\s+)[Pp][Aa][Ll][Ll][Ii]|'+\
        r'(?:\s+)[Pp][Uu][Nn][Kk][Tt]|(?:\s+)[Pp][Aa][Ll][Ll]|(?:\s+)[Pp])'


def test_regex_string_list_evaluation():
    # A) StringList as a choice group, case sensitive
    PALLITUS = StringList(['p', 'pall', 'punkt', 'palli', 'punkti', 'st', '-st', 'palli'], \
                           autogenerate_tests=True)
    # Note: with autogenerate_tests, unique input strings will be added as positive 
    # tests automatically, so we only need to add partial matches and negative tests
    assert len(PALLITUS.positive_tests) == 7
    # Passing tests
    PALLITUS.partial_match('pallile','palli')
    PALLITUS.partial_match('pallist','palli')
    PALLITUS.no_match('boonus')
    PALLITUS.no_match('skoor')
    PALLITUS.no_match('P')
    PALLITUS.test()
    # Failing tests
    PALLITUS.full_match('punni')
    PALLITUS.no_match('punni')
    PALLITUS.partial_match('pallile', 'pallile')
    PALLITUS.partial_match(' PALLI ', 'PALLI')
    # Validate
    eval_pos_results_dict = \
        PALLITUS.evaluate_positive_examples().to_dict(orient='split')
    #print( eval_pos_results_dict )
    assert eval_pos_results_dict == \
        {'columns': ['Example', 'Description', 'Status'], 
         'data': [['p', 'autogenerated test', '+'], 
                  ['pall', 'autogenerated test', '+'], 
                  ['punkt', 'autogenerated test', '+'], 
                  ['palli', 'autogenerated test', '+'], 
                  ['punkti', 'autogenerated test', '+'], 
                  ['st', 'autogenerated test', '+'], 
                  ['-st', 'autogenerated test', '+'], 
                  ['punni', '', 'F']],
         'index': [0, 1, 2, 3, 4, 5, 6, 7]}
    eval_neg_results_dict = \
        PALLITUS.evaluate_negative_examples().to_dict(orient='split')
    #print( eval_neg_results_dict )
    assert eval_neg_results_dict == \
        {'columns': ['Example', 'Status'], 
         'data': [['boonus', '+'], ['skoor', '+'], ['P', '+'], ['punni', 'F']],
         'index': [0, 1, 2, 3]}
    eval_extract_results_dict = \
        PALLITUS.evaluate_extraction_examples().to_dict(orient='split')
    #print( eval_extract_results_dict )
    assert eval_extract_results_dict == \
        {'columns': ['Example', 'Status'], 
         'data': [['pallile', '+'], ['pallist', '+'], ['pallile', 'F'], [' PALLI ', 'F']],
         'index': [0, 1, 2, 3]}
    # B) StringList as a choice group, case insensitive
    PALLITUS2 = StringList(['p', 'pall', 'punkt', 'palli', 'punkti', 'palli'], \
                           ignore_case=True, autogenerate_tests=True)
    assert len(PALLITUS2.positive_tests) == 5
    # Passing tests
    PALLITUS2.full_match('PUNKTI')
    PALLITUS2.full_match('pALLi')
    PALLITUS2.full_match('P')
    PALLITUS2.partial_match('PALLIST', 'PALLI')
    PALLITUS2.partial_match('PalLile', 'PalLi')
    PALLITUS2.no_match('bOoNus')
    PALLITUS2.no_match('SkooR')
    PALLITUS2.test()
    # Failing tests
    PALLITUS2.full_match('Points')
    PALLITUS2.no_match('Punni')
    PALLITUS2.partial_match('PalliLE', 'PalliLE')
    # Validate
    eval_pos_results_dict = \
        PALLITUS2.evaluate_positive_examples().to_dict(orient='split')
    #print( eval_pos_results_dict )
    assert eval_pos_results_dict == \
        {'columns': ['Example', 'Description', 'Status'], 
         'data': [['p', 'autogenerated test', '+'], 
                  ['pall', 'autogenerated test', '+'], 
                  ['punkt', 'autogenerated test', '+'], 
                  ['palli', 'autogenerated test', '+'], 
                  ['punkti', 'autogenerated test', '+'], 
                  ['PUNKTI', '', '+'], 
                  ['pALLi', '', '+'], 
                  ['P', '', '+'], 
                  ['Points', '', 'F']],
         'index': [0, 1, 2, 3, 4, 5, 6, 7, 8]}
    eval_neg_results_dict = \
        PALLITUS2.evaluate_negative_examples().to_dict(orient='split')
    #print( eval_neg_results_dict )
    assert eval_neg_results_dict == \
        {'columns': ['Example', 'Status'], 
         'data': [['bOoNus', '+'], ['SkooR', '+'], ['Punni', 'F']],
         'index': [0, 1, 2]}
    eval_extract_results_dict = \
        PALLITUS2.evaluate_extraction_examples().to_dict(orient='split')
    #print( eval_extract_results_dict )
    assert eval_extract_results_dict == \
        {'columns': ['Example', 'Status'], 
         'data': [['PALLIST', '+'], ['PalLile', '+'], ['PalliLE', 'F']],
         'index': [0, 1, 2]}


def test_regex_string_list_csv_writing_and_reading():
    PALLITUS = StringList([' p', ' pall', ' punkt', ' palli_', ' punkti_'], \
                           replacements={' ':r'\s*', 'p': '[Pp]', '_': '.?'}, \
                           autogenerate_tests=True)
    PALLITUS.full_match(' palli')
    PALLITUS.full_match('  punkt')
    PALLITUS.full_match('    punkti')
    assert len(PALLITUS.positive_tests) == 8
    PALLITUS.partial_match(' pallile', ' pallil')
    PALLITUS.partial_match('pallist', 'pallis')
    PALLITUS.test()
    #print(str(PALLITUS))
    with tempfile.TemporaryDirectory(suffix='csv_') as tmp_dir:
        # Export to CSV
        fpath = os.path.join(tmp_dir, 'string_list_1.csv')
        PALLITUS.to_csv(fpath)
        # Read from CSV (must use the same replacements)
        PALLITUS2 = StringList.from_file(fpath,
                        replacements={' ':r'\s*', 'p': '[Pp]', '_': '.?'},
                        autogenerate_tests=True)
        # Check that string representations of both StringList-s match
        assert str(PALLITUS) == str(PALLITUS2)
        # Check tests
        PALLITUS2.full_match(' palli')
        PALLITUS2.full_match('  punkt')
        PALLITUS2.full_match('    punkti')
        assert len(PALLITUS2.positive_tests) == 8
        PALLITUS2.partial_match(' pallile', ' pallil')
        PALLITUS2.partial_match('pallist', 'pallis')
        PALLITUS2.test()
        #print(str(PALLITUS2))

    # assert clean up
    assert not os.path.exists(fpath)


#===================================
#   ChoiceGroup
#===================================

def test_choice_group_smoke():
    # Test composing a ChoiceGroup from various sub-expressions
    # Various numeric expressions
    SPACED_INTEGER = RegexElement('[0-9]+(?: 000)*')
    SPACED_INTEGER.full_match('1234')
    SPACED_INTEGER.full_match('123 000')
    SPACED_INTEGER.full_match('123 000 000')
    SPACED_INTEGER.full_match('123 000 000')
    SPACED_INTEGER.no_match('paarteist')
    SPACED_INTEGER.no_match('kolmteist tuhat')
    SPACED_INTEGER.partial_match('umbes 1 000 000 aastat tagasi', '1 000 000')
    SPACED_INTEGER.test()

    DECIMAL_FRACTION = RegexElement(r'(?:[0-9]+\s*(?:,|\.)\s*)?[0-9]+')
    DECIMAL_FRACTION.full_match('123')
    DECIMAL_FRACTION.full_match('012')
    DECIMAL_FRACTION.full_match('1.2')
    DECIMAL_FRACTION.full_match('1,2')
    DECIMAL_FRACTION.full_match('0.12')
    DECIMAL_FRACTION.full_match('0,12')
    DECIMAL_FRACTION.full_match('1, 3')
    DECIMAL_FRACTION.full_match('1. 3')
    DECIMAL_FRACTION.full_match('1 , 3')
    DECIMAL_FRACTION.full_match('1 . 3')
    DECIMAL_FRACTION.no_match('üks koma kolm')
    DECIMAL_FRACTION.no_match('kaks koma viis')
    DECIMAL_FRACTION.partial_match('tõusis 5%', '5')
    DECIMAL_FRACTION.partial_match('vähenes 0.25 kg', '0.25')
    DECIMAL_FRACTION.test()

    INTEGER_ABBREVIATION = StringList(['milj.', 'milj'])
    SEMI_WORD_INTEGER = RegexElement(fr'{DECIMAL_FRACTION}\s*{INTEGER_ABBREVIATION}')
    SEMI_WORD_INTEGER.full_match('10 milj.')
    SEMI_WORD_INTEGER.full_match('1,5 milj.')
    SEMI_WORD_INTEGER.full_match('1 , 5milj.')
    SEMI_WORD_INTEGER.no_match('viis milj.')
    SEMI_WORD_INTEGER.no_match('kaheks miljonit')
    SEMI_WORD_INTEGER.partial_match('mahus 10 milj. tonni', '10 milj.')
    SEMI_WORD_INTEGER.partial_match('see teeb 2 miljonit tonni rohkem', '2 milj')
    SEMI_WORD_INTEGER.test()

    NUMBER_EXPRESSION = ChoiceGroup([SEMI_WORD_INTEGER, SPACED_INTEGER, DECIMAL_FRACTION],
                                    merge_positive_tests=False,
                                    merge_negative_tests=False,
                                    merge_extraction_tests=False)
    NUMBER_EXPRESSION.full_match('123 000')
    NUMBER_EXPRESSION.full_match('123')
    NUMBER_EXPRESSION.full_match('12.35')
    NUMBER_EXPRESSION.full_match('12.35 milj.')
    NUMBER_EXPRESSION.test()
    #print(str(NUMBER_EXPRESSION))
    assert str(NUMBER_EXPRESSION) == \
        r'(?:(?:(?:(?:[0-9]+\s*(?:,|\.)\s*)?[0-9]+)\s*(?:milj\.|milj))|(?:[0-9]+(?: 000)*)|(?:(?:[0-9]+\s*(?:,|\.)\s*)?[0-9]+))'

    # Test merging tests
    # Note that we cannot merge partial_match tests as these are incompatible with the whole ChoiceGroup's pattern
    NUMBER_EXPRESSION2 = ChoiceGroup([SEMI_WORD_INTEGER, SPACED_INTEGER, DECIMAL_FRACTION], 
                                     merge_positive_tests=True,
                                     merge_negative_tests=True,
                                     merge_extraction_tests=False)
    assert len(NUMBER_EXPRESSION2.positive_tests) == 16
    assert len(NUMBER_EXPRESSION2.negative_tests) == 6
    assert len(NUMBER_EXPRESSION2.extraction_tests) == 0
    NUMBER_EXPRESSION2.test()


def test_choice_group_of_string_lists():
    # Test that ChoiceGroup uses safe and clever ways to join StringList-s
    ADJECTIVES = StringList(['pehmed', 'karvased', 'kohevad', 'oma'], ignore_case=True)
    PROPER_NOUNS = StringList(['Jacques Chirac', 'Piilupart Donald', 'Vegas', 'Om'], ignore_case=False)
    ADJ_AND_NAMES = ChoiceGroup([ADJECTIVES, PROPER_NOUNS])
    ADJ_AND_NAMES.full_match('Jacques Chirac')
    ADJ_AND_NAMES.full_match('Piilupart Donald')
    ADJ_AND_NAMES.full_match('KARVASED')
    ADJ_AND_NAMES.full_match('Pehmed')
    ADJ_AND_NAMES.full_match('koheVAD')
    ADJ_AND_NAMES.no_match('piilupart')
    ADJ_AND_NAMES.no_match('om')
    ADJ_AND_NAMES.no_match('vegas')
    ADJ_AND_NAMES.partial_match('uued PehmeD poognad', 'PehmeD')
    ADJ_AND_NAMES.partial_match('OMA TEEMA', 'OMA')
    ADJ_AND_NAMES.partial_match('kontsert Aigu Om ', 'Om')
    ADJ_AND_NAMES.test()
    #print(str(ADJ_AND_NAMES))
    
