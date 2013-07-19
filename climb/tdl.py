### $Id: tdl.py,v 1.17 2008-07-24 11:16:41 sfd Exp $

######################################################################
# imports

import sys
import os
import copy
###########################################################################
# TDL Tokenization
#
# isid(s)
#   return true iff s is a valid TDL identifier (or '...')
#
# TDLtokenize(s)
#  convert s list of TDL tokens and return that list
###########################################################################

def isid(s):
  if s == '...':
    return True
  for c in s:
    if not (c.isalnum() or ord(c) > 127 or c in ['-', '+', '_', '*', '%']):
      return False
  return True

def TDLtokenize(s):
  tok = ""
  val = []

  while len(s) > 0:
    s = s.strip()
    if isid(s[0]) or s[0] == '#' or s[0] == '\'':
      i = 1
      while isid(s[i:i + 1]):
        i += 1
      val.append(s[0:i])
      s = s[i:]
    elif s[0] == '"':
      i = 1
      while i < len(s) and s[i] != '"':
        i += 1
      i += 1
      val.append(s[0:i]) # include the quotes
      s = s[i:]
    elif s[0] == '<':
      if s[1:2] == '!':
        val.append(s[0:2])
        s = s[2:]
      else:
        val.append(s[0])
        s = s[1:]
    elif s[0] == '!':
      if s[1:2] == '>':
        val.append(s[0:2])
        s = s[2:]
      else:
        val.append('Unrecognized token "' + s[0] + '"')
        s = ""
    elif s[0] == ':':
      if s[1:2] == '=' or s[1:2] == '<' or s[1:2] == '+':
        val.append(s[0:2])
        s = s[2:]
      else:
        val.append('Unrecognized token "' + s[0] + '"')
        s = ""
    elif s[0:3] == '...':
      val.append(s[0:3])
      s = s[3:]
    elif s[0] == '[' or s[0] == ']' or \
         s[0] == '&' or s[0] == ',' or \
         s[0] == '.' or s[0] == '>':
      val.append(s[0])
      s = s[1:]
    else:
      val.append('Unrecognized token "' + s[0] + '"')
      s = ""

  return val


###########################################################################
# TDL Parsing classes and functions
###########################################################################

###########################################################################
# output

debug_write = False

tdl_file = sys.stdout
tdl_indent = 0

def TDLset_file(f):
  global tdl_file
  tdl_file = f

def TDLget_indent():
  global tdl_indent
  return tdl_indent

def TDLset_indent(indent):
  global tdl_indent
  tdl_indent = indent

def TDLwrite(s):
  global tdl_indent
  global tdl_file
  tdl_file.write(s)
  i = s.rfind('\n')
  if i != -1:
    tdl_indent = len(s) - (i + 1)
  else:
    tdl_indent += len(s)


###########################################################################
# A TDLelem is a node in a TDL parse tree.  This is an abstract class; the
# specific classes below derive from it.

class TDLelem(object):
  def add(self, ch):
    self.child.append(ch)

  def ordered(self):
    return False

  def set_comment(self, comment):
    pass

  def get_comment(self):
    return ''

  def set_type(self, type_name):
    pass

  def get_type(self):
    return ''

  def sort(self):
    new_child = []
    # corefs first
    for c in self.child:
      if isinstance(c, TDLelem_coref):
        new_child.append(c)
    # ...then type names
    for c in self.child:
      if isinstance(c, TDLelem_type):
        new_child.append(c)
    # ...and finally everything else
    for c in self.child:
      if not isinstance(c, TDLelem_coref) and not isinstance(c, TDLelem_type):
        new_child.append(c)
    self.child = new_child
        

###########################################################################
# A TDLelem_literal is an unprocessed string.  It's used for things like
# inflectional rules that must be formatted in a particular way, and
# which aren't expected to merge:
#
# cs1n-bottom :=
#   %prefix (* foo)
#   cs1n-bottom-coord-rule.

class TDLelem_literal(object):
  def __init__(self, literal):
    self.child = []
    self.comment = ''
    self.one_line = False
    self.section = ''
    self.literal = literal

  def write(self):
    if self.comment:
      for l in self.comment.split('\n'):
        TDLwrite('; ' + l + '\n')
      TDLwrite('\n')

    if debug_write:
      TDLwrite('literal\n')

    tdl_file.write(self.literal)

  def set_comment(self, comment):
    self.comment = comment

  def get_comment(self):
    return self.comment

  def set_type(self, type_name):
    pass

  def get_type(self):
    return ''


###########################################################################
# A TDLelem_typedef corresponds to a statement like:
#
# subj-head-phrase := basic-head-subj-phrase & head-final &
#  [ HEAD-DTR.SYNSEM.LOCAL.CAT.VAL.COMPS < > ].
#
# ...as well as a comment preceding the statement

class TDLelem_typedef(TDLelem):
  def __init__(self, type, op):
    self.child = []
    self.comment = ''
    self.one_line = False
    self.section = ''
    self.type = type
    self.op = op

  def write(self):
    if self.comment and not self.one_line:
      for l in self.comment.split('\n'):
        TDLwrite('; ' + l + '\n')
      TDLwrite('\n')

    if debug_write:
      TDLwrite('typedef\n')
      
    TDLwrite(self.type + " " + self.op + " ")
    TDLset_indent(2)
    for ch in self.child:
      ch.write()

    TDLwrite('.')
    if self.one_line and self.comment:
      TDLwrite('  ; ' + self.comment)

  def set_comment(self, comment):
    self.comment = comment

  def get_comment(self):
    return self.comment

  def set_type(self, type_name):
    self.type = type_name

  def get_type(self):
    return self.type

  def set_one_line(self, one_line):
    self.one_line = one_line

  def get_one_line(self):
    return self.one_line


###########################################################################
# A TDLelem_type corresponds to an identifier (e.g. basic-verb-lex)

