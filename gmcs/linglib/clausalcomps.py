from gmcs.utils import TDLencode
from gmcs.utils import orth_encode
from gmcs.utils import merge_constraints, get_name
from gmcs.lib import TDLHierarchy

from gmcs.linglib import features

######################################################################
# Clausal Complements
#   Create the type definitions associated with the user's choices
#   about clasual complements.

######################################################################


def customize_clausalcomps(mylang,ch,lexicon,rules,irules):
    if not 'comps' in ch:
        return None

    add_complementizers_to_lexicon(lexicon,ch)
    add_complementizer_types_to_grammar(mylang,ch,rules)

def add_complementizer_types_to_grammar(mylang,ch,rules):
    mylang.set_section('complex')
    add_complementizer_supertype(mylang)

    for cs in ch.get('comps'):
        typename = add_complementizer_subtype(ch, cs, mylang,rules)
        customize_order(ch, cs, mylang, rules, typename)

def add_complementizer_subtype(ch, cs, mylang,rules):
    id = cs.full_key
    typename = id + '-comp-lex-item'
    mylang.add(typename + ' := comp-lex-item.', section='complex')
    # merge feature information in
    path = 'SYNSEM.LOCAL.CAT.VAL.COMPS.FIRST.LOCAL.CAT.HEAD.FORM'
    merge_constraints(choicedict=cs, mylang=mylang, typename=typename, path=path, key1='feat', key2='name', val='form')
    # Deal with differing word order (e.g. complementizer attaching at the left edge
    # in an otherwise SOV language.
    return typename

def customize_order(ch, cs, mylang, rules, typename):
    verbtypename = None
    if cs['clause-pos-extra'] == 'on':
        for v in ch.get('verb'):
            if v.get('valence') == cs.full_key:
                verbtypename = get_name(v) + '-' + cs.full_key + '-verb-lex'
    if ch.get('word-order') in ['sov', 'ovs', 'osv', 'vfinal']:
        if cs['comp-pos-before'] == 'on' or cs['clause-pos-extra'] == 'on':
            mylang.add('head :+ [ INIT bool ].', section='addenda')
            mylang.add('transitive-verb-lex := [ SYNSEM.LOCAL.CAT.HEAD.INIT - ].', merge=True)
            add_phrase_structure_rules(ch, cs, mylang, rules)
        if cs['comp-pos-before'] == 'on':
            mylang.add(typename + ' := [ SYNSEM.LOCAL.CAT.HEAD.INIT + ].', merge=True)
        else:
            mylang.add(typename + ' := [ SYNSEM.LOCAL.CAT.HEAD.INIT - ].', merge=True)
        if cs['clause-pos-extra'] == 'on':
            if not verbtypename:
                raise Exception('Clausalcomps.py customize_order could '
                                'not find a ctp verb type to go along with a clausal complement strategy.')
            mylang.add( verbtypename + ' := [ SYNSEM.LOCAL.CAT.HEAD.INIT + ]. ', merge=True)

    elif ch.get('word-order') in ['svo', 'vos', 'vso', 'v2'] and cs['comp-pos-after'] == 'on':
        mylang.add('head :+ [ INIT bool ].', section='addenda')
        mylang.add(typename + ' := [ SYNSEM.LOCAL.CAT.HEAD.INIT - ].', merge=True)
        mylang.add('transitive-verb-lex := [ SYNSEM.LOCAL.CAT.HEAD.INIT + ].', merge=True)
        add_phrase_structure_rules(ch, cs, mylang, rules)
        if cs['comp-pos-before'] == 'on':
            mylang.add(typename + ' := [ SYNSEM.LOCAL.CAT.HEAD.INIT - ].', merge=True)


def add_complementizer_supertype(mylang):
    mylang.add('comp-lex-item := raise-sem-lex-item & basic-one-arg &\
      [ SYNSEM.LOCAL.CAT [ HEAD comp &\
                                [ MOD < > ],\
                           VAL [ SPR < >,\
                                 SUBJ < >,\
                                 COMPS < #comps > ] ],\
        ARG-ST < #comps & \
                 [ LOCAL.CAT [ HEAD verb, MC -,\
                               VAL [ SUBJ < >,\
                                     COMPS < > ] ] ] > ].', section='complex')

