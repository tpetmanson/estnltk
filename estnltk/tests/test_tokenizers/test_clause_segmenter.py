from estnltk.text import Text
from estnltk.taggers import WordTagger
from estnltk.taggers import SentenceTokenizer
from estnltk.taggers import ClauseSegmenter
from estnltk.taggers import VabamorfTagger


def test_clause_segmenter_1():
    # Initialize segmenter
    segmenter = ClauseSegmenter()
    test_texts = [ 
        { 'text': 'Igaüks, kes traktori eest miljon krooni lauale laob, on huvitatud sellest, '+\
                  'et traktor meenutaks lisavõimaluste poolest võimalikult palju kosmoselaeva.',\
          'expected_clause_word_texts': [['Igaüks', 'on', 'huvitatud', 'sellest', ','], \
                                         [',', 'kes', 'traktori', 'eest', 'miljon', 'krooni', 'lauale', 'laob', ','], \
                                         ['et', 'traktor', 'meenutaks', 'lisavõimaluste', 'poolest', 'võimalikult', 'palju', 'kosmoselaeva', '.']] }, \
        { 'text': 'Kõrred, millel on toitunud viljasääse vastsed, jäävad õhukeseks.', \
          'expected_clause_word_texts': [['Kõrred', 'jäävad', 'õhukeseks', '.'], \
                                         [',', 'millel', 'on', 'toitunud', 'viljasääse', 'vastsed', ',']] }, \
        { 'text': 'Sest mis sa ikka ütled, kui seisad tükk aega kinniste tõkkepuude taga, ootad ja ootad, aga rongi ei tulegi.', \
          'expected_clause_word_texts': [['Sest', 'mis', 'sa', 'ikka', 'ütled', ','], \
                                         ['kui', 'seisad', 'tükk', 'aega', 'kinniste', 'tõkkepuude', 'taga', ','], \
                                         ['ootad', 'ja'], \
                                         ['ootad', ','], \
                                         ['aga', 'rongi', 'ei', 'tulegi', '.']] }, \
        { 'text': 'Pankurid Arti (LHV) ja Juri (Citadele) tulevad ja räägivad sellest, mida pank mõtleb laenu andmise juures.', \
          'expected_clause_word_texts': [['Pankurid', 'Arti', 'ja', 'Juri', 'tulevad', 'ja'], \
                                         ['(', 'LHV', ')'], \
                                         ['(', 'Citadele', ')'], \
                                         ['räägivad', 'sellest', ','], \
                                         ['mida', 'pank', 'mõtleb', 'laenu', 'andmise', 'juures', '.']] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences', 'morph_analysis'])
        segmenter.tag(text)
        # Collect results 
        clause_word_texts = \
            [[word.text for word in clause.words] for clause in text['clauses'].span_list]
        #print( clause_word_texts )
        # Check results
        assert clause_word_texts == test_text['expected_clause_word_texts']
    # Terminate Java process
    segmenter._java_process._process.terminate()


def test_clause_segmenter_2_missing_commas():
    # Initialize segmenter that is insensitive to missing commas
    segmenter = ClauseSegmenter(ignore_missing_commas=True)
    test_texts = [ 
        { 'text': 'Keegi teine ka siin ju kirjutas et ütles et saab ise asjadele järgi minna aga '+
                  'vastust seepeale ei tulnudki.', \
          'expected_clause_word_texts': [['Keegi', 'teine', 'ka', 'siin', 'ju', 'kirjutas'],\
                                         ['et', 'ütles'], \
                                         ['et', 'saab', 'ise', 'asjadele', 'järgi', 'minna'], \
                                         ['aga', 'vastust', 'seepeale', 'ei', 'tulnudki', '.']] }, \
        { 'text': 'Pritsimehed leidsid eest lõõmava kapotialusega auto mida läheduses parkinud masinate sohvrid eemale '+
                  'üritasid lükata kuid esialgu see ei õnnestunud sest autol oli käik sees.', \
          'expected_clause_word_texts': [['Pritsimehed', 'leidsid', 'eest', 'lõõmava', 'kapotialusega', 'auto'], \
                                         ['mida', 'läheduses', 'parkinud', 'masinate', 'sohvrid', 'eemale', 'üritasid', 'lükata'], \
                                         ['kuid', 'esialgu', 'see', 'ei', 'õnnestunud'], \
                                         ['sest', 'autol', 'oli', 'käik', 'sees', '.']] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences', 'morph_analysis'])
        segmenter.tag(text)
        # Collect results 
        clause_word_texts = \
            [[word.text for word in clause.words] for clause in text['clauses'].span_list]
        #print( clause_word_texts )
        # Check results
        assert clause_word_texts == test_text['expected_clause_word_texts']
    # Terminate Java process
    segmenter._java_process._process.terminate()


def test_apply_clause_segmenter_on_empty_text():
    # Applying clause segmenter on empty text should not produce any errors
    text = Text( '' )
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    
    segmenter = ClauseSegmenter()
    segmenter.tag(text)
    
    assert len(text.words) == 0
    assert len(text.sentences) == 0
    assert len(text.clauses) == 0

    # Terminate Java process
    segmenter._java_process._process.terminate()



def test_change_input_output_layer_names_of_clause_segmenter():
    # Tests that names of input / output layers of ClauseSegmenter can be changed
    word_tagger        = WordTagger(output_layer='my_words')
    sentence_tokenizer = SentenceTokenizer(input_words_layer='my_words', 
                                           output_layer='my_sentences')
    morftagger = VabamorfTagger(input_words_layer     ='my_words',
                                input_sentences_layer ='my_sentences',
                                layer_name            ='my_morf')
    segmenter = ClauseSegmenter(input_words_layer          ='my_words',
                                input_sentences_layer      ='my_sentences',
                                input_morph_analysis_layer ='my_morf',
                                output_layer          ='my_clauses')

    test_texts = [ 
        { 'text': 'Igaüks, kes traktori eest miljon krooni lauale laob, on huvitatud sellest, '+\
                  'et traktor meenutaks lisavõimaluste poolest võimalikult palju kosmoselaeva.',\
          'expected_clause_word_texts': [['Igaüks', 'on', 'huvitatud', 'sellest', ','], \
                                         [',', 'kes', 'traktori', 'eest', 'miljon', 'krooni', 'lauale', 'laob', ','], \
                                         ['et', 'traktor', 'meenutaks', 'lisavõimaluste', 'poolest', 'võimalikult', 'palju', 'kosmoselaeva', '.']] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['tokens', 'compound_tokens'])
        word_tagger.tag( text )
        sentence_tokenizer.tag( text )
        morftagger.tag( text )
        segmenter.tag( text )
        # Initial assertions
        assert 'my_clauses' in text.layers.keys()
        assert 'clauses' not in text.layers.keys()
        # Collect results 
        clause_word_texts = \
            [[word.text for word in clause.spans] for clause in text['my_clauses'].span_list]
        #print( clause_word_texts )
        # Check results
        assert clause_word_texts == test_text['expected_clause_word_texts']
    # Terminate Java process
    segmenter._java_process._process.terminate()

