from estnltk.text import Span, Layer, Text
from estnltk.taggers import Tagger
from estnltk.vabamorf.morf import Vabamorf

from estnltk.rewriting.postmorph.vabamorf_corrector import VabamorfCorrectionRewriter

class VabamorfTagger(Tagger):
    description = 'Tags morphological analysis on words.'
    layer_name = None
    attributes = ('lemma', 'root', 'root_tokens', 'ending', 'clitic', 'form', 'partofspeech')
    depends_on = None
    configuration = None

    def __init__(self,
                 layer_name='morph_analysis',
                 postmorph_rewriter=VabamorfCorrectionRewriter(),
                 **kwargs):
        self.kwargs = kwargs
        self.instance = Vabamorf.instance()

        self.layer_name = layer_name
        self.postmorph_rewriter = postmorph_rewriter

        self.configuration = {'postmorph_rewriter':self.postmorph_rewriter.__class__.__name__}
        self.configuration.update(self.kwargs)

        self.depends_on = ['words']

        # TODO: Think long and hard about the default parameters
        # TODO: See also https://github.com/estnltk/estnltk/issues/66
        """
        words: list of str or str
            Either a list of pretokenized words or a string. In case of a string, it will be splitted using
            default behaviour of string.split() function.
        disambiguate: boolean (default: True)
            Disambiguate the output and remove incosistent analysis.
        guess: boolean (default: True)
            Use guessing in case of unknown words
        propername: boolean (default: True)
            Perform additional analysis of proper names.
        compound: boolean (default: True)
            Add compound word markers to root forms.
        phonetic: boolean (default: False)
            Add phonetic information to root forms.

        Returns
        -------
        list of (list of dict)
            List of analysis for each word in input.
        """

    def _get_wordlist(self, text:Text):
        result = []
        for word in text.words:
            if hasattr(word, 'normalized_form') and word.normalized_form != None:
                # If there is a normalized version of the word, add it
                # instead of word's text
                result.append(word.normalized_form)
            else:
                result.append(word.text)
        return result


    def tag(self, text: Text, return_layer=False) -> Text:
        wordlist = self._get_wordlist(text)
        if len(wordlist) > 15000:
            # if 149129 < len(wordlist) on Linux,
            # if  15000 < len(wordlist) < 17500 on Windows,
            # then self.instance.analyze(words=wordlist, **self.kwargs) raises
            # RuntimeError: CFSException: internal error with vabamorf
            analysis_results = []
            for i in range(0, len(wordlist), 15000):
                analysis_results.extend(self.instance.analyze(words=wordlist[i:i+15000], **self.kwargs))
        else:
            analysis_results = self.instance.analyze(words=wordlist, **self.kwargs)

        morph_attributes = self.attributes

        attributes = morph_attributes
        if self.postmorph_rewriter:
            attributes = attributes + ('word_normal',)
            morph = Layer(name='words',
              parent='words',
              ambiguous=True,
              attributes=attributes
              )
        else:
            morph = Layer(name=self.layer_name,
                          parent='words',
                          ambiguous=True,
                          attributes=morph_attributes
                          )

        for word, analyses in zip(text.words, analysis_results):
            for analysis in analyses['analysis']:
                span = morph.add_span(Span(parent=word))
                for attr in morph_attributes:
                    if attr == 'root_tokens':
                        # make it hashable for Span.__hash__
                        setattr(span, attr, tuple(analysis[attr]))
                    else:
                        setattr(span, attr, analysis[attr])
                if self.postmorph_rewriter:
                    setattr(span, 'word_normal', analyses['text'])
        if self.postmorph_rewriter:
            morph = morph.rewrite(source_attributes=attributes,
                                  target_attributes=morph_attributes, 
                                  rules=self.postmorph_rewriter,
                                  name=self.layer_name,
                                  ambiguous=True)
        if return_layer:
            return morph
        text[self.layer_name] = morph
        return text
        

# ==========================================================
# ==========================================================
#      Follows a refactoring of VabamorfTagger 
#               ( work in progress )
# ==========================================================
# ==========================================================

