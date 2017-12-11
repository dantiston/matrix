from gmcs.utils import TDLencode
from gmcs.utils import orth_encode
from gmcs.utils import merge_constraints
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
        add_complementizer_subtype(ch, cs, mylang,rules)


def add_complementizer_subtype(ch, cs, mylang,rules):
    id = cs.full_key
    typename = id + '-comp-lex-item'
    mylang.add(typename + ' := comp-lex-item.', section='complex')
    # merge feature information in
    path = 'SYNSEM.LOCAL.CAT.VAL.COMPS.FIRST.LOCAL.CAT.HEAD.FORM'
    merge_constraints(choicedict=cs, mylang=mylang, typename=typename, path=path, key1='feat', key2='name', val='form')
    # Deal with differing word order (e.g. complementizer attaching at the left edge
    # in an otherwise SOV language.
    customize_complementizer_order(ch, cs, mylang, rules, typename)


'''
Deal with differing word order (e.g. complementizer attaching at the left edge
in an otherwise SOV language.
'''
def customize_complementizer_order(ch, cs, mylang, rules, typename):
    if ch.get('word-order') in ['sov', 'ovs', 'osv', 'vfinal'] and cs['comp-pos-before'] == 'on':
        mylang.add('head :+ [ INIT bool ].', section='addenda')
        mylang.add(typename + ' := [ SYNSEM.LOCAL.CAT.HEAD.INIT + ].', merge=True)
        mylang.add('transitive-verb-lex := [ SYNSEM.LOCAL.CAT.HEAD.INIT - ].', merge=True)
        add_phrase_structure_rules(ch, cs, mylang, rules)
    elif ch.get('word-order') in ['svo', 'vos', 'vso', 'v2'] and cs['comp-pos-after'] == 'on':
        mylang.add('head :+ [ INIT bool ].', section='addenda')
        mylang.add(typename + ' := [ SYNSEM.LOCAL.CAT.HEAD.INIT - ].', merge=True)
        mylang.add('transitive-verb-lex := [ SYNSEM.LOCAL.CAT.HEAD.INIT + ].', merge=True)
        add_phrase_structure_rules(ch, cs, mylang, rules)


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
'''
def add_phrase_structure_rules(ch,cs,mylang,rules):
    if ch.get('word-order') in ['sov', 'ovs', 'osv', 'vfinal'] and cs['comp-pos-before'] == 'on':
        rules.add('head-comp := head-comp-phrase.')
        mylang.add('head-comp-phrase := basic-head-1st-comp-phrase & head-initial & '
                   '[ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD comp & [ INIT + ] ].',section='phrases')
        mylang.add('comp-head-phrase := [ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD.INIT - ] ].',section='phrases')
    elif ch.get('word-order') in ['svo', 'vos', 'vso', 'v2'] and cs['comp-pos-after'] == 'on':
        rules.add('comp-head := comp-head-phrase.')
        mylang.add('comp-head-phrase := basic-head-1st-comp-phrase & head-final & '
                   '[ HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD comp & [ INIT - ] ].',section='phrases')
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