class TDLelem_type(TDLelem):
  def __init__(self, type):
    self.child = []
    self.type = type

  def write(self):
    if debug_write:
      TDLwrite('type\n')

    TDLwrite(self.type)


###########################################################################
# A TDLelem_coref corresponds to a coreference (e.g. #comps)

class TDLelem_coref(TDLelem):
  def __init__(self, coref):
    self.child = []
    self.coref = coref

  def write(self):
    if debug_write:
      TDLwrite('coref\n')

    TDLwrite(self.coref)


###########################################################################
# A TDLelem_conj corresponds to a list of TDL statements conjoined using
# the & operator.

class TDLelem_conj(TDLelem):
  def __init__(self):
    self.child = []

  def write(self):
    if debug_write:
      TDLwrite('conj\n')

    old_i = TDLget_indent()
  
    last_was_feat = False
    for ch in self.child[0:1]:
      if ch:
        ch.write()
        last_was_feat = (isinstance(ch, TDLelem_feat));
    for ch in self.child[1:]:
      cur_is_feat = (isinstance(ch, TDLelem_feat));
      # don't print empty AVMs ([]) unless it's the only thing
      if cur_is_feat and len(ch.child) == 0: continue
      if cur_is_feat or last_was_feat:
        TDLwrite(' &\n')
        for i in range(old_i):
          TDLwrite(' ')
      else:
        TDLwrite(' & ')
      if ch is not None:
        ch.write()
      last_was_feat = cur_is_feat


###########################################################################
# A TDLelem_feat corresponds to an attribute-value matrix
# (e.g. [ HEAD noun, VAL.SPR < > ])

class TDLelem_feat(TDLelem):
  def __init__(self):
    self.child = []
    self.empty_list = False

  # Does self contain only a FIRST and a REST?  If so, self can be
  # printed with '<' and '>' (and maybe as a list).
  def is_cons(self):
    if self.empty_list:
      return True
    c0 = None
    c1 = None
    if len(self.child) == 2:
      c0 = self.child[0]
      c1 = self.child[1]
    return c0 and c1 and \
           isinstance(c0, TDLelem_av) and \
           isinstance(c1, TDLelem_av) and \
           ((c0.attr == 'FIRST' and c1.attr == 'REST') or \
            (c0.attr == 'REST' and c1.attr == 'FIRST'))

  # Does self contain only a FIRST and a REST, and is the value of REST
  # either the type 'null' or also a list?  If so, self can be printed
  # as a list.
  def is_list(self):
    if self.is_cons():
      c0 = self.child[0]
      c1 = self.child[1]

      if c0.attr == 'REST' and len(c0.child) == 1:
        r = c0.child[0]
      elif c1.attr == 'REST' and len(c1.child) == 1:
        r = c1.child[0]

      if r and \
         isinstance(r, TDLelem_conj) and \
         len(r.child) == 1:
        c = r.child[0]
        return (isinstance(c, TDLelem_type) and c.type == 'null') or \
               (isinstance(c, TDLelem_feat) and c.is_list())

    return False

  def write_cons(self):
    if self.empty_list:
      TDLwrite('< >')
      return
    islist = self.is_list() # just call once and store the result
    cur = self
    first_elem = True
    while cur:
      if first_elem:
        TDLwrite('< ')
        old_i = TDLget_indent()
        first_elem = False
      else:
        # pairs will never get this far
        TDLwrite(',\n')
        for i in range(old_i):
          TDLwrite(' ')

      if cur.child[0].attr == 'REST':
        f = cur.child[1].child[0]
        r = cur.child[0].child[0].child[0]
      else:
        f = cur.child[0].child[0]
        r = cur.child[1].child[0].child[0]

      f.write() # write value of FIRST

      if islist and isinstance(r, TDLelem_type) and r.type == 'null':
        break
      elif not islist:
        TDLwrite(' . ')
        r.write()
        break
      else:
        cur = r
    TDLwrite(' >')

  def write(self):
    if debug_write:
      TDLwrite('feat\n')

    if self.is_cons():
      self.write_cons()
    else:
      TDLwrite('[')
      old_i = TDLget_indent() + 1
      for ch in self.child[0:1]:
        TDLwrite(' ')
        ch.write()
      for ch in self.child[1:]:
        TDLwrite(',\n')
        for i in range(old_i):
          TDLwrite(' ')
        ch.write()
      TDLwrite(' ]')


###########################################################################
# A TDLelem_av corresponds to a single attribute-value pair
# (e.g. HEAD noun)

class TDLelem_av(TDLelem):
  def __init__(self, attr):
    self.child = []
    self.attr = attr

  def write_dotted(self):
    c = self
    if len(c.child) == 1 and isinstance(c.child[0], TDLelem_conj):
      c = c.child[0]
      if len(c.child) == 1 and isinstance(c.child[0], TDLelem_feat):
        c = c.child[0]
        if len(c.child) == 1 and isinstance(c.child[0], TDLelem_av):
          c = c.child[0]
          TDLwrite(self.attr)
          TDLwrite('.')
          c.write()
          return True
    return False

  def write(self):
    if debug_write:
      TDLwrite('av\n')

    if not self.write_dotted():
      TDLwrite(self.attr)
      TDLwrite(' ')
      for ch in self.child:
        ch.write()


###########################################################################
# A TDLelem_dlist corresponds to a diff-list (e.g. <! [ PRED "_q_rel" ] !>)

class TDLelem_dlist(TDLelem):
  def __init__(self):
    self.child = []

  def write(self):
    if debug_write:
      TDLwrite('dlist\n')

    TDLwrite('<! ')
    for ch in self.child[0:1]:
      ch.write()
    for ch in self.child[1:]:
      TDLwrite(', ')
      ch.write()
    TDLwrite(' !>')

  def ordered(self):
    return True


###########################################################################
# TDL Parsing functions
# These functions, one for each of the types of TDL element, all consume
# tokens from the global list "tok".

tok = []

