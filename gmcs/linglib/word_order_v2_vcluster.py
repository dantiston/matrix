

########################################################
# COMMON COMPONENTS V2+CLUSTERS ACROSS ANALYSES CHOICES
# GENERAL COMPONENTS

def v2_and_verbal_clusters(ch, mylang, lrules, rules):

#create nexus phrases if cluster is present  
  add_nexus_constraints_v2_with_cluster(ch, mylang)
#creating basic phrases and rules
  add_basic_phrases_v2_with_cluster(ch, mylang)
  add_v2_with_cluster_rules(ch, rules)
#specialized rules and interactions for Germanic
  specialized_word_order_v2_with_cluster(ch, mylang, lrules, rules)


def add_nexus_constraints_v2_with_cluster(ch, mylang):

###ADDING CONSTRAINTS ON BASIC RULES CREATING SECOND POSITION

  mylang.add('head-initial-head-nexus := nonverbal-comp-phrase & \
                  [ HEAD-DTR.SYNSEM.LOCAL.CAT.MC + ].')
  mylang.add('finite-lex-rule := [ SYNSEM.LOCAL.CAT.MC na-or-- ].')
  mylang.add('head-final-head-nexus := nonverbal-comp-phrase & \
                                       [ SYNSEM.LOCAL.CAT.MC +,\
                                         NON-HEAD-DTR.SYNSEM.LOCAL.CAT.MC - ].')
  
  if ch.get('aux-comp-order') == 'both' or ch.get('vc-analysis') == 'aux-rule':
    mylang.add('cat :+ [ HEADFINAL bool ].', section='addenda')

  if ch.get('vc-analysis') == 'basic':
    mylang.add('head-initial-head-nexus := [ HEAD-DTR.SYNSEM.LOCAL.CAT.SECOND + ].')
    mylang.add('head-final-head-nexus := [ SYNSEM.LOCAL.CAT.SECOND #scd, \
                                           HEAD-DTR.SYNSEM.LOCAL.CAT.SECOND #scd ].')
  elif ch.get('vc-analysis') == 'aux-rule':
    mylang.add('head-initial-head-nexus := [ HEAD-DTR.SYNSEM.LOCAL.CAT.HEADFINAL - ].')
    mylang.add('head-final-head-nexus := [ SYNSEM.LOCAL.CAT.HEADFINAL #hf, \
                                           HEAD-DTR.SYNSEM.LOCAL.CAT.HEADFINAL #hf ].')


def add_basic_phrases_v2_with_cluster(ch, mylang):

  mylang.add('subj-head-vc-phrase := decl-head-subj-phrase & head-final-invc & nonverbal-comp-phrase.') 


###Analysis independent rules

  if ch.get('vc-placement') == 'pre':
    general_pre_objectival_cluster_phrases(ch, mylang)
  else:
    general_post_objectival_cluster_phrases(ch, mylang)

  if ch.get('argument-order') == 'fixed':
    add_fixed_argument_order_constraints(mylang)
  else:
    mylang.add('head-comp-phrase-2 := basic-head-2nd-comp-phrase & head-initial-head-nexus.')

  if ch.get('vc-analysis') == 'basic':
    create_argument_composition_phrases(ch, mylang)
  elif ch.get('vc-analysis') == 'aux-rule':
    create_aux_plus_verb_phrases(ch, mylang)

def general_pre_objectival_cluster_phrases(ch, mylang):
  mylang.add('general-head-comp-vc-phrase := basic-head-1st-comp-phrase & head-initial-invc.')
  mylang.add('head-comp-vc-phrase := general-head-comp-vc-phrase & nonverbal-comp-phrase.')
  mylang.add('head-comp-2-vc-phrase := basic-head-2nd-comp-phrase & head-initial-invc & nonverbal-comp-phrase.')
  if ch.get('aux-comp-order') == 'before':
    mylang.add('aux-comp-vc-phrase := [ HEAD-DTR.SYNSEM.LIGHT +, \
                             NON-HEAD-DTR.SYNSEM.LOCAL.CAT.MC - ].') 


