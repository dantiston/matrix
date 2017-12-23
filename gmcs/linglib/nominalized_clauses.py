
###
# Constants
###

NHS_SUPERTYPE = 'basic-head-subj-phrase'
NHS_DEF = '[ HEAD-DTR.SYNSEM [ LOCAL [ CONT.HOOK.INDEX ref-ind ],\
                               NON-LOCAL [ QUE 0-dlist,\
                                           REL 0-dlist ]]\
            NON-HEAD-DTR.SYNSEM.LOCAL.CAT.VAL.SPR < > ].'

HIGH_OR_MID_LEXRULE = 'high-or-mid-nominalization-lex-rule := cat-change-with-ccont-lex-rule & same-cont-lex-rule &\
    [ SYNSEM.LOCAL [ CONT [ HOOK [ INDEX event ]],\
		   CAT [ HEAD verb &\
			      [ NMZ +,\
                     MOD #mod ],\
                         VAL [ SUBJ < [ LOCAL [ CAT [ HEAD noun,\
                                                      VAL.SPR < > ],\
                                                CONT.HOOK.INDEX #subj ] ] >,\
                               COMPS #comps,\
                               SPR #spr,\
                               SPEC #spec ],\
                         MC #mc,\
                         MKG #mkg,\
                         HC-LIGHT #hc-light,\
                         POSTHEAD #posthead ] ],\
    DTR.SYNSEM.LOCAL [ CAT [ HEAD [ MOD #mod ],\
                           VAL [ SUBJ < [ LOCAL.CONT.HOOK.INDEX #subj ] >,\
                                 COMPS #comps,\
                                 SPR #spr,\
                                 SPEC #spec ],\
                           MC #mc,\
                           MKG #mkg,\
                           HC-LIGHT #hc-light,\
                           POSTHEAD #posthead ]],\
   C-CONT [ RELS <! !>, HCONS <! !> ] ].'

LOW_LEXRULE = 'low-nominalization-lex-rule := cat-change-with-ccont-lex-rule &\
                [ SYNSEM.LOCAL.CAT [ HEAD noun & \
			    [ MOD #mod ],\
		        VAL [ SUBJ < [ LOCAL [ CAT [ HEAD noun,\
		                            VAL.SPR < > ],\
				      	      CONT.HOOK.INDEX #subj ]] >,\
			     COMPS #comps,\
			     SPEC #spec,\
			     SPR < [ OPT + ]> ],\
		       MC #mc,\
		       MKG #mkg,\
		       HC-LIGHT #hc-light,\
		       POSTHEAD #posthead ],\
                C-CONT [ RELS <! [ PRED "nominalized_rel",\
		       LBL #ltop,\
		       ARG0 ref-ind & #arg0,\
		       ARG1 #arg1 ] !>,\
	            HCONS <! qeq &\
		        [ HARG #arg1,\
		      LARG #larg ] !>,\
	            HOOK [ INDEX #arg0,\
		        LTOP #ltop ]],\
                DTR.SYNSEM.LOCAL [ CAT [ HEAD [ MOD #mod ],\
			     VAL [ SUBJ < [ LOCAL.CONT.HOOK.INDEX #subj ] >,\
				   COMPS #comps,\
				   SPEC #spec  ],\
			     MC #mc,\
			     MKG #mkg,\
			     HC-LIGHT #hc-light,\
			     POSTHEAD #posthead ],\
		       CONT.HOOK [ LTOP #larg ]]].'