def TDLparse_type():
  global tok
  return TDLelem_type(tok.pop(0))

def TDLparse_coref():
  global tok
  return TDLelem_coref(tok.pop(0))

def TDLparse_av():
  global tok
  attr = tok.pop(0)
  elem = TDLelem_av(attr)
  if tok[0] == '.':
    tok.pop(0) # '.'
    cur = elem
    temp = TDLelem_conj()
    cur.add(temp)
    cur = temp
    temp = TDLelem_feat()
    cur.add(temp)
    cur = temp
    cur.add(TDLparse_av())
  else:
    elem.add(TDLparse_conj())
  return elem

def TDLparse_feat():
  global tok
  tok.pop(0) # '['
  elem = TDLelem_feat()
  while tok[0] != ']':
    elem.add(TDLparse_av())
    if tok[0] == ',':
      tok.pop(0)
  tok.pop(0) # ']'
  return elem

def TDLparse_list():
  global tok
  tok.pop(0) # '<'

  term = True       # is the list terminated (i.e. doesn't end in ...)?
  seen_dot = False  # were the items separated by a .?
  child = []
  while tok[0] != '>':
    if tok[0] == '...':
      term = False
    child.append(TDLparse_conj())
    if tok[0] == ',':
      tok.pop(0)
    elif tok[0] == '.':
      seen_dot = True
      tok.pop(0)
  tok.pop(0) # '>'

  # We've got the list elements, and the variable seen_dot tells us
  # if it ends with a null (False) or not (True).  Loop through them
  # backwards, constructing feature structures with FIRST and REST
  # as appropriate

  # first, short-circuit empty lists
  if len(child) == 0:
    elem = TDLelem_feat()
    elem.empty_list = True
    return elem

  # otherwise, deal with the contents of the child list
  elem = None
  
  # loop through all but the last child, constructing a list as we go
  for i in range(len(child) - 1):
    if elem == None:
      temp = TDLelem_feat()
      elem = temp
      cur = temp
    else:
      temp = TDLelem_conj()
      cur.add(temp)
      cur = temp
      temp = TDLelem_feat()
      cur.add(temp)
      cur = temp
    temp = TDLelem_av('FIRST')
    cur.add(temp)
    temp.add(child[i])

    # Unless we're at the end of an unterminated list...
    if term or i < len(child) - 2:
      # ...set up for the next iteration (or the finish)
      temp = TDLelem_av('REST')
      cur.add(temp)
      cur = temp # leave cur pointing to an av

  # Unless the list is unterminated...
  if term:
    # ...add the last child to the list as indicated by seen_dot
    if seen_dot:
      cur.add(child[-1])
    else:
      if elem == None:
        temp = TDLelem_feat()
        elem = temp
        cur = temp
      else:
        temp = TDLelem_conj()
        cur.add(temp)
        cur = temp
        temp = TDLelem_feat()
        cur.add(temp)
        cur = temp
      temp = TDLelem_av('FIRST')
      cur.add(temp)
      temp.add(child[-1])
      temp = TDLelem_av('REST')
      cur.add(temp)
      cur = temp
      temp = TDLelem_conj()
      cur.add(temp)
      cur = temp
      temp = TDLelem_type('null')
      cur.add(temp)
      cur = temp
  
  return elem

def TDLparse_dlist():
  global tok
  tok.pop(0) # '<!'
  elem = TDLelem_dlist()
  while tok[0] != '!>':
    elem.add(TDLparse_conj())
    if tok[0] == ',':
      tok.pop(0)
  tok.pop(0) # '!>'
  return elem

def TDLparse_term():
  global tok
  if isid(tok[0]) or tok[0][0] == '"':
    return TDLparse_type()
  elif tok[0][0] == '#':
    return TDLparse_coref()
  elif tok[0] == '[':
    return TDLparse_feat()
  elif tok[0] == '<':
    return TDLparse_list()
  elif tok[0] == '<!':
    return TDLparse_dlist()

def TDLparse_conj():
  global tok
  elem = TDLelem_conj()
  elem.add(TDLparse_term())
  while tok[0] == '&':
    tok.pop(0)
    elem.add(TDLparse_term())
  return elem

def TDLparse_typedef():
  global tok
  type = tok.pop(0) # the type name
  op = tok.pop(0)
  while not op in (':=', ':<', ':+'):
    type += '_' + op  # turn spaces in the type name to _'s
    op = tok.pop(0)
  #hack, from somewhere _1 is added to type names, removing this
  elem = TDLelem_typedef(type, op)
  elem.add(TDLparse_conj())
  tok.pop(0) # '.'
  return elem

def TDLparse(s):
  global tok
  tok = TDLtokenize(s)
  return TDLparse_typedef()


###########################################################################
# TDLmergeable
#   type:  e1.type == e2.type
#   coref: e1.coref == e2.coref
#   av:    same attr names
#   conj:  always true
#   feat:  always true
#   list:  always true
#   dlist: always true

def TDLmergeable(e1, e2):
  if type(e1) != type(e2):
    return False
  if isinstance(e1, TDLelem_typedef):
    return e1.type == e2.type and e1.op == e2.op
  if isinstance(e1, TDLelem_type):
    return e1.type == e2.type
  if isinstance(e1, TDLelem_coref):
    return e1.coref == e2.coref
  if isinstance(e1, TDLelem_av):
    return e1.attr == e2.attr
  if (isinstance(e1, TDLelem_conj) or \
      isinstance(e1, TDLelem_feat) or \
      isinstance(e1, TDLelem_dlist)):
    return True


###########################################################################
# TDLmerge takes two TDLelem_typedef, merges them together as high up in
# the tree as possible, and returns the merged TDLelem_typedef.