def general_post_objectival_cluster_phrases(ch, mylang):

  mylang.add('general-comp-head-vc-phrase:= basic-head-1st-comp-phrase & head-final-invc.')
  mylang.add('comp-head-vc-phrase := general-comp-head-vc-phrase & nonverbal-comp-phrase.')
  mylang.add('comp-2-head-vc-phrase := basic-head-2nd-comp-phrase & head-final-invc & nonverbal-comp-phrase.')
  if ch.get('aux-comp-order') == 'after': 
    mylang.add('comp-aux-vc-phrase := [ HEAD-DTR.SYNSEM.LIGHT +, \
                                          NON-HEAD-DTR.SYNSEM.LOCAL.CAT.MC - ].')

  elif ch.get('aux-comp-order') == 'both':
    mylang.add('comp-aux-vc-phrase := [ SYNSEM.LOCAL.CAT [ HEADFINAL #hf ], \
                                            HEAD-DTR.SYNSEM.LOCAL.CAT.HEADFINAL +, \
                                            NON-HEAD-DTR.SYNSEM.LOCAL.CAT [ MC -, \
                                                                            HEADFINAL #hf ] ].')
    mylang.add('aux-comp-vc-phrase := [ SYNSEM.LOCAL.CAT.HEADFINAL #hf, \
                           HEAD-DTR.SYNSEM.LOCAL.CAT [ HEADFINAL -, \
				                       VC + ], \
                           NON-HEAD-DTR.SYNSEM.LOCAL.CAT [ MC -, \
				                           HEADFINAL #hf ]].')
    if ch.get('edge-related-res') == 'yes':
      add_edge_constraint(mylang)

def add_v2_with_cluster_rules(ch, rules):

  rules.add('comp-2-head-vc := comp-2-head-vc-phrase.')
  rules.add('subj-head-vc := subj-head-vc-phrase.')
  rules.add('aux-2nd-comp := aux-2nd-comp-phrase.')
  rules.add('comp-aux-2nd := comp-aux-2nd-phrase.')



  if ch.get('argument-order') != 'fixed':
    rules.add('head-comp-2 := head-comp-phrase-2.')

  if ch.get('vc-analysis') == 'aux-rule':
    auxRule = True
  else:
    auxRule = False

  if ch.get('vc-placement') == 'pre':
    add_preverbal_verbcluster_rules(rules, auxRule)
  else:
    add_postobjectival_verbcluster_rules(ch, rules, auxRule)

  if ch.get('split-cluster') == 'yes':
    add_split_cluster_rules(rules, auxRule)


def add_preobjectival_verbcluster_rules(rules, auxRule):

  rules.add('head-comp-vc := head-comp-vc-phrase.')
  if not auxRule:
    rules.add('head-comp-2-vc := head-comp-2-vc-phrase.')
  if ch.get('aux-comp-order') == 'before':
    rules.add('aux-comp-vc := aux-comp-vc-phrase.')


def add_postobjectival_verbcluster_rules(ch, rules, auxRule):

  rules.add('comp-head-vc := comp-head-vc-phrase.')
  if not auxRule:
    rules.add('comp-2-head-vc := comp-2-head-vc-phrase.')
  if ch.get('aux-comp-order') == 'after' or ch.get('aux-comp-order') == 'both':
    rules.add('comp-aux-vc := comp-aux-vc-phrase.')
  if ch.get('aux-comp-order') == 'before' or ch.get('aux-comp-order') == 'both':
    rules.add('aux-comp-vc := aux-comp-vc-phrase.') 


def add_split_cluster_rules(rules, auxRule):
  if auxRule:
    rules.add('noncomp-aux-2nd := noncomp-aux-2nd-phrase.')  
    rules.add('insert-auxiliary := special-insert-aux-phrase.')

####################
# More specialized word order
#

###function that registers whether a specific verb-form is placed
###at the edge of the verbal cluster

def add_edge_constraint(mylang):
  mylang.add('comp-aux-vc-phrase := [ SYNSEM.LOCAL.CAT.EDGE #ed & na-or--, \
                                      NON-HEAD-DTR.SYNSEM.LOCAL.CAT.EDGE #ed ].')
  mylang.add('aux-comp-vc-phrase := [ SYNSEM.LOCAL.CAT.EDGE #ed & bool , \
                                      NON-HEAD-DTR.SYNSEM.LOCAL.CAT.EDGE #ed ].')

###function that adds necessary constraints to make complements that are not
###in sentence initial position appear in fixed order

def add_fixed_argument_order_constraints(mylang):
  mylang.add('head-comp-phrase := [ HEAD-DTR.SYNSEM.LOCAL.CAT.VAL.SUBJ < > ].')  
  mylang.add('subj-head-vc-phrase := [ SYNSEM.LOCAL.CAT.ARG-ORDER - ].')
  mylang.add('comp-head-vc-phrase := [ SYNSEM.LOCAL.CAT [ ARG-ORDER -, \
                        ALLOWED-PART #ap & bool ], \
                        HEAD-DTR.SYNSEM.LOCAL.CAT [ ARG-ORDER +, \
                                                    ALLOWED-PART #ap ] ].')
  mylang.add('comp-2-head-vc-phrase := [ SYNSEM.LOCAL.CAT.ARG-ORDER #ao, \
                                         HEAD-DTR.SYNSEM.LOCAL.CAT.ARG-ORDER #ao & + ].')


