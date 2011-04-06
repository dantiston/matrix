# find out whether verbal clusters

def determine_vcluster(auxcomp, auxorder, wo, ch):

  vcluster = False
  if ch.get('has-aux') == 'yes':
    if ch.get('verb-cluster') == 'yes':
      vcluster = True
    elif auxcomp == 'vp':
      if (wo == 'v-initial' and auxorder == 'before') or (wo == 'v-final' and auxorder == 'after'):
        vcluster = True
    elif auxcomp == 'v':
      if wo == 'v-initial' or wo == 'v-final' or wo == 'osv' or wo == 'vso':
        vcluster = True
      if wo == 'sov' or wo == 'ovs':
        if auxorder == 'before':
          vcluster = True
      if wo == 'vos' or wo == 'svo':
        if auxorder == 'after':
          vcluster = True
      if wo == 'free' and ch.get('multiple-aux') == 'yes':
        vcluster = True
  return vcluster



