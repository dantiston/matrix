
from delphin_choices import info

from gmcs.lib import TDLHierarchy
from gmcs.linglib import case
from gmcs.linglib import morphotactics
from gmcs.linglib.lexbase import ALL_LEX_TYPES
from gmcs.utils import get_name

dirinv_geom = 'LOCAL.CAT.HEAD.DIRECTION'

########################
### HELPER FUNCTIONS ###
########################

def get_subj_comps_types(j, scale_size, direc, equal):
    hi_type = lo_type = 'dir-inv-'
    if equal == 'direct' and direc == 'dir':
        lo_type += ('scale' if j==1 else ('non-' + str(j-1)))
        hi_type += (('non-' + str(j-1)) if j==scale_size else str(j))
    else:
        hi_type += str(j)
        lo_type += 'non-' + str(j)

    if direc == 'dir':
        return (hi_type, lo_type)
    else:
        return (lo_type, hi_type)

##########################
### MAIN LOGIC METHODS ###
##########################

def customize_direct_inverse(choices, mylang, hierarchies):
    if 'direct-inverse.scale' not in choices:
        return
    write_dir_inv_types(choices, mylang, hierarchies)
    write_dir_inv_lexrule_supertypes(choices, mylang)

def write_dir_inv_types(choices, mylang, hierarchies):
    mylang.add('verb :+ [ DIRECTION direction ].', section='addenda')
    hier = TDLHierarchy('direction')
    hier.add('dir', 'direction')
    hier.add('inv', 'direction')
    hier.save(mylang)

    if info.has_SCARGS(choices):
        mylang.add('word-or-lexrule :+ [ SC-ARGS list ].', section='addenda')
        mylang.add('lex-rule :+ [ SC-ARGS #1, DTR.SC-ARGS #1 ].', section='addenda')

    cases = case.case_names(choices)
    features = info.features(choices)

    # Figure out which features are involved in the hierarchy
    names = []  # feature names
    for scale in choices.get('direct-inverse.scale', ()):
        for feat in scale.get('feat', ()):
            names.append(feat.get('name', ''))

    # Now pass through the scale, creating the direct-inverse hierarchy
    # pairwise
    mylang.set_section('dirinv')
    mylang.add_literal(';;; Direct-inverse scale')
    supertype = 'dir-inv-scale'
    mylang.add(supertype + ' := canonical-synsem.')

    scales = choices.get('direct-inverse.scale', ())
    scale_len = len(scales)

    for i, scale in enumerate(scales[:-1], start=1):
        values = {}  # for each feature, a set of values

        # get the features on the first scale entry in this range
        for feat in scale.get('feat', ()):
            name = feat.get('name','')
            if name not in values:
                values[name] = set()
            values[name].add(feat.get('value'))

        # create the left type in the pair
        type = f'dir-inv-{i}'

        mylang.add(type + ' := ' + supertype + '.')

        for n in values:
            vset = values[n]

            if n == 'case':
                new_vset = set()
                for v in vset:
                    new_vset.add(canon_to_abbr(v, cases))
                vset = new_vset

            geom = ''
            for f in features:
                if f[0] == n:
                    geom = f[2]
                    break

            value = hierarchies[n].get_type_covering(vset)
            if value != n:  # don't bother if it doesn't constrain anything
                mylang.add(type + ' := [ ' + geom + ' ' + value + ' ].')

        # rest of the scale
        values = {}

        for next_scale in scales[i:]:
            for feat in next_scale.get('feat', ()):
                name = feat.get('name','')
                if name not in values:
                    values[name] = set()
                values[name].add(feat.get('value',''))

        # create the right type in the pair
        type = 'dir-inv-non-' + str(i)

        mylang.add(type + ' := ' + supertype + '.')

        for n, vset in values.items():
            if n == 'case':
                new_vset = set()
                for v in vset:
                    new_vset.add(canon_to_abbr(v, cases))
                vset = new_vset

            geom = ''
            for f in features:
                if f[0] == n:
                    geom = f[2]
                    break

            value = hierarchies[n].get_type_covering(vset)
            if value != n:  # don't bother if it doesn't constrain anything
                mylang.add(type + ' := [ ' + geom + ' ' + value + ' ].')

        supertype = type

    # generate subtypes to patch the direct-inverse/unexpressed type conflict
    mylang.add_literal(';;; Direct-inverse/unexpressed subtypes for compatibility with argument optionality')

    # add subtypes for each left-branching leaf on the scale
    for i in range(1, scale_len):
        type = 'dir-inv-' + str(i)
        subtype = type + '-unexpressed'
        mylang.add(subtype + ' := ' + type + ' & unexpressed.')

    # now add the last, right-branching leaf
    type = 'dir-inv-non-' + str(scale_len-1)
    subtype = type + '-unexpressed'
    mylang.add(subtype + ' := ' + type + ' & unexpressed.')