def specialized_word_order_v2_with_cluster(ch, mylang, lrules, rules):
 
  auxorder = ch.get('aux-comp-order')

##VC used to distinguish elements that can or cannot be part of verbal cluster
##nouns break verbal cluster
  mylang.add('noun-lex := [ SYNSEM.LOCAL.CAT.VC - ].')
  
##phrase to combine head with complement while head is in final position
##taking Germanic languages: either needs to become complement of conjugated
##verb in second position, or is a subordinate clause. (hence MC -)
##TO CHECK: DANISH

  mylang.add('head-final-invc := head-final & \
                    [ SYNSEM.LOCAL.CAT.MC #mc & -, \
                      HEAD-DTR.SYNSEM.LOCAL.CAT.MC #mc ].')

##nonverbal-comp-phrase: states that phrase cannot be used to combine
##head with verbal complement
  mylang.add('nonverbal-comp-phrase := basic-binary-headed-phrase & \
                   [ NON-HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD +njrpcdmo ].')

##edge related restrictions to account for Dutch:
##*hij zal de bal kunnen gekregen hebben.
##hij zal de bal gekregen kunnen hebben.
##hij zal de bal kunnen hebben gekregen.
##he shall the ball can-inf have-inf got-ptc
##
##the participle can appear on either side of the cluster,
##but not in the middle (this is however allowed in Flemish)
##
##feature EDGE can register if an item is at the edge of a phrase or not

  if ch.get('edge-related-res') == 'yes':
    mylang.add('cat :+ [ EDGE luk ].', 'EDGE is used to prevent participles from occurring in the middle of the cluster', section='addenda')

##
##verb-second languages can have a fixed or (relatively) free order of arguments
##that are not in first position.
##Dutch and Danish have fixed order, German allows more freedom.
##Fixed order is reflected as well in which partial VPs are allowed in the 
##Vorfeld

  if ch.get('argument-order') == 'fixed':
    mylang.add('cat :+ [ ARG-ORDER bool, \
                         ALLOWED-PART luk ].', 'ARG-ORD keeps track of ordering of arguments. ALLOWED-PART makes sure no disallowed partial VP-phrases occur in the Vorfeld.', section='addenda')
    mylang.add('lex-rule :+ [ SYNSEM.LOCAL.CAT.ALLOWED-PART #ap, \
                              DTR.SYNSEM.LOCAL.CAT.ALLOWED-PART #ap ].',
               section='addenda')
###not allowed partial vps can occur with ditransitive verbs 
    if ch.get('ditransitives') == 'yes':
      mylang.add('ditransitive-verb-lex := [ SYNSEM.LOCAL.CAT.ALLOWED-PART na-or-- ].')


##verb-initial in cluster counter part, only when necessary which may be:
## 1. verbs precede their verbal complement (Dutch, German auxiliary flip
## 2. verbs precede their objects (Danish)
## [MC - ] as for head-final-invc (above)

  if auxorder == 'before' or auxorder == 'both' or ch.get('vc-placement') == 'pre':
    mylang.add('head-initial-invc := head-initial & \
                  [ SYNSEM.LOCAL.CAT.MC #mc & -, \
                    HEAD-DTR.SYNSEM.LOCAL.CAT.MC #mc ].')
##
##calling specific rules depending on chosen analysis

  if ch.get('vc-analysis') == 'aux-rule':
    spec_word_order_phrases_aux_plus_verb(ch, mylang)
  else:
    spec_word_order_phrases_argument_composition(ch, mylang, lrules, rules)

##########################################################################
#                                                                        #
# ALTERNATIVE ANALYSES                                                   #
#                                                                        #
##########################################################################

#####
# A. Argument-composition analysis (standard HPSG)
#  

####DISCLAIMER: NOT ALL LOGICAL COMBINATIONS ARE COVERED BY CODE FOR NOW