class VabamorfTagger2(Tagger):
    description   = 'Tags morphological analysis on words.'
    layer_name    = None
    attributes    = ('lemma', 'root', 'root_tokens', 'ending', 'clitic', 'form', 'partofspeech')
    depends_on    = None
    configuration = None

    def __init__(self,
                 layer_name='morph_analysis',
                 postmorph_rewriter=VabamorfCorrectionRewriter(),
                 **kwargs):
        self.kwargs = kwargs
        self.layer_name = layer_name
        
        # Validate morph's parameters 
        #  (parameters should be given either by the Resolver, or specified manually by the user)
        for param in ['disambiguate','guess','propername','phonetic','compound']:
            param_value = self.kwargs.get(param)
            assert isinstance(param_value, bool), \
                '(!) Parameter '+param+' should be bool, but is '+str(param_value)+' instead.\n'+\
                'Please specify boolean parameters disambiguate, guess, propername, phonetic, '+\
                'compound on initializing '+self.__class__.__name__+'.'
        
        self.postmorph_rewriter = postmorph_rewriter
        extra_attributes = None
        if postmorph_rewriter:
            extra_attributes = ['word_normal']
        self.instance = Vabamorf.instance()
        self.vabamorf_analyser      = VabamorfAnalyzer( vm_instance=self.instance, \
                                                        extra_attributes=extra_attributes )
        self.vabamorf_disambiguator = VabamorfDisambiguator( vm_instance=self.instance )
        

        self.configuration = {'postmorph_rewriter':self.postmorph_rewriter.__class__.__name__,
                              'vabamorf_analyser':self.vabamorf_analyser.__class__.__name__,
                              'vabamorf_disambiguator':self.vabamorf_disambiguator.__class__.__name__ }
        self.configuration.update(self.kwargs)

        self.depends_on = ['words', 'sentences']


    def tag(self, text: Text, return_layer=False) -> Text:
        # Fetch parameters
        disambiguate = self.kwargs.get('disambiguate')
        guess        = self.kwargs.get('guess')
        propername   = self.kwargs.get('propername')
        phonetic     = self.kwargs.get('phonetic')
        compound     = self.kwargs.get('compound')
        # --------------------------------------------
        #   Morphological analysis
        # --------------------------------------------
        self.vabamorf_analyser.tag( text, \
                                    guess=guess,\
                                    propername=propername,\
                                    phonetic=phonetic, \
                                    compound=compound )
        morph_layer = text[self.layer_name]
        # --------------------------------------------
        #   Post-processing
        # --------------------------------------------
        if self.postmorph_rewriter:
            # Fill in 'word_normal'
            for spanlist in morph_layer.spans:
                for span in spanlist:
                    setattr(span, 'word_normal', span.text)
        if self.postmorph_rewriter:
            morph_layer = morph_layer.rewrite(source_attributes=morph_layer.attributes,
                                              target_attributes=morph_layer.attributes,
                                              rules=self.postmorph_rewriter,
                                              name=self.layer_name,
                                              ambiguous=True)
            # TODO:
            #
            #   Now we have to re-attach the layer to the text, but 
            #        delattr(text, self.layer_name)
            #        text[self.layer_name] = morph_layer
            #   gives:
            #        AssertionError: Cant add a layer "morph_analysis" before adding its parent "morph_analysis"
            #
            #   However, the original VabamorfTagger also fails to populate the 
            #   attribute 'word_normal', or at least the attribute does not show up
            #   in the Notebook's output
            #
        # --------------------------------------------
        #   Morphological disambiguation
        # --------------------------------------------
        if disambiguate:
            self.vabamorf_disambiguator.tag(text)
        # --------------------------------------------
        #   Return layer or Text
        # --------------------------------------------
        # Return layer
        if return_layer:
            delattr(text, self.layer_name) # Remove layer from the text
            return morph_layer
        # Layer is already attached to the text, return it
        return text


# ========================================================
#    Utils for converting Vabamorf dict <-> EstNLTK Span
# ========================================================