'''
Add custom phrase-structure rules for case when the general order in the matrix clause
and the order of complementizer and its complement differ.
The function is very spaghetti at the moment.
It would be ideal to extract some clearer logic from it.
'''
def add_phrase_structure_rules(ch,cs,mylang,rules):
    if not cs['clause-pos-extra']:
        cs['clause-pos-same'] = 'on'
        cs['clause-pos-extra'] = 'off'
    if ch.get('word-order') in ['sov', 'ovs', 'osv', 'vfinal'] \
            and (cs['comp-pos-before'] == 'on' or cs['clause-pos-extra'] == 'on'):
        head = None
        if (cs['clause-pos-extra'] == 'on' and cs['comp-pos-before'] == 'on'):
            head = '+vc'
        elif cs['clause-pos-extra'] == 'on':
            head = 'verb'
        elif cs['comp-pos-before'] == 'on':
            head = 'comp'
        rules.add('head-comp := head-comp-phrase.')
        if not head:
            raise Exception('Clausalcomps.py add_phrase_structure_rules() '
                            'head could not be determined for the additional head-comp rule.')
        mylang.add('head-comp-phrase := basic-head-1st-comp-phrase & head-initial & '
                   '[ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD ' + head + ' & [ INIT + ] ].',section='phrases')
        # Need additional constraints to rule out comp-head licensing
        # unless order is flexible and allows both comp-head and head-comp here.
        if not (cs['comp-pos-after'] == 'on'and cs['clause-pos-same'] == 'on'):
            mylang.add('comp-head-phrase := [ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD.INIT - ].',section='phrases')
    elif ch.get('word-order') in ['svo', 'vos', 'vso', 'v2'] and cs['comp-pos-after'] == 'on':
        rules.add('comp-head := comp-head-phrase.')
        mylang.add('comp-head-phrase := basic-head-1st-comp-phrase & head-final & '
                   '[ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD comp & [ INIT - ] ].',section='phrases')
        if not cs['comp-pos-before'] == 'on':
            mylang.add('head-comp-phrase := [ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD.INIT + ] ].',section='phrases')

'''
Determine whether additional phrase structure rules
are needed to accommodate the complementizer attachment.
E.g. if the order is SOV but the complementizer
attaches in front of the complement clause,
additional rules will be needed. Similarly
if the order is SVO but the complementizer is
at the end of the clause (that I think is typologically not common).
'''
def complementizer_order_differs(ch,cs):
    if ch.get('wo') in ['sov', 'vfinal', 'osv', 'ovs'] and cs['comp-pos-before'] == 'on':
        return True
    if ch.get('wo') in ['svo', 'v2', 'vinitial', 'vso', 'vos'] and cs['comp-pos-after'] == 'on':
        return True

def add_complementizers_to_lexicon(lexicon,ch):
    lexicon.add_literal(';;; Complementizers')
    for comp_strategy in ch['comps']:
        id = comp_strategy.full_key
        typename = id + '-comp-lex-item'
        for complementizer in comp_strategy['complementizer']:
            orth = complementizer['orth']
            typedef = complementizer.full_key + ' := ' + typename + '& \
                          [ STEM < "' + orth + '" > ].'

            lexicon.add(typedef)


def add_ctp_supertype(ch, mainorverbtype,mylang):
    head = 'comp'
    for ccs in ch.get('comps'):
        if ccs['comp'] == 'opt':
            head = '+vc'
            break
    typedef = 'ctp-verb-lex := ' + mainorverbtype + '& clausal-second-arg-trans-lex-item &\
      [ SYNSEM.LOCAL.CAT.VAL.COMPS < #comps >,\
        ARG-ST < [ LOCAL.CAT.HEAD noun ],\
                 #comps &\
                 [ LOCAL.CAT [ VAL [ SPR < >, COMPS < > ],' \
                                                    'HEAD ' + head + ' ] ] > ].'
    mylang.add(typedef,section='verblex')

def update_verb_lextype(ch,verb, vtype):
    suffix = ''
    val = verb.get('valence')
    for css in ch.get('comps'):
        if val == css.full_key:
            suffix = val
    if suffix:
        name = vtype.split('-',1)[0]
        rest = vtype.split('-',1)[1]
        vtype = name + '-' + val + '-' + rest
    return vtype

def validate(ch,vr):
    if not ch.get('comps'):
        pass
    if ch.get('word-order') not in ['sov', 'ovs', 'vfinal', 'osv']:
        for css in ch.get('comps'):
            if css['clause-pos-extra'] == 'on':
                vr.err(css.full_key + '_clause-pos-extra',
                       'Extraposed clausal complements are only supported for word orders '
                       'where Objects precedes Verb (e.g. SOV).')