def TDLmerge(e1, e2):
  if TDLmergeable(e1, e2):
    e0 = copy.copy(e1)
    e0.child = []

    c1 = e1.get_comment()
    c2 = e2.get_comment()
    c0 = c1
    if c1 != c2:  # if the comments are the same, don't duplicate
      if len(c1) and len(c2):
        c0 += '\n\n'
      c0 += c2
    e0.set_comment(c0)

    # if the elements are ordered (list or dlist), merge the list
    # items in order.  That is, <a,b,c> + <A,B,C> = <a&A,b&B,c&C>.
    if e1.ordered():
      for i in range(max(len(e1.child), len(e2.child))):
        if i < len(e1.child) and i < len(e2.child) and \
           TDLmergeable(e1.child[i], e2.child[i]):
          e0.add(TDLmerge(e1.child[i], e2.child[i]))
        else:
          if i < len(e1.child):
            e0.add(copy.copy(e1.child[i]))
          if i < len(e2.child):
            e0.add(copy.copy(e2.child[i]))
    else:
      for c in e1.child + e2.child:
        handled = False
        for c0 in e0.child:
          if TDLmergeable(c0, c):
            e0.child.remove(c0)
            e0.add(TDLmerge(c0, c))
            handled = True
            break
        if not handled:
          e0.add(copy.copy(c))
  else:
    e0 = TDLelem_conj()
    e0.add(copy.copy(e1))
    e0.add(copy.copy(e2))

  e0.sort()

  return e0

###########################################################################
# A TDLsection describes a section in a TDLfile.  It has four attributes:
#   name (the unique name by which the section can be addressed internally)
#   comment (the comment that will precede the section)
#   major (Boolean; True iff this is a major section
#   force (Boolean; True iff the comment should appear even if the section
#          is empty)
class TDLsection(object):
  name = ''
  comment = ''
  major = True
  force = False


###########################################################################
# A TDLfile contains the contents of a single .tdl file.  It is initialized
# with a file name, to which it will be eventually saved.  Statements can
# be added to the TDLfile using the add() method.

class TDLfile(object):
  def __init__(self, file_name):
    self.file_name = file_name  # we'll eventually save to this file
    self.typedefs = []
    self.sections = []
    self.section = ''

  def define_sections(self, sections):
    """
    Use the passed-in list of sections for this file.  The sections
    list is a list of quadruples, each of which contains:
      name (string)
      comment (string)
      major (Boolean)
      force (Boolean)
    (see TDLsection above for an explanation of these)
    e.g., ['addenda', 'Matrix Type Addenda', True, False]).
    """
    for s in sections:
      newsec = TDLsection()
      newsec.name = s[0]
      newsec.comment = s[1]
      newsec.major = s[2]
      newsec.force = s[3]
      self.sections += [newsec]

  def define_climb_sections(self):
    """
    Use the passed-in list of sections for this file.  The sections
    list is a list of quadruples, each of which contains:
      name (string)
      comment (string)
      major (Boolean)
      force (Boolean) 
    For CLIMB files, a fixed number of sections is defined, 
    namely all tdl files to be created.
    """
    sections = [['mylang', 'File=Language Specific', True, False],
               ['features', 'section=features', True, False],
               ['rules', 'File=rules', True, False],
               ['lrules', 'File=lrules', True, False],
               ['irules', 'File=irules', True, True],
               ['lexicon', 'File=lexicon', True, False],
               ['roots', 'File=roots', True, False]]

    self.define_sections(sections)


  def set_section(self, section):
    """
    Set the current section.  All subsequent typedefs or literals
    added will be a part of this section (unless they explicitly
    override the section) until the next call to set_section().
    """
    self.section = section


  def write_comment(self, comment, major):
    """
    Write out a comment.  If major is True, write a three-line
    (i.e. major-section) comment; otherwise, write a one-line comment;
    """
    if major:
      TDLwrite((len(comment) + 6) * ';' + '\n')
    TDLwrite(';;; ' + comment + '\n')
    if major:
      TDLwrite((len(comment) + 6) * ';' + '\n')


  def save(self):
    self.disambiguate_types()

    f = open(self.file_name, 'w')
    TDLset_file(f)

    # We probably only need this for lexicon.tdl, but to be safe let's
    # put it on all TDL files
    TDLwrite(';;; -*- Mode: TDL; Coding: utf-8 -*-\n')

    # make sure there's an "empty" section so that typedefs not
    # assigned to a section still get written out
    sections = self.sections
    has_empty = False
    for s in sections:
      if s.name == '':
        has_empty = True
        break
    if not has_empty:
      sections = [TDLsection()] + sections

    # pass through the list of sections, for each writing out a
    # header comment and all typedefs in the section
    first_typedef = True
    last_was_one_line = False
    for s in sections:
      comment_written = False
      if s.force:
        if first_typedef:
          first_typedef = False
        else:
          TDLwrite('\n')
        self.write_comment(s.comment, s.major)
        comment_written = True

      for t in self.typedefs:
        if t.section == s.name:
          if first_typedef:
            first_typedef = False
          elif not (last_was_one_line and t.one_line):
            TDLwrite('\n') # double-space unless two one-lines in a row

          if not comment_written and s.comment:
            self.write_comment(s.comment, s.major)
            TDLwrite('\n')
            comment_written = True
          
          t.write()
          TDLwrite('\n')
          last_was_one_line = t.one_line
    
    f.close()


  def disambiguate_types(self):
    """
    Pass through the contents of the TDL file.  Ensure that every type
    defined is unique.  If not, make it unique my appending _1, _2, etc.
    """
    type_count = {}
    for i in range(len(self.typedefs)):
      t = self.typedefs[i].get_type()
      if type_count.has_key(t):
        type_count[t] += 1
      else:
        type_count[t] = 1

    for i in range(len(self.typedefs)):
      t = self.typedefs[i].get_type()
      if type_count[t] > 1:
        index = 1
        new_type = t + '_' + str(index)
        while type_count.has_key(new_type):
          index += 1
          new_type = t + '_' + str(index)
        self.typedefs[i].set_type(new_type)
        type_count[new_type] = 1


  def dump(self):
    TDLset_file(sys.stdout)
    for t in self.typedefs:
      t.write()


  def add(self, tdl_type,
          comment = '', one_line = False, merge = False, section = ''):
    """
    Add a type definition to this file, merging with an existing
    definition if possible.
    """
    typedef = TDLparse(tdl_type)
    typedef.set_comment(comment)
    typedef.set_one_line(one_line)

    typedef.section = section
    if not section:
      typedef.section = self.section

    handled = False
    for i in range(len(self.typedefs) - 1, -1, -1):
      if TDLmergeable(self.typedefs[i], typedef):
        self.typedefs[i] = TDLmerge(self.typedefs[i], typedef)
        handled = True
        break
    if not handled:
      self.typedefs.append(typedef)


  def add_comment(self, tdl_type, comment):
    """
    Add a comment to an existing type in this file
    """
    self.add(tdl_type + ':= [].', comment)


  def add_literal(self, literal,
                  comment = '', section = ''):
    """
    Add a literal string (which will never merge) to this file
    """
    l = TDLelem_literal(literal)
    l.set_comment(comment)

    l.section = section
    if not section:
      l.section = self.section

    self.typedefs.append(l)

