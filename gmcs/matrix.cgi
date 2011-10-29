#!/usr/local/bin/python2.5

### $Id: matrix.cgi,v 1.27 2008-09-09 08:37:52 sfd Exp $

######################################################################
# imports

import sys
import os
import glob
import shutil
import cgi
import cgitb; cgitb.enable()
import time
import glob
from random import randint
from distutils.dir_util import remove_tree

from gmcs.deffile import MatrixDefFile
from gmcs.customize import customize_matrix
from gmcs.validate import validate_choices
from gmcs.choices import ChoicesFile

from gmcs.deffile import HTTP_header


######################################################################
# beginning of main program

# Uncomment this to see the output from print in the HTML page
# print HTTP_header + '\n\n'

matrixdef = MatrixDefFile('matrixdef')

form_data = cgi.FieldStorage()

# see if we are in debug mode
debug = 'debug' in form_data and form_data['debug'].value in ('true','True')

# Get the cookie.  If there's not one, make one.
http_cookie = os.getenv('HTTP_COOKIE')
browser_cookie = False
cookie = ''
if http_cookie:
  for c in http_cookie.split(';'):
    (name, value) = c.split('=', 1)
    if name == 'session' and len(value) == 4 and value.isdigit():
      browser_cookie = True
      cookie = value
      break

if not cookie:
  cookie = str(randint(1000,9999))
  while os.path.exists('sessions/' + cookie):
    cookie = str(randint(1000,9999))

# make the sessions directory if necessary
if not os.path.exists('sessions'):
  os.mkdir('sessions')

# look for any sessions older than 24 hours and delete them
now = time.time()
sessions = glob.glob('sessions/*')
for s in sessions:
  if now - os.path.getmtime(s) > 86400:
    remove_tree(s)

# figure out the path to the current session's directory, creating it
# if necessary
session_path = 'sessions/' + cookie
if cookie and not os.path.exists(session_path):
  os.mkdir(session_path)
  # create a blank choices file
  open(os.path.join(session_path, 'choices'), 'w').close()

# if the 'choices' field is defined, we have either the contents of an
# uploaded choices file or the name of a sample choices file (which
# will begin with 'sample-choices/') to replace the current choices.
if form_data.has_key('choices'):
  choices = form_data['choices'].value
  if choices:
    if choices[:15] == 'sample-choices/':
      f = open(choices, 'r')
      data = f.read()
      f.close()
    else:
      data = choices
    f = open(os.path.join(session_path, 'choices'), 'w')
    f.write(data)
    f.close()

# if the 'section' field is defined, we have submitted values to save
if form_data.has_key('section'):
  matrixdef.save_choices(form_data, os.path.join(session_path, 'choices'))

# If the 'verbpred' field is defined, then the user wishes to generate more sentences with that predication
if form_data.has_key('verbpred'):
  matrixdef.more_sentences_page(session_path,form_data['grammar'].value, form_data['verbpred'].value, form_data['template'].value, cookie)
  sys.exit()

# Get a list of error messages, determined by validating the current
# choices.  If the current choices are valid, the list will be empty.
try:
  vr = validate_choices(os.path.join(session_path, 'choices'))
except:
  exc = sys.exc_info()
  matrixdef.choices_error_page(os.path.join(session_path, 'choices'), exc)
  sys.exit()

# if the 'customize' field is defined, create a customized copy of the matrix
# based on the current choices file
if form_data.has_key('customize'):
  # ERB 2006-10-03 Checking has_key here to enable local debugging.
  if form_data.has_key('delivery'):
    arch_type = form_data['delivery'].value
  else:
    arch_type = ''
  if arch_type != 'tgz' and arch_type != 'zip':
    vr.err('delivery', 'You must specify an archive type.')

  if vr.has_errors():
    matrixdef.error_page(vr)
  else:
    # If the user said it's OK, archive the choices file
    choices = ChoicesFile(os.path.join(session_path, 'choices'))
    if choices.get('archive') == 'yes':
      # create the saved-choices directory
      if not os.path.exists('saved-choices'):
        os.mkdir('saved-choices')

      # look at the files in saved-choices, which will have names like
      # choices.N, figure out the next serial number, and copy the current
      # choices file to saved-choices/choices.N+1
      serial = 1
      for f in glob.glob('saved-choices/choices.*'):
        i = f.rfind('.')
        if i != -1:
          num = f[i + 1:]
          if num.isdigit():
            serial = max(serial, int(num) + 1)
      shutil.copy(os.path.join(session_path, 'choices'),
                  'saved-choices/choices.' + str(serial))

    # Create the customized grammar
    try:
      grammar_dir = customize_matrix(session_path, arch_type)
    except:
      exc = sys.exc_info()
      matrixdef.customize_error_page(os.path.join(session_path, 'choices'),
                                     exc)
      sys.exit()

    if form_data.has_key('sentences'):
      matrixdef.sentences_page(session_path, grammar_dir, cookie)
    else:
      matrixdef.custom_page(session_path, grammar_dir, arch_type)
elif form_data.has_key('subpage'):
  if browser_cookie:
    matrixdef.sub_page(form_data['subpage'].value, cookie, vr)
  else:
    matrixdef.cookie_error_page()
else:
   matrixdef.main_page(cookie, vr)