from gmcs.lib import TDLHierarchy


######################################################################
# customize_tense()
# Create tense feature value hierarchies per the user's choices

def init_tense_hierarchy(ch, hierarchies):
    hier = TDLHierarchy('tense')

    tdefn = ch.get('tense-aspect-mood.tense-definition')
    if tdefn:
        if tdefn == 'choose':
            ppflist = []
            for ten in ('nonfuture', 'nonpast', 'past', 'present', 'future' ):

                if f'tense-aspect-mood.{ten}' in ch:
                    if ten not in ppflist:
                        hier.add(ten, 'tense')

                    for subtype in ch.get(f'tense-aspect-mood.{ten}-subtype', ()):
                        st = subtype.get('name','')
                        hier.add(st, ten)

                    if ten == 'nonfuture':
                        for moreten in ('past', 'present'):
                            if f'tense-aspect-mood.{moreten}' in ch:
                                hier.add(moreten, ten)
                                ppflist.append(moreten)

                    if ten == 'nonpast':
                        for moreten in ('present', 'future'):
                            if f'tense-aspect-mood.{moreten}' in ch:
                                hier.add(moreten, ten)
                                ppflist.append(moreten)

        elif tdefn == 'build':

            for tense in ch.get('tense-aspect-mood.tense', ()):
                name = tense.get('name')

                for supertype in tense.get('supertype', ()):
                    supername = supertype.get('name')
                    hier.add(name, supername)

    if not hier.is_empty():
        hierarchies[hier.name] = hier


def customize_tense(mylang, hierarchies):
    if 'tense' in hierarchies:
        hierarchies['tense'].save(mylang, False)


######################################################################
# customize_aspect()
# Create viewpoint aspect feature value definitions per the user's choices

def init_aspect_hierarchy(ch, hierarchies):
    hier = TDLHierarchy('aspect')

    for aspect in ch.get('tense-aspect-mood.aspect',[]):
        name = aspect.get('name')
        for supertype in aspect.get('supertype', []):
            supername = supertype.get('name')
            hier.add(name, supername)

    if not hier.is_empty():
        hierarchies[hier.name] = hier
    elif ch.get('tense-aspect-mood.perimper'):
        for asp in ('perfective', 'imperfective'):
            name = asp
            supername = 'aspect'
            hier.add(name, supername)
            hierarchies[hier.name] = hier

def customize_aspect(mylang, hierarchies):
    if 'aspect' in hierarchies:
        hierarchies['aspect'].save(mylang, False)

# customize_situation()
# Create situation aspect feature value definitions per the user's choices

def init_situation_hierarchy(ch, hierarchies):
    hier = TDLHierarchy('situation')

    for situation in ch.get('tense-aspect-mood.situation',[]):
        name = situation.get('name')
        for supertype in situation.get('supertype',[]):
            supername = supertype.get('name')
            hier.add(name, supername)

    if not hier.is_empty():
        hierarchies[hier.name] = hier

def customize_situation(mylang, hierarchies):
    if 'situation' in hierarchies:
        mylang.set_section('features')
        mylang.add('situation := sort.')
        mylang.add('tam :+ [SITUATION situation].', section='addenda')
        hierarchies['situation'].save(mylang, False)

######################################################################
# customize_mood()
# Create mood feature value definitions per the user's choices

def init_mood_hierarchy(ch, hierarchies):
    hier = TDLHierarchy('mood')

    for mood in ch.get('tense-aspect-mood.mood', ()):
        name = mood.get('name')
        for supertype in mood.get('supertype',[]):
            supername = supertype.get('name')
            hier.add(name, supername)

    if not hier.is_empty():
        hierarchies[hier.name] = hier
    elif ch.get('tense-aspect-mood.subjind'):
        for md in ('subjunctive', 'indicative'):
            name = md
            supername = 'mood'
            hier.add(name, supername)
            hierarchies[hier.name] = hier

def customize_mood(mylang, hierarchies):
    if 'mood' in hierarchies:
        hierarchies['mood'].save(mylang, False)


###############################################################
# customize_form()

def init_form_hierarchy(ch, hierarchies):
    """
    Create the FORM hierarchies associated with the user's choices
    about verb forms
    """
    hier = TDLHierarchy('form')
    if 'other-features.form-fin-nf' in ch:
        hier.add('nonfinite', 'form')
        hier.add('finite', 'form')
        for subform in ch.get('other-features.form-subtype', ()):
            hier.add(subform.get('name'), subform.get('supertype'))
    if not hier.is_empty():
        hierarchies[hier.name] = hier


def customize_form(mylang, hierarchies):
    if 'form' in hierarchies:
        mylang.add('head :+ [FORM form].', section='addenda')
        hierarchies['form'].save(mylang)