def create_argument_composition_phrases(ch, mylang):

  if ch.get('vc-placement') == 'pre':

    if ch.get('aux-comp-order') == 'before':
      currenttype = 'aux-comp-vc-phrase'
      mylang.add(currenttype + ' :=  general-head-comp-vc-phrase & \
                                 [ NON-HEAD-DTR.SYNSEM.LOCAL.CAT.VC + ].')

  else:
    if ch.get('aux-comp-order') == 'after':
      mylang.add('comp-aux-vc-phrase := general-comp-head-vc-phrase & \
                         [ NON-HEAD-DTR.SYNSEM.LOCAL.CAT.VC + ].') 

    elif ch.get('aux-comp-order') == 'both':
      mylang.add('comp-aux-vc-phrase := general-comp-head-vc-phrase & \
                         [ SYNSEM.LOCAL.CAT.SECOND na,\
                           HEAD-DTR.SYNSEM.LOCAL.CAT [ VC +, \
                                                       SECOND + ], \
                           NON-HEAD-DTR.SYNSEM.LOCAL.CAT.VC + ].')
      mylang.add('aux-comp-vc-phrase := basic-head-1st-comp-phrase & head-initial-invc & \
                         [ SYNSEM.LOCAL.CAT.SECOND +,\
                           HEAD-DTR.SYNSEM.LOCAL.CAT.SECOND na, \
                           NON-HEAD-DTR.SYNSEM.LOCAL.CAT.VC + ].')

      if ch.get('argument-order') == 'fixed':
        mylang.add('comp-aux-vc-phrase := [ SYNSEM.LOCAL.CAT.ALLOWED-PART #ap, \
                             NON-HEAD-DTR.SYNSEM.LOCAL.CAT.ALLOWED-PART #ap ].')

        mylang.add('aux-comp-vc-phrase := [ SYNSEM.LOCAL.CAT.ALLOWED-PART #ap, \
                             NON-HEAD-DTR.SYNSEM.LOCAL.CAT.ALLOWED-PART #ap ].')


################
# specialized phrases for argument composition plus clusters
#

def spec_word_order_phrases_argument_composition(ch, mylang, lrules, rules):

###SECOND registers whether element is currently in 2nd position or not
###and whether it is allowed to be in second position (for Germanic only 
###finite verb forms)
  mylang.add('cat :+ [ SECOND luk ].')

###verbal items are [ VC + ]
###basic phrases need to pass on value of VC feature

  mylang.add('verb-lex := [ SYNSEM.LOCAL.CAT.VC + ].')
  mylang.add('basic-bare-np-phrase :+ [ SYNSEM.LOCAL.CAT.VC #vc, \
                                        HEAD-DTR.SYNSEM.LOCAL.CAT.VC #vc ].')
  mylang.add('basic-head-comp-phrase :+ [ SYNSEM.LOCAL.CAT.VC #vc, \
                                          NON-HEAD-DTR.SYNSEM.LOCAL.CAT.VC #vc ].')

###[POTENTIALLY MORE GENERAL]
###head-comp constraint on LIGHT extend to head-subj-phrase
  mylang.add('basic-head-subj-phrase :+ [ SYNSEM [ LOCAL.CAT [ VC #vc, \
                                                               HC-LIGHT #light ], \
                                          LIGHT #light ], \
                          HEAD-DTR.SYNSEM.LOCAL.CAT.HC-LIGHT #light, \
                          NON-HEAD-DTR.SYNSEM.LOCAL.CAT.VC #vc ].')

###first analysis: to model some efficiency properties of aux+verb
###auxiliaries may only pick up verbal complements to their right
###this avoids spurious phrases where any form is taken as a potential subject
###or complement (the auxiliaries are more or less forced to find their verbal complements first.
###if auxiliary takes its verbal complement to its right, it still must pick up
###an element to its left to become verb second (SECOND registers this)   
###
  mylang.add('aux-2nd-comp-phrase := basic-head-1st-comp-phrase & head-initial & \
                    [ SYNSEM.LOCAL.CAT [ MC #mc & na, \
		                         SECOND - ], \
                      HEAD-DTR.SYNSEM.LOCAL.CAT[ MC #mc, \
			                         SECOND + ], \
                      NON-HEAD-DTR.SYNSEM.LOCAL.CAT [ HEAD verb, \
		                        	      MC - ]].') 


###Assuming no [subj + verb] in Vorfeld, despite occasional exceptions
###(NON-HEAD-DTR.SYNSEM.LOCAL.CAT.VAL.SUBJ <[ ]>)
  mylang.add('gen-comp-aux-2nd-phrase := head-final & basic-head-1st-comp-phrase &  \
                     [ SYNSEM.LOCAL.CAT [ MC +, \
		                          SECOND #scd ], \
                       HEAD-DTR.SYNSEM.LOCAL.CAT [ MC na, \
		             	                   SECOND #scd ], \
                       NON-HEAD-DTR.SYNSEM.LOCAL.CAT [ MC -, \
			                               HEAD verb, \
				                       VAL.SUBJ < [ ] >]].')