##########Additional functions for path abbreviation and completion


def TDLparse_abbr(s, fg_files):
  global tok
  tok_fg_dict = TDLtokenize_abbr(s, fg_files)
  tok = tok_fg_dict[0]
  return [TDLparse_typedef(), tok_fg_dict[1]]


def TDLparse_compl(s, fg_files, begin_type):
  global tok
  tok = TDLtokenize_compl(s, fg_files, begin_type)
  return TDLparse_typedef()


#def isid(s):
#  if s == '...':
#    return True
#  for c in s:
#    if not (c.isalnum() or ord(c) > 127 or c in ['-', '+', '_', '*', '%']):
#      return False
#  return True



def TDLtokenize_abbr(s, fg_dicts):
  tok = ""
  val = []

  temp_val = []
  while len(s) > 0:
    s = s.strip()
    if isid(s[0]) or s[0] == '#' or s[0] == '\'':
      i = 1
      while isid(s[i:i + 1]):
        i += 1
      val.append(s[0:i])
      s = s[i:]
    elif s[0] == '"':
      i = 1
      while i < len(s) and s[i] != '"':
        i += 1
      i += 1
      val.append(s[0:i]) # include the quotes
      s = s[i:]
    elif s[0] == '<':
      if s[1:2] == '!':
        val.append(s[0:2])
        s = s[2:]
      else:
        val.append(s[0])
        s = s[1:]
    elif s[0] == '!':
      if s[1:2] == '>':
        val.append(s[0:2])
        s = s[2:]
      else:
        val.append('Unrecognized token "' + s[0] + '"')
        s = ""
    elif s[0] == ':':
      if s[1:2] == '=' or s[1:2] == '<' or s[1:2] == '+':
        val.append(s[0:2])
        s = s[2:]
      else:
        val.append('Unrecognized token "' + s[0] + '"')
        s = ""
    elif s[0:3] == '...':
      val.append(s[0:3])
      s = s[3:]
    elif s[0] == '[' or s[0] == ']' or \
         s[0] == '&' or s[0] == ',' or \
         s[0] == '.' or s[0] == '>':
      val.append(s[0])
      s = s[1:]
    else:
      val.append('Unrecognized token "' + s[0] + '"')
      s = ""

  red_val_fg_dicts = abbreviate_paths_through_tokenization(val, fg_dicts)
  
  #call reduction algortithm here, after tokenization normal tdl.py can take over
  #(though check how globals across modules work..., alternative function in tdl
  # may be better....), try this first, else adapt tdl.py

  return red_val_fg_dicts

def TDLtokenize_compl(s, fg_dicts, begin_type):
  tok = ""
  val = []
  temp_val = []
  while len(s) > 0:
    s = s.strip()
    if isid(s[0]) or s[0] == '#' or s[0] == '\'':
      i = 1
      while isid(s[i:i + 1]):
        i += 1
      val.append(s[0:i])
      s = s[i:]
    elif s[0] == '"':
      i = 1
      while i < len(s) and s[i] != '"':
        i += 1
      i += 1
      val.append(s[0:i]) # include the quotes
      s = s[i:]
    elif s[0] == '<':
      if s[1:2] == '!':
        val.append(s[0:2])
        s = s[2:]
      else:
        val.append(s[0])
        s = s[1:]
    elif s[0] == '!':
      if s[1:2] == '>':
        val.append(s[0:2])
        s = s[2:]
      else:
        val.append('Unrecognized token "' + s[0] + '"')
        s = ""
    elif s[0] == ':':
      if s[1:2] == '=' or s[1:2] == '<' or s[1:2] == '+':
        val.append(s[0:2])
        s = s[2:]
      else:
        val.append('Unrecognized token "' + s[0] + '"')
        s = ""
    elif s[0:3] == '...':
      val.append(s[0:3])
      s = s[3:]
    elif s[0] == '[' or s[0] == ']' or \
         s[0] == '&' or s[0] == ',' or \
         s[0] == '.' or s[0] == '>':
      val.append(s[0])
      s = s[1:]
    else:
      val.append('Unrecognized token "' + s[0] + '"')
      s = ""

  compl_val = complete_paths_through_tokenization(val, fg_dicts, begin_type)
  #call reduction algortithm here, after tokenization normal tdl.py can take over
  #(though check how globals across modules work..., alternative function in tdl
  # may be better....), try this first, else adapt tdl.py

  return compl_val



'''Checks whether definition contains structures like ATT1.ATT2 [ ATT3 val ],
   and turns these into equivalent ATT1.ATT2.ATT3 val,'''
