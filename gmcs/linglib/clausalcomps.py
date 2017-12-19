from gmcs.utils import merge_constraints, get_name

from gmcs import constants

######################################################################
# Clausal Complements
#   Create the type definitions associated with the user's choices
#   about clasual complements.

######################################################################

# Constants (specifict to this module)
COMPS = 'comps' # choice name for clausal complement strategies
COMP = 'comp' # reserved head name for complementizers; should be a constant on some other page?
              # Also, the name for the choice for complementizer of a clausal complement strategy.
CLAUSE_POS_EXTRA = 'clause-pos-extra' # Choice name for extraposed complement
CLAUSE_POS_SAME = 'clause-pos-same' # Choice name for default noun position complement

COMP_POS_BEFORE = 'comp-pos-before' # Choice name for complementizer attaching before embedded clause
COMP_POS_AFTER = 'comp-pos-after' # Choice name for complementizer attaching after embedded clause

COMPLEX = 'complex' # TDL file section name for complementizer lexical items

COMP_LEX_ITEM_DEF = 'comp-lex-item := raise-sem-lex-item & basic-one-arg &\
      [ SYNSEM.LOCAL.CAT [ HEAD comp &\
                                [ MOD < > ],\
                           VAL [ SPR < >,\
                                 SUBJ < >,\
                                 COMPS < #comps > ] ],\
        ARG-ST < #comps & \
                 [ LOCAL.CAT [ HEAD verb, MC -,\
                               VAL [ SUBJ < >,\
                                     COMPS < > ] ] ] > ].'

FORM = 'FORM' # FORM feature name
FORM_PATH = 'SYNSEM.LOCAL.CAT.VAL.COMPS.FIRST.LOCAL.CAT.HEAD' # FORM feature path

# Note: the below lists do not include V2
OV_ORDERS = ['sov', 'ovs', 'osv', 'vfinal']
VO_ORDERS = ['svo', 'vos', 'vso', 'vinitial']

CLAUSALCOMP = 'clausalcomp'


# Error messages:
EXTRA_VO = 'Invalid choice: a VO order and extraposed clausal complement. '\
                            'You must choose same as nouns position of the complement clause.'\
                            'The only supporded word orders for extraposed complements are OV orders.'

def customize_clausalcomps(mylang,ch,lexicon,rules,irules):
    if not COMPS in ch:
        return None
    add_complementizers_to_lexicon(lexicon,ch)
    add_types_to_grammar(mylang,ch,rules)

def add_types_to_grammar(mylang,ch,rules):
    mylang.set_section(COMPLEX)
    add_complementizer_supertype(mylang)
    init = False # Has the INIT feature been used?
    # Which is the general rule and which needs to be added?
    general, additional = determine_head_comp_rule_type(ch.get(constants.WORD_ORDER))
    for cs in ch.get(COMPS):
        typename = add_complementizer_subtype(cs, mylang)
        init = customize_order2(ch, cs, mylang, rules, typename, init,general,additional)

def add_complementizer_subtype(cs, mylang):
    id = cs.full_key
    typename = id + '-comp-lex-item'
    mylang.add(typename + ' := comp-lex-item.', section=COMPLEX)
    # merge feature information in
    path = FORM_PATH + '.' + FORM
    merge_constraints(choicedict=cs, mylang=mylang, typename=typename,
                      path=path, key1='feat', key2='name', val='form')
    return typename