###if partial vp fronting is not allowed (it is not in Danish),
###verbs must be accompanied by all their complements if placed in the
###Vorfeld
  if ch.get('part-vp-front') == 'no':
    mylang.add('gen-comp-aux-2nd-phrase := [ NON-HEAD-DTR.SYNSEM.LOCAL.CAT.VAL.COMPS < > ].')
  mylang.add('comp-aux-2nd-phrase := gen-comp-aux-2nd-phrase & \
                      [ HEAD-DTR.SYNSEM.LOCAL.CAT.SECOND + ].')
###languages that have fixed argument-order (Dutch) cannot have the verb
###be placed in the vorfeld with an argument that is non-adjacent in
###canonical position: i.e.
###ik heb de man het boek gegeven.
#I have-1st-sg the man the book give-ptc.
#can be realized as (though pretty marked):
#a)het boek gegeven heb ik de man. 
#but absolutely not as:
#b) de man gegeven heb ik het boek.

  if ch.get('argument-order') == 'fixed':
    mylang.add('comp-aux-2nd-phrase := [ NON-HEAD-DTR.SYNSEM.LOCAL.CAT.ALLOWED-PART na-or-+ ].')

##additional constraints to account for split clusters, if occuring
##(explanation see below)
  if ch.get('split-cluster') == 'yes':
    split_cluster_phrases_argument_composition(ch, mylang, rules, lrules)

####
# Additions needed to account for split clusters if arg-comp
# analysis is used.
##split clusters are for instance
#
#1) geslapen zou hij kunnen hebben.
#sleep-ptc would he can-inf have-inf.
#'he could have been sleeping'
#where the main verb is in the Vorfeld, but there are still verbs in 
#the right bracket.

def split_cluster_phrases_argument_composition(ch, mylang, rules, lrules):

  mylang.add('split-cl-comp-aux-2nd-phrase := gen-comp-aux-2nd-phrase & \
                       [ HEAD-DTR.SYNSEM.LOCAL.CAT.SECOND -, \
                         NON-HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD.AUX - ].')
  rules.add('split-cluster-comp-aux-2nd := split-cl-comp-aux-2nd-phrase.')



  if ch.get('split-analysis') == 'lex-rule':
    split_cluster_arg_comp_lex_rule(ch, mylang, lrules)

  elif ch.get('split-analysis') == '3head-comp':
    mylang.add('comp-head-3-vc-phrase := basic-head-3rd-comp-phrase & \
                         nonverbal-comp-phrase & head-final-invc.')
    rules.add('comp-head-3-vc := comp-head-3-vc-phrase.')


