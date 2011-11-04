from gmcs.utils import TDLencode

######################################################################
# customize_sentential_negation()
#   Create the type definitions associated with the user's choices
#   about sentential negation.

def customize_sentential_negation(mylang, ch, lexicon, rules):
  # JDC 2011-11-04 Nowadays this function just handles the syntactic
  # negation particles (auxes and adverbs) and (coming) interactions
  # between them also possible interactions with inflection(-al negation)
  #
  # inflectional negation is handled in the feature mapping part of the
  # morphotactic system (features.py).

  # ERB 2006-09-16 Calculate a bunch of derived properties based on the
  # inputs they gave for negation.  The same thing (e.g., negation via
  # inflection on the main verb) gives a very different output depending
  # on whether there are other options (negation via selected adverb)
  # and how they combine.

  # ERB 2009-01-23 This is all moot right now since the interim system
  # doesn't do the interaction between the two, but it probably won't
  # break anything to leave it in.

  # ERB 2009-07-01 It was adding defunct lex rules in at least some
  # cases, so taking it out for now.  This much still seems to be
  # required:
  
  # JDC 2011-10-23 ... not anymore, multineg is no longer
  # extant.  Bipartite negation is coming back, but probably under a new
  # architecture that doesn't use advAlone.

  #advAlone = ''
  #multineg = ch.get('multi-neg')
  #if ch.get('adv-neg') == 'on' or multineg == 'comp':
  #  advAlone = 'always'

  # ERB 2009-01-23 Migrating negation to modern customization system.
  # This intermediate version only does independent adverbs, and so
  # I'm removing ch.get('neg-adv') == 'ind-adv' as a second part of
  # the test below.

  if ch.get('adv-neg') == 'on' and ch.get('neg-exp') == '1':
    create_neg_adv_lex_item(mylang, ch, lexicon, rules, 1)

  if ch.get('neg-head-feature') == 'on':
    mylang.add('head :+ [ NEGATED luk ].', section='addenda')

  if ch.get('neg-exp') == '2':
    # see if we need to make any neg advs
    if ch.get('neg1-type')[0] == 'f' or \
      ch.get('neg2-type')[0] == 'f':
      create_neg_adv_lex_item(mylang, ch, lexicon, rules, 2)
      