def clean_tok_from_single_att_val_brackets(my_tok):
  
  cleaned_toks = []
  temp_toks = []
  open_bracks = 0
  no_comma = False
  for my_t in my_tok:
    if my_t == '[':
      open_bracks += 1
      if open_bracks > 1:
        no_comma = True
      else:
        cleaned_toks.append(my_t)
    elif no_comma:
      if my_t == ']':
        open_bracks -= 1
        cleaned_toks.append('.')
        cleaned_toks += temp_toks
        temp_toks = []
      elif my_t == ',':
        no_comma = False
        cleaned_toks.append('[')
        cleaned_toks += temp_toks
        temp_toks = []
      else:
        temp_toks.append(my_t)
    elif no_comma:
      open_brack -= 1
    else:
      cleaned_toks.append(my_t)

  return cleaned_toks


def add_abbreviated_path(new_path, feat_geo_files):
   new_path = new_path.rstrip('.')
   atts = new_path.split('.')
   while ',' in atts:
     atts.remove(',')
   while '' in atts:
     atts.remove('')
   atts.reverse()
   if len(atts) > 0:
     reduced_atts = [atts[0], '.']
     att_2_type = feat_geo_files[0]
     type_2_att = feat_geo_files[1]
     for i, att in enumerate(atts):
       if att in att_2_type:
         my_type = att_2_type[att][0]
         if my_type in type_2_att:
           pot_atts = type_2_att[my_type]
           if ',' in pot_atts:
             if len(atts) > i + 1:
               reduced_atts += [atts[i+1], '.']
           elif ';' in pot_atts:
             pot_def_atts = pot_atts.split(';')
             if len(atts) > i + 1:
               if pot_def_atts[0] != atts[i + 1]:
                 if atts[i + 1] in pot_def_atts:
                   reduced_atts += [atts[i+1], '.']
           else:
             if len(atts) > i + 1:
               if pot_atts != atts[i+1] and not 'FIRST' in atts[i+1]:
                 print 'Potentially wrongly defined path: ', atts[i+1], ' ', att
                 print att, att_2_type[att]
                 print atts[i+1], att_2_type[atts[i+1]]
                 print pot_atts
       else:
         print att + '!----------'
     reduced_atts.pop()
     reduced_atts.reverse()
   else:
     reduced_atts = [new_path]
   return reduced_atts

#within LIST : dot means something else
#boolean, within list, if True add dot as before
def update_default_val(att_to_update, feat_geo_files, path = '', val=''):
  a_2_types = feat_geo_files[0]
  t_2_atts = feat_geo_files[1]
  old_val = a_2_types[att_to_update][1]
  if not 'list' in old_val:
    return None
  if not ',' in old_val:
    if path:
      my_att = path.split('.')[0]
      val = a_2_types[my_att][0]
    if val:
      new_val = old_val + ',' + val
      a_2_types[att_to_update][1] = new_val
      t_2_atts[val] += ';' + att_to_update
  else:
    if val:
      if not val in old_val:
        print 'Check if ' + old_val + ' needs to be updated with ' + val
  return [a_2_types, t_2_atts]


def update_feat_geo_files(new_path, feat_geo_files):
  atts = new_path.split('.')
  a_2_types = feat_geo_files[0]
  t_2_atts = feat_geo_files[1]
  f_feat = ''
  i_feat = ''
  for i, a in enumerate(atts):
    if a == 'FIRST':
      if len(atts) > i:
        f_feat = atts[i+1]
      j = i
      while j != 0:
        j -= 1
        if not atts[j] == 'REST' and not atts[j] == 'LIST' and not atts[j] == 'LAST':
          i_feat = atts[j]
          break
  if f_feat and i_feat:
    old_val = a_2_types[i_feat][1]
    if not ',' in old_val:
      new_intro_val = a_2_types[f_feat][0]
      if 'list' in old_val:
        new_val = old_val + ',' + new_intro_val
        a_2_types[i_feat][1] = new_val
        t_2_atts[new_intro_val] += ';' + i_feat
      else:
        print 'something is wrong, type with value', old_val, 'identified as taking lists'
  return [a_2_types, t_2_atts]