def split_cluster_arg_comp_lex_rule(ch, mylang, lrules):
  headdtrval = '[ SYNSEM.LOCAL.CAT.VFRONT #vf, \
                  HEAD-DTR.SYNSEM.LOCAL.CAT.VFRONT #vf'
  nhddtrval = '[ SYNSEM.LOCAL.CAT.VFRONT #vf, \
                 NON-HEAD-DTR.SYNSEM.LOCAL.CAT.VFRONT #vf'

  mylang.add('head-initial-head-nexus := ' + headdtrval + ' ].')
  mylang.add('comp-head-vc-phrase := ' + headdtrval + ' & na-or-- ].')
  mylang.add('comp-2-head-vc-phrase:= [ HEAD-DTR.SYNSEM.LOCAL.CAT.VFRONT - ].')
  mylang.add('comp-aux-vc-phrase := ' + nhddtrval + ' ].')
  mylang.add('basic-head-subj-phrase :+ '+ headdtrval + ' ].')
  mylang.add('aux-2nd-comp-phrase := ' + nhddtrval + ' ].')
  mylang.add('comp-aux-2nd-phrase := ' + nhddtrval + ' ].')
  mylang.add('split-cl-comp-aux-2nd-phrase := [ SYNSEM.LOCAL.CAT.VFRONT -, \
                                                        NON-HEAD-DTR.SYNSEM.LOCAL.CAT.VFRONT na-or-+ ].')


  mylang.add('cat :+ [ VFRONT luk ].', 'VFRONT checks whether ditransitive verb has undergone needed modification to occur in the Vorfeld', section='addenda')
  mylang.add('infl-lex-rule :+ [ SYNSEM.LOCAL.CAT.VFRONT #vf, \
                                       DTR.SYNSEM.LOCAL.CAT.VFRONT #vf ].')
  mylang.add('change-arg-order-rule := const-val-change-only-lex-rule & \
 [ SYNSEM.LOCAL.CAT [ VAL [ SUBJ #subj, \
			    COMPS < #comp2, #comp1 >,\
			    SPR #spr,\
			    SPEC #spec ],\
		      VFRONT +,\
		      VC #vc,\
		      SECOND #sd ], \
   DTR.SYNSEM.LOCAL.CAT [ VAL [ SUBJ #subj,\
				COMPS < #comp1, #comp2 >,\
				SPR #spr,\
				SPEC #spec ],\
			  VFRONT -,\
			  HEAD [ FORM nonfinite,\
				 AUX - ],\
			  VC #vc,\
			  SECOND #sd   ] ].')
  lrules.add('change-arg-order := change-arg-order-rule.')
  if ch.get('argument-order') == 'fixed':
    mylang.add('change-arg-order-rule := \
                        [ SYNSEM.LOCAL.CAT [ ARG-ORDER #ao, \
                                             ALLOWED-PART #ap ], \
                          DTR.SYNSEM.LOCAL.CAT [ ARG-ORDER #ao, \
                                                 ALLOWED-PART #ap ]].')

  if ch.get('edge-related-res') == 'yes':
    mylang.add('change-arg-order-rule := [ SYNSEM.LOCAL.CAT.EDGE #ed, \
                                          DTR.SYNSEM.LOCAL.CAT.EDGE #ed ].')
  if ch.get('aux-comp-order') == 'both':
    mylang.add('aux-comp-vc-phrase := ' + nhddtrval + ' ].')
    mylang.add('head-initial-invc := ' + headdtrval + ' ].')
    if ch.get('ditransitives') == 'yes':
      mylang.add('ditransitive-verb-lex := [ SYNSEM.LOCAL.CAT.VFRONT - ].')



###########
# B) Aux+verb rule analysis, proposed by Dan Flickinger,
# first described in Bender (2008)
# 


def create_aux_plus_verb_phrases(ch, mylang):

  if ch.get('vc-placement') == 'pre':
    if ch.get('aux-comp-order') == 'before':
      currenttype = 'aux-comp-vc-phrase'
      mylang.add(currenttype + ' := head-initial & basic-aux-verb-rule & \
                            [ SYNSEM [ LOCAL.CAT [ MC -, \
                                                   VC na ], \
                                       LIGHT - ], \
                              NON-HEAD-DTR.SYNSEM.LOCAL.CAT.VC na-or-+ ].')
  else:
    if ch.get('aux-comp-order') == 'after': 
      mylang.add('comp-aux-vc-phrase := basic-aux-verb-rule & head-final & \
                         [ SYNSEM [ LOCAL.CAT [ MC -, \
                                                VC + ], \
                                    LIGHT - ] ].')

    elif ch.get('aux-comp-order') == 'both':
      mylang.add('comp-aux-vc-phrase := basic-aux-verb-rule & head-final & \
                                    [ SYNSEM.LOCAL.CAT [ MC -, \
                                                         VC +, \
                                                         NOMINAL #nl ], \
                                      HEAD-DTR.SYNSEM.LOCAL.CAT.VC na, \
                                      NON-HEAD-DTR.SYNSEM.LOCAL.CAT.NOMINAL #nl ].')
      mylang.add('aux-comp-vc-phrase := basic-aux-verb-rule & head-initial & \
                                  [ SYNSEM.LOCAL.CAT [ MC -, \
                                                       VC na ], \
                                    NON-HEAD-DTR.SYNSEM.LOCAL.CAT [ VC na-or-+, \
                                                                      NOMINAL - ] ].')
######next constraint is shared between both alternative analyses
####WILL STAY UP THERE....
#      mylang.add(currenttype + ' := ' + currentsupertype + ' & \
#                           [ HEAD-DTR.SYNSEM.LIGHT +, \
#                             NON-HEAD-DTR.SYNSEM.LOCAL.CAT.MC - ].') 



########
# specialized rules
#