############################
### LEXICAL RULE METHODS ###
############################

def write_dir_inv_lexrule_supertypes(choices, mylang):
    mylang.set_section('dirinv')
    mylang.add_literal(';;; Direct-inverse lexical rules')
    mylang.add('dir-lex-rule := add-only-no-ccont-rule & ' + \
               '[ SYNSEM.' + dirinv_geom + ' dir ].')
    mylang.add('inv-lex-rule := add-only-no-ccont-rule & ' + \
               '[ SYNSEM.' + dirinv_geom + ' inv ].')
    if info.has_SCARGS(choices):
        mylang.add('dir-lex-rule := \
                   [ SC-ARGS < #1, #2 >, \
                     SYNSEM.LOCAL.CAT.VAL [ SUBJ < #1 >, \
                                            COMPS < #2 > ] ].')
        mylang.add('inv-lex-rule := \
                   [ SC-ARGS < #1, #2 >, \
                     SYNSEM.LOCAL.CAT.VAL [ SUBJ < #2 >, \
                                            COMPS < #1 > ] ].')

def add_lexrules(choices):
    scale_size = len(choices.get('direct-inverse.scale', ()))
    equal = choices.get('direct-inverse.scale-equal')

    for lex in choices.get(f'lexicon.verb', ()):
        n = get_name(lex)

        # If the lexical type is a direct-inverse verb, later rules
        # should use its mandatory rules as input rather than the
        # lexical type.  Create those rules here and put their supertype
        # in the root_dict.
        if lex.get('valence', '').endswith('dirinv'):
            name = n + '-dir-inv'
            choices.set('morphology.verb-pc', {
                'name': name,
                'inputs': [lex.full_key],
                # The order doesn't really matter for lrules, so just put something
                'order': 'suffix',
            })
            pc = next(pc for pc in choices.get('morphology.verb-pc') if pc['name'] == name)
            reassign_inputs(choices, lex.full_key, pc.full_key)
            # make the lexical type require the pc
            lex.set('require.others', pc.full_key)

            # regarding the calculating of the keys, consider scale_size is 2:
            #   i = 0 or 1, so direc_lrt_key = (0*2)+0+1 = 1, or (1*2)+1+1 = 4
            #   j = 1 or 2, so lrt_key = (0*2)+0+1+1 = 2, (0*2)+0+2+1 = 3, or
            #                            (1*2)+1+1+1 = 5, (1*2)+1+2+1 = 6
            for i, direc in enumerate(['dir', 'inv']):
                direc_lrt_key = pc.full_key + '.lrt' + str((i * scale_size) + i + 1)
                choices[direc_lrt_key + '.name'] = '-'.join([n, direc])
                choices[direc_lrt_key + '.feat1_name'] = 'direction'
                choices[direc_lrt_key + '.feat1_value'] = direc
                for j in range(1, scale_size+1):
                    if j == scale_size and not (equal == 'direct' and direc == 'dir'):
                        break
                    lrt_key = f'morphology.{pc.full_key}.lrt{str((i * scale_size) + i + j + 1)}'
                    subj_type, comps_type = get_subj_comps_types(j, scale_size,
                                                                 direc, equal)
                    choices[f'{lrt_key}.name'] = '-'.join([n, direc, str(j)])
                    choices[f'{lrt_key}.supertypes'] = direc_lrt_key
                    choices[f'{lrt_key}.feat1.name'] = 'dirinv-type'
                    choices[f'{lrt_key}.feat1.head'] = 'subj'
                    choices[f'{lrt_key}.feat1.value'] = subj_type
                    choices[f'{lrt_key}.feat2.name'] = 'dirinv-type'
                    choices[f'{lrt_key}.feat2.head'] = 'obj'
                    choices[f'{lrt_key}.feat2.value'] = comps_type
                    # add an empty lexical rule instance
                    choices[f'{lrt_key}.lri1.inflecting'] = 'no'
                    choices[f'{lrt_key}.lri1.orth'] = ''

def reassign_inputs(choices, inp_key, pc_key):
    for lexprefix in ALL_LEX_TYPES:
        for pc in choices.get(f'morphology.{lexprefix}-pc', ()):
            if pc.full_key == pc_key: continue
            inputs = pc.get('inputs', ())
            if inp_key in inputs:
                pc['inputs'] = [i if i != inp_key else pc_key for i in inputs]