# Deal with differing word order (e.g. complementizer attaching at the left edge
# in an otherwise SOV language).
def customize_order(ch, cs, mylang, rules, typename, init):
    verbtypename = None
    if cs[CLAUSE_POS_EXTRA] == constants.ON:
        for v in ch.get(constants.VERB):
            if v.get(constants.VALENCE) == cs.full_key:
                verbtypename = get_name(v) + '-' + cs.full_key + '-verb-lex'
    if ch.get(constants.WORD_ORDER) in OV_ORDERS:
        if cs[COMP_POS_BEFORE] == constants.ON or cs[CLAUSE_POS_EXTRA] == constants.ON:
            if not init:
                mylang.add('head :+ [ INIT bool ].', section='addenda')
                init = True
            mylang.add('transitive-verb-lex := [ SYNSEM.LOCAL.CAT.HEAD.INIT - ].', merge=True)
            #TODO this should better be called separately, from outside this function
            add_phrase_structure_rules(ch, cs, mylang, rules)
        if cs[COMP_POS_BEFORE] == constants.ON:
            mylang.add(typename + ' := [ SYNSEM.LOCAL.CAT.HEAD.INIT + ].', merge=True)
        else:
            mylang.add(typename + ' := [ SYNSEM.LOCAL.CAT.HEAD.INIT - ].', merge=True)
        if cs[CLAUSE_POS_EXTRA] == constants.ON:
            if not verbtypename:
                raise Exception('Clausalcomps.py customize_order could '
                                'not find a clausal-complement verb type to go along '
                                'with a clausal complement strategy.')
            mylang.add( verbtypename + ' := [ SYNSEM.LOCAL.CAT.HEAD.INIT + ]. ', merge=True)

    elif ch.get(constants.WORD_ORDER) in VO_ORDERS and cs[COMP_POS_AFTER] == constants.ON:
        if not init:
            mylang.add('head :+ [ INIT bool ].', section='addenda')
            init = True
        mylang.add(typename + ' := [ SYNSEM.LOCAL.CAT.HEAD.INIT - ].', merge=True)
        mylang.add('transitive-verb-lex := [ SYNSEM.LOCAL.CAT.HEAD.INIT + ].', merge=True)
        #TODO this should better be called separately, from outside this function
        add_phrase_structure_rules(ch, cs, mylang, rules)
        if cs[COMP_POS_BEFORE] == constants.ON: #TODO this line repeats line 66 above
            mylang.add(typename + ' := [ SYNSEM.LOCAL.CAT.HEAD.INIT - ].', merge=True)
    return init

def add_complementizer_supertype(mylang):
    mylang.add(COMP_LEX_ITEM_DEF, section=COMPLEX)


'''
Add and modify head-complement rules depending
on what kind of word order variations clausal complements
exhibit.
'''
def customize_order2(ch, cs, mylang, rules, typename, init, general, additional):
    wo = ch.get(constants.WORD_ORDER)
    if not order_customization_needed(wo,cs):
        return init
    init_value = '+' if additional == constants.HEAD_COMP else '-'
    default_init_value = '-' if init_value == '+' else '+'
    # What is the head of the added rule's head daughter?
    head = determine_head(wo,cs)
    # Do I need to modify the general rule? (== Is INIT feature needed?)
    if not init:
        init = init_needed(wo,cs,mylang)
    if init and head:
        # If INIT feature was used before or is needed now:
        # Which lexical types need to be constrained wrt INIT?
        constrain_lex_items(head,ch,cs,typename,init_value,default_init_value,mylang)
    # Constrain added and general rule wrt head and INIT
    constrain_head_comp_rules(mylang,rules,init,init_value,default_init_value,head,general,additional)
    return init

'''
There are two combinations of choices for which no action is needed:
complementizers and clausal verbs can just use the default head-comp rule.
'''
def order_customization_needed(wo,cs):
    if wo in OV_ORDERS and cs[COMP_POS_AFTER] and cs[CLAUSE_POS_SAME] \
            and not cs[COMP_POS_BEFORE] and not cs[CLAUSE_POS_EXTRA]:
        return False
    if wo in VO_ORDERS and cs[COMP_POS_BEFORE] and cs[CLAUSE_POS_SAME] \
            and not cs[COMP_POS_AFTER] and not cs[CLAUSE_POS_EXTRA]:
        return False
    return True

def constrain_head_comp_rules(mylang,rules,init,init_value, default_init_value,head,general,additional):
    rules.add(additional + ' := ' + additional + '-phrase.', merge=True) #TODO: But this should only be done once!
    supertype = 'head-initial' if additional == constants.HEAD_COMP else 'head-final'
    mylang.add(additional + '-phrase := basic-head-1st-comp-phrase & ' + supertype + '.'
               ,section = 'phrases',merge=True)
    if head:
        mylang.add(additional + '-phrase := [ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD ' + head +' ].'
                   ,merge=True)
    if init:
        mylang.add(additional +
                   '-phrase := [ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD.INIT ' + init_value + ' ].',
                   merge=True)
        mylang.add(general + '-phrase := [ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD.INIT ' + default_init_value + ' ].',
                   merge=True)

def find_clausalverb_typename(ch,cs):
    for v in ch.get(constants.VERB):
        if v.get(constants.VALENCE) == cs.full_key:
            return get_name(v) + '-' + cs.full_key + '-verb-lex'