def spec_word_order_phrases_aux_plus_verb(ch, mylang):
 
  mylang.add('basic-aux-verb-rule := head-compositional & basic-binary-headed-phrase & head-valence-phrase & \
                [ SYNSEM.LOCAL [ CAT.VAL #val, \
		                 CONT.HOOK #hook ], \
                  C-CONT [ RELS <! !>, \
	                   HCONS <! !>, \
	                   HOOK #hook ], \
                  HEAD-DTR.SYNSEM.LOCAL [ CAT [ HEAD verb & [ AUX + ], \
				                VAL.COMPS < #comp > ], \
			                  CONT.HOOK #hook ], \
                  NON-HEAD-DTR.SYNSEM #comp & [ LOCAL.CAT [ HEAD verb, \
					                    VAL #val ] ] ].')
       
  mylang.add('aux-2nd-comp-phrase := basic-aux-verb-rule & head-initial & \
                             [ SYNSEM [ LOCAL.CAT [ HEADFINAL +, \
			                            MC #mc & na, \
			                            HEAD.FORM finite ], \
	                                            LIGHT - ], \
                               HEAD-DTR.SYNSEM [ LIGHT +, \
		                                 LOCAL.CAT.MC #mc ], \
                               NON-HEAD-DTR.SYNSEM.LOCAL.CAT.MC - ].')   
        
  mylang.add('head-final-invc := [ SYNSEM.LOCAL.CAT.VC -, \
                                         HEAD-DTR.SYNSEM.LOCAL.CAT.VC na-or-- ].')
  if ch.get('vc-placement') == 'pre':
    mylang.add('head-initial-invc := [ SYNSEM.LOCAL.CAT.VC -, \
                                       HEAD-DTR.SYNSEM.LOCAL.CAT.VC na-or-- ].')

  if ch.get('argument-order') == 'fixed':
    mylang.add('comp-aux-2nd-phrase := [ NON-HEAD-DTR.SYNSEM.LOCAL.CAT.ALLOWED-PART na-or-+ ].')
    mylang.add('basic-aux-verb-rule := [ SYNSEM.LOCAL.CAT.ALLOWED-PART #ap, \
NON-HEAD-DTR.SYNSEM.LOCAL.CAT.ALLOWED-PART #ap ].')

  if ch.get('part-vp-front') == 'no':
    mylang.add('comp-aux-2nd-phrase := [ SYNSEM.LOCAL.CAT.VAL.COMPS < > ].') 

  if ch.get('aux-comp-order') == 'both':
    mylang.add('head-final-invc := [ SYNSEM.LOCAL.CAT.NOMINAL + ].')
    mylang.add('cat :+ [ NOMINAL bool ].', 'NOMINAL prevents nominal forms from occurring in the verbal cluster', section='addenda')

  if ch.get('split-cluster') == 'yes':
    split_cluster_phrases_aux_plus_verb(ch, mylang)
  else:
    mylang.add('comp-aux-2nd-phrase := basic-aux-verb-rule & head-final & \
                              [ SYNSEM.LOCAL.CAT [ MC +, \
		                                   HEADFINAL #hf, \
		                                   VAL.SUBJ < [] >  ], \
                                HEAD-DTR.SYNSEM.LOCAL.CAT [ MC na, \
			       	                            HEADFINAL #hf ], \
                                NON-HEAD-DTR.SYNSEM.LOCAL.CAT.MC - ].')
    
def split_cluster_phrases_aux_plus_verb(ch, mylang):


  mylang.add('cat :+ [ VFRONT bool ].', 'VFRONT checks whether the vorfeld contains a partial verbal cluster', section='addenda')
  mylang.add('head :+ [ DTR-FORM form ].')