def create_neg_adv_lex_item(mylang, ch, lexicon, rules, exp):
  mylang.set_section('otherlex')
  mylang.add('''neg-adv-lex := basic-scopal-adverb-lex &
                 [ SYNSEM.LOCAL.CAT [ VAL [ SPR < >,
                                            COMPS < >,
                                            SUBJ < > ],
                                      HEAD.MOD < [ LOCAL.CAT.HEAD verb ] > ]].''',
             'Type for negative adverbs.')


  # ERB 2006-10-06 Below was advAlone == 'always', but that seems wrong.
  # changing it to advAlone == 'never' being the case where we don't want
  # the adverb to be a modifier.

  # if advAlone == 'never':
  mylang.add_comment('neg-adv-lex',
    '''Constrain the MOD value of this adverb to keep\n
    it from modifying the kind of verbs which can select it,\n
    To keep spurious parses down, as a starting point, we have\n
    assumed that it only modifies verbs (e.g., non-finite verbs).''')
  if exp == 1:
    if ch.get('neg-order') == 'before':
      mylang.add('neg-adv-lex := [ SYNSEM.LOCAL.CAT.POSTHEAD - ].')
    elif ch.get('neg-order') == 'after':
      mylang.add('neg-adv-lex := [ SYNSEM.LOCAL.CAT.POSTHEAD + ].')

    if ch.get('neg-mod') == 's':
      mylang.add('''neg-adv-lex := [ SYNSEM.LOCAL.CAT.HEAD.MOD.FIRST.LOCAL.CAT.VAL [ SUBJ null,
                                                                                     COMPS null ]].''')
    elif ch.get('neg-mod') == 'vp':
      mylang.add('''neg-adv-lex := [ SYNSEM.LOCAL.CAT.HEAD.MOD.FIRST.LOCAL.CAT.VAL [ SUBJ cons,
                                                                                     COMPS null ]].''')
    elif ch.get('neg-mod') == 'v':
      mylang.add('''neg-adv-lex := [ SYNSEM.LOCAL.CAT.HEAD.MOD.FIRST.LIGHT + ].''')
  elif exp == 2:
    if ch.get('neg1-type')[0] == 'f':
      mylang.add('neg1-adv-lex := neg-adv-lex.')
      if ch.get('neg1-order') == 'before':
        mylang.add('neg1-adv-lex := [ SYNSEM.LOCAL.CAT.POSTHEAD - ].')
      elif ch.get('neg1-order') == 'after':
        mylang.add('neg1-adv-lex := [ SYNSEM.LOCAL.CAT.POSTHEAD + ].')

      if ch.get('neg-mod') == 's':
        mylang.add('''neg1-adv-lex := [ SYNSEM.LOCAL.CAT.HEAD.MOD.FIRST.LOCAL.CAT.VAL [ SUBJ null,
                                                                                       COMPS null ]].''')
      elif ch.get('neg1-mod') == 'vp':
        mylang.add('''neg1-adv-lex := [ SYNSEM.LOCAL.CAT.HEAD.MOD.FIRST.LOCAL.CAT.VAL [ SUBJ cons,
                                                                                       COMPS null ]].''')
      elif ch.get('neg1-mod') == 'v':
        mylang.add('''neg1-adv-lex := [ SYNSEM.LOCAL.CAT.HEAD.MOD.FIRST.LIGHT + ].''')
    if ch.get('neg2-type')[0] == 'f':
      mylang.add('neg2-adv-lex := neg-adv-lex.')
      if ch.get('neg2-order') == 'before':
        mylang.add('neg2-adv-lex := [ SYNSEM.LOCAL.CAT.POSTHEAD - ].')
      elif ch.get('neg2-order') == 'after':
        mylang.add('neg2-adv-lex := [ SYNSEM.LOCAL.CAT.POSTHEAD + ].')

      if ch.get('neg2-mod') == 's':
        mylang.add('''neg2-adv-lex := [ SYNSEM.LOCAL.CAT.HEAD.MOD.FIRST.LOCAL.CAT.VAL [ SUBJ null,
                                                                                       COMPS null ]].''')
      elif ch.get('neg2-mod') == 'vp':
        mylang.add('''neg2-adv-lex := [ SYNSEM.LOCAL.CAT.HEAD.MOD.FIRST.LOCAL.CAT.VAL [ SUBJ cons,
                                                                                       COMPS null ]].''')
      elif ch.get('neg2-mod') == 'v':
        mylang.add('''neg2-adv-lex := [ SYNSEM.LOCAL.CAT.HEAD.MOD.FIRST.LIGHT + ].''')

    mylang.add('verb-lex := [ SYNSEM.LOCAL.CAT.HC-LIGHT - ].','''verb-lex is HC-LIGHT - to allow us to pick out\n
    lexical Vs for V-level attachment of negative adverbs.''')
    

  # ERB 2006-09-22 Validation should really make sure we have a value of
  # neg-adv-orth before we get here, but just in case, checking first, since
  # the script gets really unhappy if I try to write to an empty type.

  if(ch.get('neg-adv-orth')):
    orth = ch.get('neg-adv-orth')
    lexicon.add(TDLencode(orth) + ' := neg-adv-lex &\
                [ STEM < \"'+ orth +'\" >,\
                  SYNSEM.LKEYS.KEYREL.PRED \"neg_rel\" ].')

  if(ch.get('neg1-adv-orth')):
    orth = ch.get('neg1-adv-orth')
    lexicon.add(TDLencode(orth) + '1 := neg1-adv-lex &\
                [ STEM < \"'+ orth +'\" >,\
                  SYNSEM.LKEYS.KEYREL.PRED \"neg_rel\" ].')

  if(ch.get('neg2-adv-orth')):
    orth = ch.get('neg2-adv-orth')
    lexicon.add(TDLencode(orth) + '2 := neg2-adv-lex &\
                [ STEM < \"'+ orth +'\" >,\
                  SYNSEM.LKEYS.KEYREL.PRED \"neg_rel\" ].')


  # ERB 2006-10-06 And of course we need the head-modifier rules, if we're
  # going to have an independent modifier.  While we're at it, we need to
  # contrain the MOD value on the rest of the head types to keep them
  # from going nuts.

  #if advAlone != 'never':
  rules.add('head-adj-int := head-adj-int-phrase.',
            'Rule instances for head-modifier structures. Corresponding types\n' +
            'are defined in matrix.tdl.  The matrix customization script did\n' +
            'not need to add any further constraints, so no corresponding tyes\n' +
            'appear in ' + ch.get('language').lower() + '.tdl')
  rules.add('adj-head-int := adj-head-int-phrase.')
  rules.add('head-adj-scop := head-adj-scop-phrase.')
  rules.add('adj-head-scop := adj-head-scop-phrase.')

  mylang.add('+nvcdmo :+ [ MOD < > ].',
             'This grammar includes head-modifier rules.  To keep\n' +
             'out extraneous parses, constrain the value of MOD on\n' +
             'various subtypes of head.  This may need to be loosened later.\n' +
             'This constraint says that only adverbs, adjectives,\n' +
             'and adpositions can be modifiers.',
             section='addenda')



##################
### VALIDATION ###
##################