'''
This function assumes that INIT feature is needed.
It will constrain verbs and/or complementizers with respect to INIT feature.
'''
def constrain_lex_items(head,ch,cs,comptype, init_value, default_init_value,mylang):
    clausalverb = find_clausalverb_typename(ch,cs)
    if head == '+vc':
        if cs[CLAUSE_POS_EXTRA] and not cs[CLAUSE_POS_SAME]:
            constrain_lexitem_for_init(clausalverb,init_value,mylang)
        if cs[COMP_POS_BEFORE] and not cs[COMP_POS_AFTER] and ch.get(constants.WORD_ORDER) in OV_ORDERS:
            constrain_lexitem_for_init(comptype,init_value,mylang)
    elif head == constants.VERB:
        if cs[CLAUSE_POS_EXTRA] and not cs[CLAUSE_POS_SAME]:
            constrain_lexitem_for_init(clausalverb,init_value,mylang)
        mylang.add('transitive-verb-lex := [ SYNSEM.LOCAL.CAT.HEAD.INIT ' + default_init_value + ' ].'
                   , merge=True)
    elif head == 'comp':
        if cs[COMP_POS_BEFORE] and not cs[COMP_POS_AFTER] and ch.get(constants.WORD_ORDER) in OV_ORDERS:
            mylang.add(comptype + ':= [ SYNSEM.LOCAL.CAT.HEAD.INIT ' + init_value + ' ].')


def constrain_lexitem_for_init(typename, init_value,mylang):
    mylang.add( typename + ' := [ SYNSEM.LOCAL.CAT.HEAD.INIT ' + init_value + ' ]. ',
                            merge=True)

'''
Determine whether the head of the additional head-comp rule
should be constrained to just verbs, just complementizers, or both.
'''
def determine_head(wo,cs):
    head = None
    if wo in OV_ORDERS:
        if cs[COMP_POS_BEFORE]:
            if cs[CLAUSE_POS_EXTRA]:
                head = '+vc'
            elif cs[CLAUSE_POS_SAME]:
                head = 'comp'
        elif cs[COMP_POS_AFTER]:
            if cs[CLAUSE_POS_EXTRA]:
                head = 'verb'
    return head

'''
Determine which head-complement rule is the generally applicable one
and which one would be the secondary one, applicable only to complementizers
and/or clausal complement verbs.
'''
def determine_head_comp_rule_type(wo):
    if wo == 'v2' or wo == 'free':
        # Note: it is possible that not much is needed here, as v2 and free are very flexible
        raise Exception('Currently only supporting strict VO/OV orders, but not V2 or free.')
    return (constants.HEAD_COMP, constants.COMP_HEAD) if wo in VO_ORDERS \
        else (constants.COMP_HEAD,constants.HEAD_COMP)

'''
Given word order and clausal complement choices,
determine whether the INIT feature will be used,
for this particular clausal complement strategy.
Note that once the INIT feaure has been used for
one strategy, you will need to keep it in mind
for all of them, so you will need to stop
calling this function once it returns True.
'''

def init_needed(wo, cs,mylang):
    if wo in OV_ORDERS:
        if cs[COMP_POS_BEFORE]:
            if not cs[COMP_POS_AFTER]: # complementizer before clause only
                mylang.add('head :+ [ INIT bool ].', section='addenda')
                return True
            else: # complementizer both before and after clause
                res = cs[CLAUSE_POS_SAME] == constants.ON and not cs[CLAUSE_POS_EXTRA] == constants.ON
                if res:
                    mylang.add('head :+ [ INIT bool ].', section='addenda')
                return res
        elif cs[COMP_POS_AFTER]:
            res = cs[CLAUSE_POS_EXTRA] == constants.ON
            if res:
                mylang.add('head :+ [ INIT bool ].', section='addenda')
            return res
    elif wo in VO_ORDERS:
        if not cs[CLAUSE_POS_SAME]:
            raise Exception(EXTRA_VO)
        res = cs[COMP_POS_AFTER] == constants.ON and not cs[COMP_POS_BEFORE] == constants.ON
        if res:
            mylang.add('head :+ [ INIT bool ].', section='addenda')
        return res