def abbreviate_paths_through_tokenization(my_tok, feat_geo_files):

  no_att_val_brack =  ['.', ',', '&',':+',':=',':<','>','!','...','\'','"','!>']
  prec_is_val = [',',']','&','>','!>']
  paths = []
  cleaned_toks = clean_tok_from_single_att_val_brackets(my_tok)
  red_toks = []
  att_to_update = ''

  new_path = ''
  open_brackets = 0
  open_list = 0
  open_dlist = 0
  open_brack_in_list = 0
  for i, my_t in enumerate(my_tok):
    
    if my_t == '[':
      open_brackets += 1
      if open_list > 0 or open_dlist > 0:
        open_brack_in_list += 1
      if new_path:
        if 'FIRST' in new_path:
          feat_geo_files = update_feat_geo_files(new_path, feat_geo_files)
        elif (open_list > 0 or open_dlist > 0) and att_to_update:
          feat_geo_files = update_default_val(att_to_update, feat_geo_files, new_path)
        new_toks = add_abbreviated_path(new_path, feat_geo_files)
        new_path = ''
        red_toks += new_toks
      red_toks.append('[')
    elif my_t == ']':
      open_brackets -= 1
      if open_list > 0 or open_dlist > 0:
        open_brack_in_list -= 1
      red_toks.append(']')
    elif my_t == '<':
      open_list += 1
      if new_path:
        #if 'FIRST' in new_path:
        #  feat_geo_files = update_feat_geo_files(new_path, feat_geo_files)
        #elif (open_list > 1 or open_dlist > 0) and att_to_update:
        #  feat_geo_files = update_default_val(att_to_update, feat_geo_files, new_path)
        new_toks = add_abbreviated_path(new_path, feat_geo_files)
        new_path = new_path.rstrip('.')
        red_toks += new_toks
        att_to_update = new_path.split('.')[-1]
        new_path = ''
      red_toks.append(my_t)
    elif my_t == '>':
      open_list -= 1
      red_toks.append(my_t)
    elif my_t == '<!':
      open_dlist += 1
      if new_path:
        #if 'FIRST' in new_path:
        #  feat_geo_files = update_feat_geo_files(new_path, feat_geo_files)
        #elif (open_list > 0 or open_dlist > 1) and att_to_update:
        #  feat_geo_files = update_default_val(att_to_update, feat_geo_files, new_path)
        new_toks = add_abbreviated_path(new_path, feat_geo_files)
        new_path = new_path.rstrip('.')
        red_toks += new_toks
        att_to_update = new_path.split('.')[-1]
        new_path = ''
      red_toks.append(my_t)
    elif my_t == '!>':
      open_dlist -= 1
      red_toks.append(my_t)
    elif (not my_t in no_att_val_brack) and (open_brackets > 0):
      next_t = my_tok[i+1]
      if not (next_t in prec_is_val):
        if not ('#' in my_t or '"' in my_t or '<' in my_t):
          new_path += my_t.upper() + '.'
        elif new_path:
          red_toks.append(new_path.rstrip('.'))
          new_path = ''
        else:
          red_toks.append(my_t)
          if not '#' in my_t:
            if (open_list > 0 or open_dlist > 0) and att_to_update:
              feat_geo_files = update_default_val(att_to_update, feat_geo_files, val=my_t)
      else:
        if 'FIRST' in new_path:
          feat_geo_files = update_feat_geo_files(new_path, feat_geo_files)
        elif (open_list > 0 or open_dlist > 0) and att_to_update and not '#' in my_t:
          feat_geo_files = update_default_val(att_to_update, feat_geo_files, new_path)
        new_toks = add_abbreviated_path(new_path, feat_geo_files)
        new_path = ''
        if new_toks[0]:
          red_toks += new_toks
        red_toks.append(my_t)
    elif not my_t == '.': 
      red_toks.append(my_t)
    elif (open_list > 0 or open_dlist > 0) and not open_brack_in_list > 0:
      red_toks.append(my_t)
    
  #all dots are introduced by abbreviated path function, except for the last one
  red_toks.append('.')    
  return [red_toks, feat_geo_files]



def get_current_type(new_toks, val_2_types):

  list_types = ['FIRST','REST']
  final_att = new_toks[-1]
  if final_att in list_types:
    i = 2
    while True:
      if len(new_toks) < i:
        intro_type = '*top*'
        break
      final_att = new_toks[-i]
      if final_att in list_types or final_att == '.':
        i += 1
      else:
        intro_type = val_2_types[final_att][1]
        if ',' in intro_type:
          intro_type = intro_type.split(',')[1].rstrip()
        break
  else:
    intro_type = val_2_types[final_att][1]
  return intro_type



def complete_paths_through_tokenization(my_tok, fg_dicts, begin_type):
  
  no_att_val_brack =  ['.', ',', '&',':+',':=',':<','>','!','...','\'','"','!>']
  prec_is_val = [',',']','&','>','!>']
  compl_toks = []
  val_2_types = fg_dicts[0]
  types_2_val = fg_dicts[1]
  curr_type = begin_type
 # def_type
  bracks_to_types = ['']
  def_types = ['']

  new_path = ''
  open_brackets = 0
  open_list = 0
  open_dlist = 0
  open_brack_in_list = 0
  for i, my_t in enumerate(my_tok):
    if my_t == '[':
      open_brackets += 1
      if open_list > 0 or open_dlist > 0:
        open_brack_in_list += 1
      if new_path:
        if open_list > 0 and not open_brack_in_list > 2:
          end_type = def_types[open_list]
        elif open_dlist > 0 and not open_brack_in_list > 2:
          end_type = def_types[open_dlist]
        else:
          end_type = bracks_to_types[open_brackets-1]
        new_toks = add_completed_path(new_path, fg_dicts, end_type, open_list + open_dlist)
        curr_type = get_current_type(new_toks, val_2_types)
        new_path = ''
        compl_toks += new_toks
      compl_toks.append('[')
      if len(bracks_to_types) <= open_brackets:
        bracks_to_types.append(curr_type)
      else:
        bracks_to_types[open_brackets] = curr_type
    elif my_t == ']':
      open_brackets -= 1
      if open_list > 0 or open_dlist > 0:
        open_brack_in_list -= 1
      compl_toks.append(']')
    elif my_t == '<':
      open_list += 1
      if new_path:
        #should be larger than 1 (just added to open list)
        if open_list > 1 and not open_brack_in_list > 1:
          end_type = def_types[open_list -1]
        elif open_dlist > 0 and not open_brack_in_list > 1:
          end_type = def_types[open_dlist]
        else:
          end_type = bracks_to_types[open_brackets]
        new_toks = add_completed_path(new_path, fg_dicts, end_type, open_list + open_dlist -1)
        curr_type = get_current_type(new_toks, val_2_types)
        compl_toks += new_toks
        new_path = ''
      compl_toks.append(my_t)
      if len(def_types) <= open_list:
        def_types.append(curr_type)
      else:
        def_types[open_list] = curr_type
    elif my_t == '>':
      open_list -= 1
      compl_toks.append(my_t)
    elif my_t == '<!':
      open_dlist += 1
      if new_path:
        if open_list > 0 and not open_brack_in_list > 1:
          end_type = def_types[open_list -1]
        elif open_dlist > 1 and not open_brack_in_list > 1:
          end_type = def_types[open_dlist]
        else:
          end_type = bracks_to_types[open_brackets]
        new_toks = add_completed_path(new_path, fg_dicts, end_type, open_list + open_dlist - 1)
        curr_type = get_current_type(new_toks, val_2_types)
        compl_toks += new_toks
        new_path = ''
      compl_toks.append(my_t)
      if len(def_types) <= open_dlist:
        def_types.append(curr_type)
      else:
        def_types[open_dlist] = curr_type
    elif my_t == '!>':
      open_dlist -= 1
      compl_toks.append(my_t)
    elif (not my_t in no_att_val_brack) and (open_brackets > 0):
      next_t = my_tok[i+1]
      if not (next_t in prec_is_val):
        if not ('#' in my_t or '"' in my_t or '<' in my_t):
          new_path += my_t.upper() + '.'
          #curr_type = val_2_types[my_t][1]
        elif new_path:
          compl_toks.append(new_path.rstrip('.'))
          new_path = ''
        else:
          compl_toks.append(my_t)
      elif new_path:
        if open_list > 0 and not open_brack_in_list > 1:
          end_type = def_types[open_list]
        elif open_dlist > 0 and not open_brack_in_list > 1:
          end_type = def_types[open_dlist]
        else:
          end_type = bracks_to_types[open_brackets]

        new_toks = add_completed_path(new_path, fg_dicts, end_type, open_list + open_dlist)
        curr_type = get_current_type(new_toks, val_2_types)
        new_path = ''
        if new_toks[0]:
          compl_toks += new_toks
        compl_toks.append(my_t)
      else:
        compl_toks.append(my_t)
    elif not my_t == '.': 
      compl_toks.append(my_t)
    elif (open_list > 0 or open_dlist > 0) and not open_brack_in_list > 0:
      compl_toks.append(my_t)
    
  #all dots are introduced by abbreviated path function, except for the last one
  compl_toks.append('.')    
  return compl_toks
  #go through list, if count bracket, create dictionary for each bracket with end type
  #if find path, go through it backward and complete (as before)
  #add completed path, rather than short path