def init_verbal_hierarchies(ch, hierarchies):
    init_tense_hierarchy(ch, hierarchies)
    init_aspect_hierarchy(ch, hierarchies)
    init_situation_hierarchy(ch, hierarchies)
    init_mood_hierarchy(ch, hierarchies)
    init_form_hierarchy(ch, hierarchies)

def customize_verbal_features(mylang, hierarchies):
    customize_form(mylang, hierarchies)
    customize_tense(mylang, hierarchies)
    customize_aspect(mylang, hierarchies)
    customize_situation(mylang, hierarchies)
    customize_mood(mylang, hierarchies)

def make_vpm_order(name, h, o):
    if name not in list(h.keys()): return []
    for n in h[name]:
        make_vpm_order(n, h, o)
    o.append(name)
    return o

def create_vpm_tense(ch, vpm):
    literal = ''
    _hier = {}
    #default_tense = ''

    tdefn = ch.get('tense-aspect-mood.tense-definition')
    if tdefn == 'choose':
        for ten in ('present', 'nonpast', 'past', 'nonfuture', 'future' ):
            if ten in ch:
                literal += '  ' + ten + ' <> ' + ten + '\n'

    elif tdefn == 'build':
        tenses = ch.get('tense-aspect-mood.tense', ())
        for tense in tenses:
            name = tense.get('name')
            if name not in _hier:
                _hier[name] = []
            for supertype in tense.get('supertype', []):
                supername = supertype.get('name')
                if supername not in _hier:
                    _hier[supername] = [name]
                else:
                    _hier[supername].append(name)

        order = make_vpm_order('tense', _hier, [])
        for name in order:
            if name == 'tense': continue
            literal += '  ' + name + ' <> ' + name + '\n'

    if literal != '':
        vpm.add_literal('E.TENSE : E.TENSE\n' + literal + '  * <> *')
    else:
        vpm.add_literal('E.TENSE : E.TENSE\n  * <> *')


def create_vpm_aspect(ch, vpm):
    literal = ''
    _hier = {}
    for aspect in ch.get('tense-aspect-mood.aspect', ()):
        name = aspect.get('name')
        if name not in _hier:
            _hier[name] = []
        for supertype in aspect.get('supertype', ()):
            supername = supertype.get('name')
            if supername not in _hier:
                _hier[supername] = [name]
            else:
                _hier[supername].append(name)

    order = make_vpm_order('aspect', _hier, [])
    for name in order:
        if name == 'aspect': continue
        literal += '  ' + name + ' <> ' + name + '\n'

    if literal != '':
        vpm.add_literal('E.ASPECT : E.ASPECT\n' + literal + '  * <> *')
    else:
        vpm.add_literal('E.ASPECT : E.ASPECT\n  * <> *')

def create_vpm_mood(ch, vpm):
    literal = ''
    _hier = {}

    for mood in ch.get('tense-aspect-mood.mood', ()):
        name = mood.get('name')
        if name not in _hier:
            _hier[name] = []
        for supertype in mood.get('supertype', ()):
            supername = supertype.get('name')
            if supername not in _hier:
                _hier[supername] = [name]
            else:
                _hier[supername].append(name)

    order = make_vpm_order('mood', _hier, [])
    for name in order:
        if name == 'mood': continue
        literal += '  ' + name + ' <> ' + name + '\n'

    if literal != '':
        vpm.add_literal('E.MOOD : E.MOOD\n' + literal + '  * <> *')
        #vpm.add_literal('E.MOOD : E.MOOD\n' + literal + '  * <> !')
    else:
        vpm.add_literal('E.MOOD : E.MOOD\n  * <> *')

def create_vpm_situation(ch, vpm):
    literal = ''
    _hier = {}

    for situation in ch.get('tense-aspect-mood.situation', ()):
        name = situation.get('name')
        if name not in _hier:
            _hier[name] = []
        for supertype in situation.get('supertype',  ()):
            supername = supertype.get('name')
            if supername not in _hier:
                _hier[supername] = [name]
            else:
                _hier[supername].append(name)

    order = make_vpm_order('situation', _hier, [])
    for name in order:
        if name == 'situation': continue
        literal += '  ' + name + ' <> ' + name + '\n'

    if literal != '':
        vpm.add_literal('E.SITUATION : E.SITUATION\n' + literal + '  * <> *')
        #vpm.add_literal('E.SITUATION : E.SITUATION\n' + literal + '  * <> !')
    else:
        vpm.add_literal('E.SITUATION : E.SITUATION\n  * <> *')


def create_vpm_blocks(ch, vpm, hierarchies):
    create_vpm_tense(ch, vpm)
    create_vpm_aspect(ch, vpm)
    create_vpm_mood(ch, vpm)
    if 'situation' in hierarchies:
        create_vpm_situation(ch, vpm)