def customize_nmcs(mylang, ch, rules, lrules):
    """
    the main nominalized clause customization routine
    """
    for vpc in ch['verb-pc']:
        for lrt in vpc['lrt']:
            for f in lrt['feat']:
                if 'nominalization' in f['name']:
                    for ns in ch.get('ns'):
                        if ns.get('name') == f['value']:
                            level = ns.get('level')
                            if level == 'mid' or level == 'high':
                                lrt['supertypes'] = ', '.join(lrt['supertypes'].split(', ') + \
                                                      ['high-or-mid-nominalization-lex-rule'])
                            if level == 'low':
                                lrt['supertypes'] = ', '.join(lrt['supertypes'].split(', ') + \
                                                  ['low-nominalization-lex-rule'])
    for ns in ch.get('ns'):
        name = ns.get('name')
        level = ns.get('level')
        nmzrel = ns.get('nmzRel')
        add_features(mylang)
        mylang.add('+nvcdmo :+ [ MOD < > ].')
        # OZ 2017-12-23: Refactoring the first part of the function
        super = ''
        if level == 'low' or level == 'mid':
            mylang.set_section('phrases')
            wo = ch.get('word-order')
            if wo == 'osv' or wo == 'sov' or wo == 'svo' or wo == 'v-final':
                typename = 'non-event-subj-head'
                rules.add(typename + ' := ' + typename + '-phrase.')
                super = 'head-final'
            elif wo == 'ovs' or wo == 'vos' or wo == 'vso' or wo == 'v-initial':
                typename = 'non-event-head-subj'
                rules.add(typename + ' := ' + typename + '-phrase.')
                super = 'head-initial'
            mylang.add(typename + '-phrase := ' + NHS_SUPERTYPE + '&' + super + '&' + NHS_DEF)
            if wo in [ 'sov', 'svo', 'ovs', 'vos']:
                mylang.add(typename + '-phrase := [ HEAD-DTR.SYNSEM.LOCAL.CAT.VAL.COMPS < > ].',merge=True)
        if level == 'mid' or level == 'high':
            mylang.set_section('lexrules')
            mylang.add(HIGH_OR_MID_LEXRULE)
        if level == 'low':
            mylang.set_section('lexrules')
            mylang.add(LOW_LEXRULE)
        elif level == 'mid':
            mylang.set_section('phrases')
            mylang.add(level + '-nominalized-clause-phrase := basic-unary-phrase &\
                                    [ SYNSEM.LOCAL.CAT [ HEAD noun,\
            		                VAL [ SPR < [ OPT + ] >,\
                                            SPEC < >,\
                                            COMPS < >,\
            		                        SUBJ < #subj > ]],\
                                    C-CONT [ RELS <! [ PRED "nominalized_rel",\
            	    	            LBL #ltop,\
            		                ARG0 ref-ind & #arg0,\
            		                ARG1 #arg1 ] !>,\
            	                    HCONS <! qeq &\
                		            [ HARG #arg1,\
            	    	            LARG #larg ] !>,\
            	                    HOOK [ INDEX #arg0,\
            		                LTOP #ltop ]],\
                                    ARGS < [ SYNSEM [ LOCAL [ CAT [ HEAD verb &\
            					     [ NMZ + ],\
                				    VAL [ COMPS < >,\
            	    				  SUBJ < #subj >,\
            		    			  SPR < >,\
            			    		  SPEC < > ]],\
            			            CONT.HOOK [ LTOP #larg ]]]] > ].')
            rules.add(level + '-nominalized-clause := ' + level + '-nominalized-clause-phrase.')
        elif level == 'high':
            mylang.set_section('phrases')
            if nmzrel == 'no':
                mylang.add(level + '-no-rel-nominalized-clause-phrase := basic-unary-phrase &\
  [ SYNSEM [ LOCAL.CAT [ HEAD noun,\
                         VAL [ COMPS < >,\
                                        SUBJ < >,\
                                        SPR < >,\
                                        SPEC < > ]]],\
    C-CONT [ RELS <! !>,\
	     HCONS <! !>,\
	     HOOK [ LTOP #ltop ] ],\
    ARGS < [ SYNSEM [ LOCAL [ CAT [ HEAD verb &\
                                       [ NMZ + ],\
                                  VAL [ COMPS < >,\
                                        SUBJ < >,\
                                        SPR < >,\
                                        SPEC < > ] ],\
		CONT.HOOK [ LTOP #ltop ] ] ] ] > ].')
                rules.add(level + '-no-rel-nominalized-clause := ' + level + '-no-rel-nominalized-clause-phrase.')
            elif nmzrel == 'yes':
                mylang.add(level + '-nominalized-clause-phrase := basic-unary-phrase &\
                          [ SYNSEM.LOCAL.CAT [ HEAD noun,\
		       VAL [ SPR < [ OPT + ] >,'
                           'COMPS < >,\
					  SUBJ < >,\
					  SPEC < > ]],\
    C-CONT [ RELS <! [ PRED "nominalized_rel",\
		       LBL #ltop,\
		       ARG0 ref-ind & #arg0,\
		       ARG1 #arg1 ] !>,\
	     HCONS <! qeq &\
		    [ HARG #arg1,\
		      LARG #larg ] !>,\
	     HOOK [ INDEX #arg0,\
		    LTOP #ltop ]],\
    ARGS < [ SYNSEM [ LOCAL [ CAT [ HEAD verb &\
					 [ NMZ + ],\
				    VAL [ COMPS < >,\
					  SUBJ < >,\
					  SPR < >,\
					  SPEC < > ]],\
			      CONT.HOOK [ LTOP #larg ]]]] > ].')
                rules.add(level + '-nominalized-clause := ' + level + '-nominalized-clause-phrase.')

def add_features(mylang):
    mylang.set_section('addenda')
    mylang.add('head :+ [ NMZ bool ].')
    mylang.set_section('noun-lex')
    mylang.add('noun-lex := [ SYNSEM.LOCAL.CAT.HEAD.NMZ - ].')
    mylang.set_section('verb-lex')
    mylang.add('verb-lex := [ SYNSEM.LOCAL.CAT.HEAD.NMZ - ].')