def convert_morph_analysis_span_to_vm_dict( span ):
    attrib_dicts = {}
    # Get lists corresponding to attributes
    for attr in VabamorfTagger.attributes:
        attrib_dicts[attr] = getattr(span, attr)
    # Rewrite attributes in Vabamorf's analysis format
    # Collect analysis dicts
    nr_of_analyses = len(attrib_dicts['lemma'])
    word_dict = { 'text' : span.text[0], \
                  'analysis' : [] }
    for i in range( nr_of_analyses ):
        analysis = {}
        for attr in attrib_dicts.keys():
            attr_value = attrib_dicts[attr][i]
            if attr == 'root_tokens':
                attr_value = list(attr_value)
            analysis[attr] = attr_value
        word_dict['analysis'].append(analysis)
    return word_dict

    
def convert_vm_dict_to_morph_analysis_spans( vm_dict, word, layer_attributes=None ):
    spans = []
    current_attributes = \
        layer_attributes if layer_attributes else VabamorfTagger.attributes
    for analysis in vm_dict['analysis']:
        span = Span(parent=word)
        for attr in current_attributes:
            if attr in analysis:     
                # We have a Vabamorf's attribute
                if attr == 'root_tokens':
                    # make it hashable for Span.__hash__
                    setattr(span, attr, tuple(analysis[attr]))
                else:
                    setattr(span, attr, analysis[attr])
            else:
                # We have an extra attribute -- initialize with None
                setattr(span, attr, None)
        spans.append(span)
    return spans


# ===============================
#    VabamorfAnalyzer
# ===============================

class VabamorfAnalyzer(Tagger):
    description   = 'Analyzes texts morphologically. Note: resulting analyses can be ambiguous. '
    layer_name    = None
    attributes    = VabamorfTagger.attributes
    depends_on    = None
    configuration = None
    
    def __init__(self,
                 layer_name='morph_analysis',
                 extra_attributes=None,
                 vm_instance=None,
                 **kwargs):
        self.kwargs = kwargs
        if vm_instance:
            self.instance = vm_instance
        else:
            self.instance = Vabamorf.instance()
        self.extra_attributes = extra_attributes
        self.layer_name = layer_name
        
        self.configuration = {}
        self.configuration.update(self.kwargs)

        self.depends_on = ['words', 'sentences', 'morph_analysis']

    def _get_wordlist(self, text:Text):
        result = []
        for word in text.words:
            if hasattr(word, 'normalized_form') and word.normalized_form != None:
                # If there is a normalized version of the word, add it
                # instead of word's text
                result.append(word.normalized_form)
            else:
                result.append(word.text)
        return result

    def tag(self, text: Text, \
                  return_layer=False, \
                  guess=True, \
                  propername=True, \
                  compound=True, \
                  phonetic=False ) -> Text:
        # --------------------------------------------
        #   Use Vabamorf for morphological analysis
        # --------------------------------------------
        kwargs = {
            "disambiguate": False,  # perform analysis without disambiguation
            "guess"     : guess,\
            "propername": propername,\
            "compound"  : compound,\
            "phonetic"  : phonetic,\
        }
        wordlist = self._get_wordlist(text)
        analysis_results = []
        if len(wordlist) > 15000:
            # if 149129 < len(wordlist) on Linux,
            # if  15000 < len(wordlist) < 17500 on Windows,
            # then self.instance.analyze(words=wordlist, **self.kwargs) raises
            # RuntimeError: CFSException: internal error with vabamorf
            analysis_results = []
            for i in range(0, len(wordlist), 15000):
                analysis_results.extend(self.instance.analyze(words=wordlist[i:i+15000], **kwargs))
        else:
            analysis_results = self.instance.analyze(words=wordlist, **kwargs)
        # --------------------------------------------
        #   Store analysis results in a new layer     
        # --------------------------------------------
        # A) Create layer
        morph_attributes = self.attributes
        current_attributes = morph_attributes
        if self.extra_attributes:
            for extra_attr in self.extra_attributes:
                current_attributes = current_attributes + (extra_attr,)
        morph_layer = Layer(name=self.layer_name,
                            parent='words',
                            ambiguous=True,
                            attributes=current_attributes )
        # B) Populate layer        
        for word, analyses_dict in zip(text.words, analysis_results):
            # Convert from Vabamorf dict to a list of Spans 
            spans = \
                convert_vm_dict_to_morph_analysis_spans( \
                        analyses_dict, \
                        word, \
                        layer_attributes=current_attributes )
            # Attach spans
            for span in spans:
                if self.extra_attributes:
                    # Initialize all extra attributes with None
                    # (it is up to the end-user to fill these in)
                    for extra_attr in self.extra_attributes:
                        setattr(span, extra_attr, None)
                morph_layer.add_span( span )
        # --------------------------------------------
        #   Return layer or Text
        # --------------------------------------------
        if return_layer:
            return morph_layer
        text[self.layer_name] = morph_layer
        return text

