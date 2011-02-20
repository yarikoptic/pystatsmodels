#!/usr/bin/env python
"""
This script installs the trunk version, builds the docs, then uploads them
to ...

Then it installs the devel version, builds the docs, and uploads them to
...

Depends
-------
virtualenv
"""
import base64
import subprocess
import os
import shutil
import re
import smtplib
from email.MIMEText import MIMEText

######### INITIAL SETUP ##########

# hard-coded branches
stable_trunk = 'statsmodels'
devel = 'statsmodels/0.3-devel'
last_release = 'statsmodels/releases'
branches = {'trunk' : stable_trunk, 'devel' : devel, 'released' : last_release}

# virtual environment directory
virtual_dir = 'BUILDENV'
virtual_dir = os.path.abspath(virtual_dir)

# my security holes
with open('/home/skipper/statsmodels/sforge.txt') as f:
    pwd = f.readline().strip()
sourceforge_pwd = base64.b64decode(pwd)
with open('/home/skipper/statsmodels/gmail.txt') as f:
    pwd = f.readline().strip()
gmail_pwd = base64.b64decode(pwd)

# make a virtualenv for installation if it doesn't exist
# and easy_install sphinx
if not os.path.exists(virtual_dir):
    retcode = subprocess.call(['virtualenv', virtual_dir])
    if retcode != 0:
        msg = """There was a problem creating the virtualenv"""
        raise Exception(msg)
    retcode = subprocess.call([virtual_dir+'/bin/easy_install', 'sphinx'])
    if retcode != 0:
        msg = """There was a problem installing sphinx"""
        raise Exception(msg)

# this points to the newly installed python in the virtualenv
virtual_python = os.path.join(virtual_dir,'bin','python')


########### EMAIL #############
email_name ='statsmodels.dev' + 'AT' + 'gmail.com'
email_name = email_name.replace('AT','@')
gmail_pwd= gmail_pwd


########### FUNCTIONS ###############

def getdirs():
    """
    Get current directories in order to restore to this
    """
    dirs = [i for i in os.listdir('./') if not os.path.isfile(i)]
    return dirs

def newdir(dirs):
    """
    Returns difference in directories between dirs and current directories

    If the difference is greater than one directory it raises an error.
    """
    dirs = set(dirs)
    newdirs = set([i for i in os.listdir('./') if not os.path.isfile(i)])
    newdir = newdirs.difference(dirs)
    if len(newdir) != 1:
        msg = """There was more than one directory created.  Don't know what to delete."""
        raise Exception(msg)
    newdir = newdir.pop()
    return newdir

def get_branch(branch_name):
    """
    Branches branch_name from launchpad.

    Returns the name of the new branch directory.
    """
    dirs = getdirs()
    retcode = subprocess.call(["bzr", "branch", "lp:"+branch_name])
    if retcode != 0:
        msg = """Could not create branch %s.""" % branch_name
        raise Exception(msg)
    nd = newdir(dirs)
    return nd


def install_branch(branch_dir):
    """
    Installs the new branch in a virtualenv.
    """
    old_cwd = os.getcwd()

    # if it's already in the virtualenv, remove it
    sitepack = os.path.join(virtual_dir,'lib','python2.6', 'site-packages')
    dir_list = os.listdir(sitepack)
    for f in dir_list:
        if 'scikits.statsmodels' in f:
            shutil.rmtree(os.path.join(sitepack, f))

    os.chdir(branch_dir)
    retcode = subprocess.call([virtual_python, 'setup.py','build'])
    if retcode != 0:
        os.chdir(old_cwd)
        msg = """Could not build branch %s""" % branch_dir
        raise Exception(msg)
    retcode = subprocess.call([virtual_python, 'setup.py', 'install'])
    if retcode != 0:
        os.chdir(old_cwd)
        msg = """Could not install branch %s""" % branch_dir
        raise Exception(msg)
    os.chdir(old_cwd)

def build_docs(new_branch_dir): 
    """
    Changes into new_branch_dir and builds the docs using sphinx in the 
    BUILDENV virtualenv
    """
    old_cwd = os.getcwd()
    os.chdir(os.path.join(new_branch_dir,'scikits','statsmodels','docs'))
    sphinx_dir = os.path.join(virtual_dir,'bin')
#NOTE: don't use make.py, just use make and specify which sphinx
#    retcode = subprocess.call([virtual_python,'make.py','html',
#        '--sphinx_dir='+sphinx_dir])
    retcode = subprocess.call(['make','html',
        'SPHINXBUILD='+sphinx_dir+'/sphinx-build'])
    if retcode != 0:
        os.chdir(old_cwd)
        msg = """Could not build the html docs for branch %s""" % new_branch_dir
        raise Exception(msg)
    os.chdir(old_cwd)

def upload_docs(branch, new_branch_dir):
    old_cwd = os.getcwd()
    os.chdir(os.path.join(new_branch_dir,'scikits','statsmodels','docs'))
    retcode = subprocess.call(['rsync', '-avPr' ,'-e ssh', 'build/html/', 
        'jseabold,statsmodels@web.sourceforge.net:htdocs/'+branch])
    if retcode != 0:
        os.chdir(old_cwd)
        msg = """Could not upload to %s for branch %s""" % (branch,
                new_branch_dir)
        raise Exception(msg)
    os.chdir(old_cwd)

def email_me(status='ok'):
    if status == 'ok':
        message = """
HTML Documentation uploaded successfully.
"""
        subject = "Statsmodels HTML Build OK"
    else:
        message = status
        subject = "Statsmodels HTML Build Failed"

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = email_name
    msg['To'] = email_name
    
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(email_name, gmail_pwd)
    server.sendmail(email_name, email_name, msg.as_string())
    server.close()


############### MAIN ###################

# get branch, install in virtualenv, build the docs, upload, and cleanup
msg = 'ok'
for branch in branches:
    try:
        # get directories to restore after done 
        dirs = getdirs()

        new_branch_dir = get_branch(branches[branch])
        install_branch(new_branch_dir)
        build_docs(new_branch_dir)
        upload_docs(branch, new_branch_dir)

        #TODO: should this just go into the branch and update it instead of 
        #downloading the whole thing each time?
        # cleanup
        newdirectory = newdir(dirs) 
    except Exception as status:
        msg = status.args[0]
        email_me(msg)
    shutil.rmtree(newdirectory)

if msg == 'ok': # if it doesn't something went wrong and was caught above
    email_me()
    