###flexible aux-comp-order always uses NOMINAL with aux+verb analysis
###only add for fixed aux-comp-order + split cluster

  if ch.get('aux-comp-order') != 'both': 
    mylang.add('cat :+ [ NOMINAL bool ].', 'NOMINAL prevents nominal forms from occurring in the verbal cluster', section='addenda')

  mylang.add('special-basic-aux-verb-rule :=  head-compositional & \
                           basic-binary-headed-phrase & head-valence-phrase & \
           [ SYNSEM.LOCAL [ CAT.VAL #val, \
                            CONT.HOOK #hook ], \
             C-CONT [ RELS <! !>, \
                      HCONS <! !>, \
                      HOOK #hook ], \
             HEAD-DTR.SYNSEM.LOCAL [ CAT [ HEAD verb & [ AUX + ], \
                                           VAL.COMPS.FIRST.LOCAL.CONT #cont ], \
                                     CONT.HOOK #hook ], \
             NON-HEAD-DTR.SYNSEM  [ LOCAL [ CAT [ HEAD verb, \
                                                  VAL #val ], \
                                                  CONT #cont ] ] ].')

  mylang.add('gen-verb-aux-2nd-rule := head-final & \
                       [ SYNSEM.LOCAL.CAT [ VAL.SUBJ < [] >, \
                                            MC +, \
                                            HEADFINAL #hf, \
                                            HEAD [ DTR-FORM #dform \
                                                   FORM finite ] ], \
                         HEAD-DTR.SYNSEM.LOCAL.CAT [ MC na, \
                                                     HEADFINAL #hf ], \
                         NON-HEAD-DTR.SYNSEM.LOCAL.CAT [ MC -, \
                                                         HEAD.FORM #dform ] ].')

  mylang.add('comp-aux-2nd-phrase := gen-verb-aux-2nd-rule & basic-aux-verb-rule & [ SYNSEM.LOCAL.CAT.VFRONT - ].')
  mylang.add('noncomp-aux-2nd-phrase := gen-verb-aux-2nd-rule & special-basic-aux-verb-rule & [ SYNSEM.LOCAL.CAT.VFRONT +, \
                        NON-HEAD-DTR.SYNSEM.LOCAL.CAT.HEAD.AUX - ].')
  mylang.add('special-insert-aux-phrase := headed-phrase & \
         [ SYNSEM.LOCAL [ CONT [ HOOK #hook, \
		                 RELS [ LIST #first,\
				 LAST #last ], \
			 HCONS [ LIST [ FIRST [ HARG #harg1,\
				        	LARG #larg1 ],\
					REST #scfirst ],\
				 LAST #sclast ] ],\
		          CAT [ VAL #val,\
			        MC #mc,\
			        VFRONT - ] ],\
            HEAD-DTR #firstarg & head-initial & \
              [ SYNSEM [ LOCAL [ CAT [ HEAD verb & [ AUX +,\
						     DTR-FORM #dform ],\
				       VAL #val & [ SUBJ < >,\
						    COMPS < > ],\
				       MC #mc,\
				       VFRONT + ],\
				 CONT [ HOOK #hook,\
				 HCONS [ LIST.FIRST [ HARG #harg1, \
                                                      LARG #larg2 ] ] ] ] ] ], \
           INSERT-DTR #secarg & [ SYNSEM [ LOCAL [ CAT [ HEAD verb & [ AUX + ],\
						         VAL.COMPS.FIRST.LOCAL.CAT.HEAD.FORM #dform ],\
					            CONT [ HOOK.LTOP #larg1,\
						    HCONS [ LIST.FIRST [ LARG #larg2 ] ] ] ] ],\
			                   INFLECTED infl-satisfied ], \
                                  C-CONT [ RELS [ LIST #middle2,\
		                                  LAST #last ],\
	                          HCONS [ LIST #scmiddle2,\
		                          LAST #sclast ] ],\
           ARGS < #firstarg & [ SYNSEM.LOCAL local & \
                                     [ CONT [ RELS [ LIST #first,\
						     LAST #middle1 ],\
				       HCONS [ LIST [ FIRST [ ],\
						      REST #scfirst ],\
					       LAST #scmiddle1 ] ] ] ], \
	          #secarg  & [ SYNSEM.LOCAL local & \
                                     [ CONT [ RELS [ LIST #middle1,\
						     LAST #middle2 ],\
				       HCONS [ LIST #scmiddle1,\
					       LAST #scmiddle2 ] ] ] ] > ].')
  mylang.add('decl-head-subj-phrase :+ \
                      [ SYNSEM.LOCAL.CAT.VFRONT #vf, \
                        HEAD-DTR.SYNSEM.LOCAL.CAT.VFRONT #vf ].')
  mylang.add('basic-head-comp-phrase :+ \
                      [ SYNSEM.LOCAL.CAT.VFRONT #vf, \
                        HEAD-DTR.SYNSEM.LOCAL.CAT.VFRONT #vf ].')
  mylang.add('basic-head-mod-phrase-simple :+ \
                      [ SYNSEM.LOCAL.CAT.VFRONT #vf, \
                        HEAD-DTR.SYNSEM.LOCAL.CAT.VFRONT #vf ].')


  if ch.get('part-vp-front') == 'no':
    mylang.add('gen-verb-aux-2nd-rule := [ NON-HEAD-DTR.SYNSEM.LOCAL.CAT.VAL.COMPS < > ].')

  if ch.get('argument-order') == 'fixed':
    mylang.add('noncomp-aux-2nd-phrase := [ NON-HEAD-DTR.SYNSEM.LOCAL.CAT.ALLOWED-PART na-or-+ ].')