'''
Add custom phrase-structure rules for case when the general order in the matrix clause
and the order of complementizer and its complement differ.
The function is very spaghetti at the moment.
It would be ideal to extract some clearer logic from it.
'''
def add_phrase_structure_rules(ch,cs,mylang,rules):
    if not cs[CLAUSE_POS_EXTRA]:
        cs[CLAUSE_POS_SAME] = constants.ON
        cs[CLAUSE_POS_EXTRA] = 'off'
    if ch.get(constants.WORD_ORDER) in OV_ORDERS \
            and (cs[COMP_POS_BEFORE] == constants.ON or cs[CLAUSE_POS_EXTRA] == constants.ON):
        head = None
        if (cs[CLAUSE_POS_EXTRA] == constants.ON and cs[COMP_POS_BEFORE] == constants.ON):
            head = '+vc'
        elif cs[CLAUSE_POS_EXTRA] == constants.ON:
            head = 'verb'
        elif cs[COMP_POS_BEFORE] == constants.ON:
            head = 'comp'
        rules.add('head-comp := head-comp-phrase.')
        if not head:
            raise Exception('Clausalcomps.py add_phrase_structure_rules() '
                            'head could not be determined for the additional head-comp rule.')
        mylang.add('head-comp-phrase := basic-head-1st-comp-phrase & head-initial & '
                   '[ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD ' + head + ' & [ INIT + ] ].',section='phrases')
        # Need additional constraints to rule out comp-head licensing
        # unless order is flexible and allows both comp-head and head-comp here.
        if not (cs[COMP_POS_AFTER] == constants.ON and cs[CLAUSE_POS_SAME] == constants.ON):
            #TODO: Does this mean all other lexical types should be made INIT - as well?
            # Nouns, auxiliaries, what else?
            mylang.add('comp-head-phrase := [ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD.INIT - ].',section='phrases')
    #TODO should v2 be mentioned below as well?
    elif ch.get(constants.WORD_ORDER) in VO_ORDERS and cs[COMP_POS_AFTER] == constants.ON:
        rules.add('comp-head := comp-head-phrase.')
        mylang.add('comp-head-phrase := basic-head-1st-comp-phrase & head-final & '
                   '[ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD comp & [ INIT - ] ].',section='phrases')
        if not cs[COMP_POS_BEFORE] == constants.ON:
            mylang.add('head-comp-phrase := [ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD.INIT + ] ].',section='phrases')


def add_complementizers_to_lexicon(lexicon,ch):
    lexicon.add_literal(';;; Complementizers')
    for comp_strategy in ch[COMPS]:
        id = comp_strategy.full_key
        typename = id + '-comp-lex-item'
        for complementizer in comp_strategy['complementizer']:
            orth = complementizer['orth']
            typedef = complementizer.full_key + ' := ' + typename + '& \
                          [ STEM < "' + orth + '" > ].'

            lexicon.add(typedef)


def add_clausalcomp_verb_supertype(ch, mainorverbtype,mylang):
    head = 'comp'
    for ccs in ch.get(COMPS):
        if ccs[COMP] == 'opt':
            head = '+vc'
            break
    typedef = CLAUSALCOMP + '-verb-lex := ' + mainorverbtype + '& clausal-second-arg-trans-lex-item &\
      [ SYNSEM.LOCAL.CAT.VAL.COMPS < #comps >,\
        ARG-ST < [ LOCAL.CAT.HEAD noun ],\
                 #comps &\
                 [ LOCAL.CAT [ VAL [ SPR < >, COMPS < > ],' \
                                                    'HEAD ' + head + ' ] ] > ].'
    mylang.add(typedef,section='verblex')

def update_verb_lextype(ch,verb, vtype):
    suffix = ''
    val = verb.get(constants.VALENCE)
    for css in ch.get(COMPS):
        if val == css.full_key:
            suffix = val
    if suffix:
        name = vtype.split('-',1)[0]
        rest = vtype.split('-',1)[1]
        vtype = name + '-' + val + '-' + rest
    return vtype

def validate(ch,vr):
    if not ch.get(COMPS):
        pass
    if ch.get(constants.WORD_ORDER) not in OV_ORDERS:
        for css in ch.get(COMPS):
            if css[CLAUSE_POS_EXTRA] == constants.ON:
                vr.err(css.full_key + '_' + CLAUSE_POS_EXTRA,
                       'Extraposed clausal complements are only supported for word orders '
                       'where Object precedes Verb (e.g. SOV).')