def add_completed_path(new_path, feat_geo_files, end_type, open_list):
  new_path = new_path.rstrip('.')
  my_atts = new_path.split('.')
  att_to_introtype = feat_geo_files[0]
  intro_type_to_att = feat_geo_files[1]
  compl_path = []
  for att in my_atts:
    path_atts = create_feature_list(att, att_to_introtype, intro_type_to_att, open_list, end_type)
    path_atts.reverse()
    for ppart in path_atts:
      if compl_path:
        compl_path.append('.')
      compl_path.append(ppart)
    if not ',' in end_type:
      end_type = att_to_introtype[att][1]
    elif not (att == 'FIRST' or att == 'REST'):
      end_type = att_to_introtype[att][1]
    else:
      end_type = end_type.split(',')[1].rstrip()
  return compl_path 
     
#  for i, att in my_atts.enumerate():
#    compl_atts.append(att)
#    compl_atts.append('.')
#    itype = att_to_introtype[att][0]
#    if len(my_atts) < i and itype == end_type:
#      return compl_atts.reverse()

#    if itype in intro_type_to_att:
#      next_att = intro_type_to_att[itype]
#      if ',' in next_att:
#        if len(my_atts) >= i:
#          if not my_atts[i+1] in next_att:
#            print 'Error, ambiguous path: ' + next_att + ' cannot be lead to ' + my_atts[i+1] + ' determininstically'
#        else:
#          print 'Something fishy is going on, should have returned completed string already'
#      else:
#        if len(my_atts) >= i:
#          if not my_atts[i+1] == next_att:
#            compl_atts.append(next_att)
#            compl_atts.append('.')
#        else:
#          compl_atts.append(next_att)
#          compl_atts.append('.')



def create_feature_list(feat_name, feat_n, index_types, open_list, end_type = ''):
###END_FEAT: should be previous in list if there...
  my_p = []
  part_of_list = False
  my_types = []
  if ',' in end_type:
    my_types = end_type.split(',')
    end_type = my_types[1]
    if feat_name == 'REST' or feat_name == 'FIRST':
      my_p.append(feat_name)
      return my_p
    elif not open_list > 0:
      part_of_list = True
  stop = 0
  while True:
    my_p.append(feat_name)
    stop += 1
    if stop > 50:
      print my_p
      print feat_name, end_type, feat_n.get(feat_name)
      print 'BREAKING BECAUSE OF INFINITE LOOP'
      break
    val = feat_n.get(feat_name)
    if not val:
      print feat_name + ' is not defined in feature geometry'
      break
    else:
      loc = val[0]
        #HACK, SHOULD DO THIS ON LEVEL OF FEATURE GEOM EXTRACTION
        #should be fixed: TODO test if works without HACK
      if '+' in loc:
        loc = 'verb|+nvjrp|head|head-min|avm|'
  ##if point in established path is reached, we're done
    if end_type in loc or 'sign' in loc:
      break
    if 'sign' in end_type and 'word-or-lexrule' in loc:
      break
    if last_types_match(end_type, loc):
      break
    f_names = index_types.get(loc)
    #should only happen if feature must be part of a list (i.e. not introduced
    #by anything)
    if not f_names:
      break
 ##if neither of the above applies, but there is more than one possibility:
 ##the path is ambiguous
    if len(my_types) > 0:
      if my_types[0] in loc or last_types_match(my_types[0], loc):
        break
    if ',' in f_names:
      if not last_types_match(end_type, loc):
        print "error: unambiguous abbreviation for path"
        print feat_name + ' is located at ' + loc + ', which can be introduced by:'
        fns = f_names.split(',')
        for fn in fns:
          print fn
        print 'The current end type is: ' + end_type
        break
      else:
        break
    else:
      feat_name = f_names
  if part_of_list and not 'LIST' in my_p and not 'FIRST' in my_p and not 'LAST' in my_p:
    my_p.append('FIRST')
  return my_p


def last_types_match(end_type, loc):
  loc = loc.rstrip('|')
  end_type = end_type.rstrip('|')
  last_t1 = end_type.split('|')[-1]
  if last_t1 == 'avm':
    last_t1 = end_type.split('|')[-2]
  last_t2 = loc.split('|')[-1]
  if last_t2 == 'avm':
    last_t2 = loc.split('|')[-2]
   
  if last_t1 and last_t2:
    if last_t1 == last_t2:
      return True
  
  return False