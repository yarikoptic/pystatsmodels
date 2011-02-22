This branch is only intended for use by developers.  It only contains files 
needed to build the main entry page for statsmodels.

How to update the main entry page
---------------------------------

If you want to update the main docs page, then from this directory run the 
following (with your credentials)

make clean
make html
rsync -avPr -e ssh build/html/* jseabold,statsmodels@web.sourceforge.net:htdocs/

How to update the nightly builds
--------------------------------
Note that this is done automatically with the update_web.py script except for
new releases.  They must be done by hand.  See below "How to add a release" for
instructions.

Important: Make sure you have the version installed for which you are building 
the documentation.

To update devel branch (from devel branch)

Make sure you have devel installed
cd to docs directory
make clean
make html

rsync -avPr -e ssh build/html/* jseabold,statsmodels@web.sourceforge.net:htdocs/devel

To update trunk (from trunk branch)

Make sure you have trunk installed
cd to docs directory
make clean
make html

rsync -avPr -e ssh build/html/* jseabold,statsmodels@web.sourceforge.net:htdocs/trunk


How to add a release
--------------------
For new releases you will need to create a new directory on the sourceforge 
site.  This can be done on linux as follows

sftp jseabold,statsmodels@web.sourceforge.net
<enter password>

mkdir 0.2release
bye

Then make sure you have the release installed, cd to the docs directory and run

make clean
make html

rsync -avPr -e ssh build/html/* jseabold,statsmodels@web.sourceforge.net:htdocs/0.2release
