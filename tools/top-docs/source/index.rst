Welcome to statsmodel's project page
====================================

scikits.statsmodels is a pure python package that provides classes and 
functions for the estimation of several categories of statistical models. These 
currently include linear regression models, OLS, GLS, WLS and GLS with AR(p) 
errors, generalized linear models for six distribution families and 
M-estimators for robust linear models. An extensive list of result statistics 
are avalable for each estimation problem

Documentation
-------------


Nightly build of current development (v0.3-devel): `HTML <http://statsmodels.sourceforge.net/devel/>`__ and PDF


Nightly build of trunk (v0.3): `HTML <http://statsmodels.sourceforge.net/trunk/>`__ and PDF


Previous stable release (v0.2.0): `HTML <http://statsmodels.sourceforge.net/released/>`__ and PDF

Quickstart for the impatient
----------------------------

**License:** Simplified BSD

**Requirements:** python 2.5. to 2.7 (there are only a few 2.4 incompatibilities) and 
  recent releases of numpy (>=1.3) and scipy (>=0.7) 
  earlier versions of numpy and scipy might work but not tested
  Optional: Many of the examples use matplotlib, and some sandbox functions
  have additional dependencies 

**Repository:** http://code.launchpad.net/statsmodels

**Pypi:** http://pypi.python.org/pypi/scikits.statsmodels

**Mailing List:** http://groups.google.com/group/pystatsmodels?hl=en

**Bug Tracker:**  https://bugs.launchpad.net/statsmodels

**Development:** See our `developer's page <http://statsmodels.sourceforge.net/trunk/developernotes.html>`__.

**Installation:**

::

  easy_install scikits.statsmodels

or get the source from pypi, sourceforge, or from the launchpad repository and

::

  setup.py install  or, if this does not work, try
  setup.py build install

**Note:**
Due to our infrequent official releases, we want to point out that the trunk
branch in the launchpad repository will have the most recent code and is 
usually stable, tested, and fine for daily use.

**Usage:**

Get the data, run the estimation, and look at the results. 
For example, here is a minimal ordinary least squares case ::

  import numpy as np
  import scikits.statsmodels as sm
  
  # get data
  nsample = 100
  x = np.linspace(0,10, 100)
  X = sm.add_constant(np.column_stack((x, x**2)))
  beta = np.array([1, 0.1, 10])
  y = np.dot(X, beta) + np.random.normal(size=nsample)
  
  # run the regression
  results = sm.OLS(y, X).fit()
  
  # look at the results
  print results.summary()
  
  and look at `dir(results)` to see some of the results
  that are available