# ===============================
#    VabamorfDisambiguator
# ===============================

class VabamorfDisambiguator(Tagger):
    description = 'Disambiguates morphologically analysed texts.'
    layer_name = None
    attributes = VabamorfTagger.attributes
    depends_on = None
    configuration = None

    def __init__(self,
                 layer_name='morph_analysis',
                 vm_instance=None,
                 **kwargs):
        self.kwargs = kwargs
        if vm_instance:
            self.instance = vm_instance
        else:
            self.instance = Vabamorf.instance()

        self.layer_name = layer_name

        self.configuration = {}
        self.configuration.update(self.kwargs)

        self.depends_on = ['words', 'sentences', 'morph_analysis']


    def tag(self, text: Text, \
                  return_layer=False ) -> Text:
        # --------------------------------------------
        #  Check for existence of required layers
        # --------------------------------------------
        for required_layer in self.depends_on:
            assert required_layer in text.layers, \
                '(!) Missing layer "'+str(required_layer)+'"!'
        # Take attributes from the input layer
        current_attributes = text[self.layer_name].attributes
        # --------------------------------------------
        #  Disambiguate sentence by sentence
        # --------------------------------------------
        morph_spans = text[self.layer_name].spans
        word_spans  = text['words'].spans
        morph_span_id = 0
        disambiguated_spans = []
        for sentence in text['sentences'].spans:
            # A) Collect all words/morph_analyses inside the sentence
            sentence_words       = []
            sentence_morph_spans = []
            sentence_morph_dicts = []
            while (morph_span_id < len(morph_spans)):
                span = morph_spans[morph_span_id]
                if sentence.start <= span.start and \
                    span.end <= sentence.end:
                    sentence_morph_spans.append( span )
                    word_morph_dict = \
                        convert_morph_analysis_span_to_vm_dict( span )
                    sentence_morph_dicts.append( word_morph_dict )
                    sentence_words.append( word_spans[morph_span_id] )
                    morph_span_id += 1
                elif sentence.end <= span.start:
                    break
            # B) Use Vabamorf for disambiguation
            disambiguated_dicts = self.instance.disambiguate(sentence_morph_dicts)
            # C) Convert Vabamorf's results to Spans
            for word, analysis_dict in zip(sentence_words, disambiguated_dicts):
                spans = \
                    convert_vm_dict_to_morph_analysis_spans( \
                        analysis_dict, \
                        word, \
                        layer_attributes=current_attributes )
                # TODO: what is missing here is carrying over 
                #       values of the extra attributes
                #       ... this can be tricky ...
                disambiguated_spans.extend( spans )
        # --------------------------------------------
        #   Create new layer and attach spans
        # --------------------------------------------
        morph_layer = Layer(name=self.layer_name,
                            parent='words',
                            ambiguous=True,
                            attributes=current_attributes
        )
        for span in disambiguated_spans:
            morph_layer.add_span(span)
        # --------------------------------------------
        #   Return layer or Text
        # --------------------------------------------
        # Return layer
        if return_layer:
            return morph_layer
        # Overwrite the old layer
        delattr(text, self.layer_name)
        text[self.layer_name] = morph_layer
        return text