def validate(ch, vr):
  if ch.get('infl-neg', default=False):
    for aux in ch.get('aux', []):
      for cf in aux.get('compfeature', []):
        if cf.get('name') == 'negation':
          mess = 'When inflectional negation is selected ' +\
                 '[negation +] should only be found on bound morphemes.'
          vr.err(cf.full_key + '_name', mess)
      for f in aux.get('feat', []):
        if f.get('name') == 'negation':
          mess = 'When inflectional negation is selected ' +\
                 '[negation +] should only be found on bound morphemes.'
          vr.err(f.full_key + '_name', mess)
    for verb in ch.get('verb', []):
      for cf in verb.get('compfeature', []):
        if cf.get('name') == 'negation':
          mess = 'When inflectional negation is selected ' +\
                 '[negation +] should only be found on bound morphemes.'
          vr.err(cf.full_key + '_name', mess)
      for f in verb.get('feat', []):
        if f.get('name') == 'negation':
          mess = 'When inflectional negation is selected ' +\
                 '[negation +] should only be found on bound morphemes.'
          vr.err(f.full_key + '_name', mess)

  neginfltype = ch.get('neg-infl-type')
#  negseladv = ch.get('neg-sel-adv')

  if ch.get('neg-aux', default=False):
    has_neg_aux = False
    for aux in ch.get('aux', []):
      if aux.get('name') == 'neg-aux':
        has_neg_aux = True
        break
    if has_neg_aux == False:
      vr.warn('neg-aux',
              'You\'ve selected neg-aux but there is no corresponding ' +\
              'type in the lexicon.')
  # ERB 2009-01-23 Commenting out the following because infl-neg is
  # now handled with customize_inflection.  We should eventually give
  # a warning if infl-neg is selected but no lexical rules actually
  # use it.  I think it would make sense for that warning to go
  # on the negation page.

  # If affix is indicated, must select prefix/suffix and
  # main/aux/either and give form.
#   if (ch.get('infl-neg') == 'on'):
#     if (not ch.get('neg-infl-type')):
#       mess = 'If sentential negation is expressed through affixation, you must specify what the affix attaches to.'
#       vr.err('neg-infl-type', mess)
#     if (not ch.get('neg-aff')):
#       mess = 'If sentential negation is expressed through affixation, you must specify whether its a prefix or a suffix'
#       vr.err('neg-aff', mess)
#     if (not ch.get('neg-aff-orth')):
#       mess = 'If sentential negation is expressed through affixation, you must specify the form of the affix'
#       vr.err('neg-aff-orth', mess)
#     # If aux is selected then has-aux = 'yes' must be chosen in word order section
#     if ((neginfltype == 'aux' or neginfltype == 'aux-main') and ch.get('has-aux') != 'yes'):
#         mess = 'You have not indicated on the word order page that your language has auxiliaries.'
#         vr.err('neg-infl-type', mess)

  # If adverb is indicated, must lexical entry, what it modifies, and
  # ind/selected modifier -- now only applicable under single negation
  # bipartite negs need to validate this for themeselves
  if (ch.get('adv-neg') == 'on') and (ch.get('neg-exp') == '1'):
#    if (not ch.get('neg-adv')):
#      mess = 'If sentential negation is expressed through an adverb, you must specify whether the adverb is a selected complement or an independent modifier.'
#      vr.err('neg-adv', mess)
#    if (ch.get('neg-adv') == 'ind-adv'):
    if (not ch.get('neg-mod')):
      mess = 'If sentential negaton is expressed through an adverb, ' +\
             'you must specify what type of constituent the adverb modifies.'
      vr.err('neg-mod', mess)
    if (not ch.get('neg-order')):
      mess = 'If sentential negaton is expressed through an adverb, ' +\
             'you must specify what side of its host the adverb attaches to.'
      vr.err('neg-order', mess)
    if (not ch.get('neg-adv-orth')):
      mess = 'If sentential negation is expressed through an adverb, ' +\
             'you must specify the form of the adverb.'
      vr.err('neg-adv-orth', mess)

   # If aux is selected then has-aux = 'yes' must be chosen in word
   # order section
#    if ((negseladv == 'aux' or negseladv == 'main-aux') and
#        ch.get('has-aux') != 'yes'):
#       mess = 'You have not indicated on the word order page ' +\
#             'that your language has auxiliaries.'
#     vr.err('neg-sel-adv', mess)

   # ERB 2009-01-23 Currently not possible to say how they combine.

#   # If both strategies are checked, then they must say how they combine:
#   if ((ch.get('infl-neg') == 'on') and (ch.get('adv-neg') == 'on')):
#     if (not ch.get('multi-neg')):
#       mess = 'If you have selected both affix and adverb realizations of sentential negation, you must specify how they interact.'
#       vr.err('multi-neg', mess)
