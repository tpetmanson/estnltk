#
#   Preprocessing: adapting to tokenization requirements of TimexTagger
# 

import regex as re

from estnltk.taggers.text_segmentation.compound_token_tagger import ALL_1ST_LEVEL_PATTERNS
from estnltk.taggers.text_segmentation.compound_token_tagger import CompoundTokenTagger

def make_adapted_cp_tagger():
    '''Creates a version of standard CompoundTokenTagger which patterns have 
       been adapted to tokenization requirements of TimexTagger.
       Returns an instance of CompoundTokenTagger.
    '''
    redefined_number_pat_1 = \
        { 'comment': '*) A generic pattern for detecting long numbers (1 group) (corrected for timex tagger).',
          'example': '12,456',
          'pattern_type': 'numeric',
          '_group_': 0,
          '_priority_': (2, 1, 5),
          '_regex_pattern_': re.compile(r'''                             
                             \d+           # 1 group of numbers
                             (,\d+|\ *\.)  # + comma-separated numbers or period-ending
                             ''', re.X),
          'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(0))" }

    redefined_number_pat_2 = \
       { 'comment': '*) A generic pattern for detecting long numbers (2 groups, point-separated, followed by comma-separated numbers) (corrected for timex tagger).',
          'example': '67.123,456',
          'pattern_type': 'numeric',
          '_group_': 0,
          '_priority_': (2, 1, 3, 1),
          '_regex_pattern_': re.compile(r'''
                             \d+\.+\d+   # 2 groups of numbers
                             (,\d+)      # + comma-separated numbers
                             ''', re.X),
          'normalized': r"lambda m: re.sub(r'[\s\.]' ,'' , m.group(0))" }
    new_1st_level_patterns = []
    for pat in ALL_1ST_LEVEL_PATTERNS:
        if pat['comment'] == '*) Abbreviations of type <uppercase letter> + <numbers>;':
            # Skip this pattern
            continue 
        if pat['comment'] == '*) A generic pattern for detecting long numbers (1 group).':
            new_1st_level_patterns.append( redefined_number_pat_1 )
        elif pat['comment'] == '*) A generic pattern for detecting long numbers (2 groups, point-separated, followed by comma-separated numbers).':
            new_1st_level_patterns.append( redefined_number_pat_2 )
        else:
            new_1st_level_patterns.append( pat )
    assert len(new_1st_level_patterns)+1 == len(ALL_1ST_LEVEL_PATTERNS)
    return CompoundTokenTagger( patterns_1=new_1st_level_patterns )

# CompoundTokenTagger adapted to tokenization requirements of TimexTagger
CP_TAGGER_ADAPTED = make_adapted_cp_tagger()
