"""
Vector Autoregression (VAR) processes

References
----------
Lutkepohl (2005) New Introduction to Multiple Time Series Analysis
"""

from __future__ import division

from cStringIO import StringIO

import numpy as np
import numpy.linalg as npl
from numpy.linalg import cholesky as chol, solve
import scipy.stats as stats
import scipy.linalg as L

import matplotlib as mpl

from scikits.statsmodels.decorators import cache_readonly
from scikits.statsmodels.tools.tools import chain_dot
from scikits.statsmodels.tsa.tsatools import vec, unvec

import scikits.statsmodels.tsa.tsatools as tsa
import scikits.statsmodels.tsa.var.output as output
import scikits.statsmodels.tsa.var.plotting as plotting
import scikits.statsmodels.tsa.var.util as util

mat = np.array

try:
    import pandas.util.testing as test
    import IPython.core.debugger as _
    st = test.set_trace
except ImportError:
    import pdb
    st = pdb.set_trace

class MPLConfigurator(object):

    def __init__(self):
        self._inverse_actions = []

    def revert(self):
        for action in self._inverse_actions:
            action()

    def set_fontsize(self, size):
        old_size = mpl.rcParams['font.size']
        mpl.rcParams['font.size'] = size

        def revert():
            mpl.rcParams['font.size'] = old_size

        self._inverse_actions.append(revert)

#-------------------------------------------------------------------------------
# VAR process routines

def varsim(coefs, intercept, sig_u, steps=100, initvalues=None):
    """
    Simulate simple VAR(p) process with known coefficients, intercept, white
    noise covariance, etc.
    """
    from numpy.random import multivariate_normal as rmvnorm
    p, k, k = coefs.shape
    ugen = rmvnorm(np.zeros(len(sig_u)), sig_u, steps)
    result = np.zeros((steps, k))
    result[p:] = intercept + ugen[p:]

    # add in AR terms
    for t in xrange(p, steps):
        ygen = result[t]
        for j in xrange(p):
            ygen += np.dot(coefs[j], result[t-j-1])

    return result

def ma_rep(coefs, intercept, maxn=10):
    """
    MA(\infty) representation of VAR(p) process

    Parameters
    ----------
    coefs : ndarray (p x k x k)
    intercept : ndarry length-k
    maxn : int
        Number of MA matrices to compute

    Notes
    -----
    VAR(p) process as

    .. math:: y_t = A_1 y_{t-1} + \ldots + A_p y_{t-p} + u_t

    can be equivalently represented as

    .. math:: y_t = \mu + \sum_{i=0}^\infty \Phi_i u_{t-i}

    e.g. can recursively compute the \Phi_i matrices with \Phi_0 = I_k

    Returns
    -------
    """
    p, k, k = coefs.shape
    phis = np.zeros((maxn+1, k, k))
    phis[0] = np.eye(k)

    # recursively compute Phi matrices
    for i in xrange(1, maxn + 1):
        phi = phis[i]
        for j in xrange(1, i+1):
            if j > p:
                break

            phi += np.dot(phis[i-j], coefs[j-1])

    return phis

def is_stable(coefs, verbose=False):
    """
    Determine stability of VAR(p) system by examining the eigenvalues of the
    VAR(1) representation

    Parameters
    ----------
    coefs : ndarray (p x k x k)

    Returns
    -------
    is_stable : bool
    """
    A_var1 = util.comp_matrix(coefs)
    eigs = np.linalg.eigvals(A_var1)

    if verbose:
        print 'Eigenvalues of VAR(1) rep'
        for val in np.abs(eigs):
            print val

    return (np.abs(eigs) <= 1).all()

def var_acf(coefs, sig_u, nlags=None):
    """
    Compute autocovariance function ACF_y(h) up to nlags of stable VAR(p)
    process

    Parameters
    ----------
    coefs : ndarray (p x k x k)
        Coefficient matrices A_i
    sig_u : ndarray (k x k)
        Covariance of white noise process u_t
    nlags : int, optional
        Defaults to order p of system

    Notes
    -----
    Ref: Lutkepohl p.28-29

    Returns
    -------
    acf : ndarray, (p, k, k)
    """
    p, k, k2 = coefs.shape
    if nlags is None:
        nlags = p

    # p x k x k, ACF for lags 0, ..., p-1
    result = np.zeros((nlags + 1, k, k))
    result[:p] = _var_acf(coefs, sig_u)

    # yule-walker equations
    for h in xrange(p, nlags + 1):
        # compute ACF for lag=h
        # G(h) = A_1 G(h-1) + ... + A_p G(h-p)

        res = result[h]
        for j in xrange(p):
            res += np.dot(coefs[j], result[h-j-1])

    return result

def _var_acf(coefs, sig_u):
    """
    Compute autocovariance function ACF_y(h) for h=1,...,p

    Notes
    -----
    Lutkepohl (2005) p.29
    """
    p, k, k2 = coefs.shape
    assert(k == k2)

    A = util.comp_matrix(coefs)
    # construct VAR(1) noise covariance
    SigU = np.zeros((k*p, k*p))
    SigU[:k,:k] = sig_u

    # vec(ACF) = (I_(kp)^2 - kron(A, A))^-1 vec(Sigma_U)
    vecACF = L.solve(np.eye((k*p)**2) - np.kron(A, A), vec(SigU))

    acf = unvec(vecACF)
    acf = acf[:k].T.reshape((p, k, k))

    return acf

def forecast(y, coefs, intercept, steps):
    """
    Produce linear MSE forecast

    Parameters
    ----------


    Notes
    -----
    Lutkepohl p. 37
    """
    p = len(coefs)
    k = len(coefs[0])
    # initial value
    forcs = np.zeros((steps, k)) + intercept

    # h=0 forecast should be latest observation
    # forcs[0] = y[-1]

    # make indices easier to think about
    for h in xrange(1, steps + 1):
        f = forcs[h - 1]

        # y_t(h) = intercept + sum_1^p A_i y_t_(h-i)

        for i in xrange(1, p + 1):
            # slightly hackish
            if h - i <= 0:
                # e.g. when h=1, h-1 = 0, which is y[-1]
                prior_y = y[h - i - 1]
            else:
                # e.g. when h=2, h-1=1, which is forcs[0]
                prior_y = forcs[h - i - 1]

            # i=1 is coefs[0]
            f += np.dot(coefs[i - 1], prior_y)

    return forcs

def forecast_cov(ma_coefs, sig_u, steps):
    """
    Compute forecast error variance matrices
    """
    k = len(sig_u)
    forc_covs = np.zeros((steps, k, k))

    prior = np.zeros((k, k))
    for h in xrange(steps):
        # Sigma(h) = Sigma(h-1) + Phi Sig_u Phi'
        phi = ma_coefs[h]
        var = chain_dot(phi, sig_u, phi.T)
        forc_covs[h] = prior = prior + var

    return forc_covs

def granger_causes(coefs):
    pass

#-------------------------------------------------------------------------------
# VARProcess class: for known or unknown VAR process

def lag_select():
    pass

import unittest
class TestVAR(unittest.TestCase):
    pass

class VAR(object):
    """
    Fit VAR(p) process and do lag order selection

    .. math:: y_t = A_1 y_{t-1} + \ldots + A_p y_{t-p} + u_t

    Notes
    -----
    **References**
    Lutkepohl (2005) New Introduction to Multiple Time Series Analysis

    Returns
    -------
    .fit() method returns VAREstimator object
    """

    def __init__(self, endog, names=None, dates=None):
        self.y, self.names = util.interpret_data(endog, names)
        self.nobs, self.neqs = self.y.shape

        if dates is not None:
            assert(self.nobs == len(dates))
        self.dates = dates

    def loglike(self, params, omega):
        pass

    def fit(self, maxlags=None, method='ols', ic=None, verbose=False):
        """
        Fit the VAR model

        Parameters
        ----------
        maxlags : int
            Maximum number of lags to check for order selection, defaults to
            12 * (nobs/100.)**(1./4), see select_order function
        method : {'ols'}
            Estimation method to use
        ic : {'aic', 'fpe', 'hq', 'sic', None}
            Information criterion to use for VAR order selection.
            aic : Akaike
            fpe : Final prediction error
            hq : Hannan-Quinn
            sic : Schwarz
        verbose : bool, default False
            Print order selection output to the screen

        Notes
        -----
        Lutkepohl pp. 146-153

        Returns
        -------
        est : VAREstimator
        """
        lags = maxlags

        if ic is not None:
            selections = self.select_order(maxlags=maxlags, verbose=verbose)
            if ic not in selections:
                raise Exception("%s not recognized, must be among %s"
                                % (ic, sorted(selections)))
            lags = selections[ic]
            if verbose:
                print 'Using %d based on %s criterion' %  (lags, ic)

        return VAREstimator(self.y, p=lags, names=self.names, dates=self.dates)

    def select_order(self, maxlags=None, verbose=True):
        """

        Parameters
        ----------

        Returns
        -------
        """
        from collections import defaultdict

        if maxlags is None:
            maxlags = int(round(12*(self.nobs/100.)**(1/4.)))

        ics = defaultdict(list)
        for p in range(maxlags + 1):
            est = VAREstimator(self.y, p=p)
            for k, v in est.info_criteria.iteritems():
                ics[k].append(v)

        selected_orders = dict((k, mat(v).argmin())
                               for k, v in ics.iteritems())

        if verbose:
            output.print_ic_table(ics, selected_orders)

        return selected_orders

class VARProcess(object):
    """

    Parameters
    ----------

    Returns
    -------

    **Attributes**:

    """
    def __init__(self):
        pass

    def get_eq_index(self, name):
        try:
            result = self.names.index(name)
        except Exception:
            if not isinstance(name, int):
                raise
            result = name

        return result

    def __str__(self):
        output = ('VAR(%d) process for %d-dimensional response y_t'
                  % (self.p, self.neqs))
        output += '\nstable: %s' % self.is_stable()
        output += '\nmean: %s' % self.mean()

        return output

    def is_stable(self, verbose=False):
        """
        Determine stability based on model coefficients

        Parameters
        ----------
        verbose : bool
            Print eigenvalues of VAR(1) rep matrix

        Notes
        -----

        """
        return is_stable(self.coefs, verbose=verbose)

    def plotsim(self, steps=1000):
        Y = varsim(self.coefs, self.intercept, self.sigma_u, steps=steps)
        plotting.plot_mts(Y)

    def plotforc(self, y, steps, alpha=0.05):
        """

        """
        mid, lower, upper = self.forecast_interval(y, steps, alpha=alpha)
        plotting.plot_var_forc(y, mid, lower, upper,
                          index=self.dates,
                          names=self.names)

    def mean(self):
        """
        Mean of stable process

        .. math:: \mu = (I - A_1 - \dots - A_p)^{-1} \alpha
        """
        return solve(self._char_mat, self.intercept)

    def ma_rep(self, maxn=10):
        """
        Compute MA(\infty) coefficient matrices (also are impulse response
        matrices))

        Parameters
        ----------
        maxn : int
            Number of coefficient matrices to compute

        Returns
        -------
        coefs : ndarray (maxn x k x k)
        """
        return ma_rep(self.coefs, self.intercept, maxn=maxn)

    def orth_ma_rep(self, maxn=10, P=None):
        """
        Compute Orthogonalized MA coefficient matrices using P matrix such that
        \Sigma_u = PP'. P defaults to the Cholesky decomposition of \Sigma_u

        Parameters
        ----------
        maxn : int
            Number of coefficient matrices to compute
        P : ndarray (k x k), optional
            Matrix such that Sigma_u = PP', defaults to Cholesky descomp

        Returns
        -------
        coefs : ndarray (maxn x k x k)
        """
        if P is None:
            P = self._chol_sigma_u

        ma_mats = self.ma_rep(maxn=maxn)
        return mat([np.dot(coefs, P) for coefs in ma_mats])

    def long_run_effects(self):
        return L.inv(self._char_mat)

    @cache_readonly
    def _chol_sigma_u(self):
        return chol(self.sigma_u)

    @cache_readonly
    def _char_mat(self):
        return np.eye(self.neqs) - self.coefs.sum(0)

    def acf(self, nlags=None):
        return var_acf(self.coefs, self.sigma_u, nlags=nlags)

    def acorr(self, nlags=None):
        return util._acf_to_acorr(var_acf(self.coefs, self.sigma_u,
                                          nlags=nlags))

    def plot_acorr(self, nlags=10, linewidth=8):
        plotting.plot_acorr(self.acorr(nlags=nlags), linewidth=linewidth)

    def forecast(self, y, steps):
        """
        Produce linear minimum MSE forecasts for desired number of steps ahead,
        using prior values y

        Parameters
        ----------
        y : ndarray (p x k)
        steps : int

        Returns
        -------

        Notes
        -----
        Lutkepohl pp 37-38
        """
        return forecast(y, self.coefs, self.intercept, steps)

    def forecast_cov(self, steps):
        """
        Compute forecast error covariance matrices

        Parameters
        ----------


        Returns
        -------
        covs : (steps, k, k)
        """
        return self.mse(steps)

    def mse(self, steps):
        return forecast_cov(self.ma_rep(steps), self.sigma_u, steps)

    def _forecast_vars(self, steps):
        covs = self.forecast_cov(steps)

        # Take diagonal for each cov
        inds = np.arange(self.neqs)
        return covs[:, inds, inds]

    def forecast_interval(self, y, steps, alpha=0.05):
        """
        Construct forecast interval estimates assuming the y are Gaussian

        Parameters
        ----------

        Notes
        -----
        Lutkepohl pp. 39-40

        Returns
        -------
        (lower, mid, upper) : (ndarray, ndarray, ndarray)
        """
        assert(0 < alpha < 1)
        q = util.norm_signif_level(alpha)

        point_forecast = self.forecast(y, steps)
        sigma = np.sqrt(self._forecast_vars(steps))

        forc_lower = point_forecast - q * sigma
        forc_upper = point_forecast + q * sigma

        return point_forecast, forc_lower, forc_upper

    def forecast_dyn(self):
        """
        "Forward filter": compute forecasts for each time step
        """

        pass

    def irf(self, nperiods=50):
        """
        Compute impulse responses to shocks in system
        """
        pass

    def fevd(self):
        """
        Compute forecast error variance decomposition ("fevd")
        """
        pass


#-------------------------------------------------------------------------------
# Known VAR process and Estimator classes

class KnownVARProcess(VARProcess):
    """
    Class for analyzing VAR(p) process with known coefficient matrices and white
    noise covariance matrix

    Parameters
    ----------

    """
    def __init__(self, intercept, coefs, sigma_u):
        self.p = len(coefs)
        self.neqs = len(coefs[0])

        self.intercept = intercept
        self.coefs = coefs

        self.sigma_u = sigma_u

class VAREstimator(VARProcess):
    """
    Estimate VAR(p) process with fixed number of lags

    Returns
    -------
    **Attributes**
    k : int
        Number of variables (equations)
    p : int
        Order of VAR process
    T : Number of model observations (len(data) - p)
    y : ndarray (K x T)
        Observed data
    names : ndarray (K)
        variables names

    df_model : int
    df_resid : int

    coefs : ndarray (p x K x K)
        Estimated A_i matrices, A_i = coefs[i-1]
    intercept : ndarray (K)
    params : ndarray (Kp + 1) x K
        A_i matrices and intercept in stacked form [int A_1 ... A_p]

    sigma_u : ndarray (K x K)
        Estimate of white noise process variance Var[u_t]
    """
    _model_type = 'VAR'

    def __init__(self, data, p=1, names=None, dates=None):
        self.p = p
        self.y, self.names = util.interpret_data(data, names)
        self.nobs, self.neqs = self.y.shape

        # TODO: fix this to be something real
        self.trendorder = 1

        # This will be the dimension of the Z matrix
        self.T = self.nobs  - self.p

        self.dates = dates

        if dates is not None:
            assert(self.nobs == len(dates))

        self.names = names
        self.dates = dates

    def data_summary(self):
        pass

    def plot(self):
        plotting.plot_mts(self.y, names=self.names, index=self.dates)

    @property
    def df_model(self):
        """
        Number of estimated parameters, including the intercept / trends
        """
        return self.neqs * self.p + self.trendorder

    @property
    def df_resid(self):
        return self.T - self.df_model

    def __str__(self):
        output = ('VAR(%d) process for %d-dimensional response y_t'
                  % (self.p, self.neqs))
        output += '\nstable: %s' % self.is_stable()
        output += '\nmean: %s' % self.mean()

        return output

    def forecast_dyn(self):
        """
        "Forward filter": compute forecasts for each time step
        """

        pass

    def loglike(self, params, omega):
        r"""
        Returns the value of the VAR(p) log-likelihood.

        Parameters
        ----------
        params : array-like
            The parameter estimates
        omega : ndarray
            Sigma hat matrix.  Each element i,j is the average product of the
            OLS residual for variable i and the OLS residual for variable j or
            np.dot(resid.T,resid)/avobs.  There should be no correction for the
            degrees of freedom.


        Returns
        -------
        loglike : float
            The value of the loglikelihood function for a VAR(p) model

        Notes
        -----
        The loglikelihood function for the VAR(p) is

        .. math::

            -\left(\frac{T}{2}\right)
            \left(\ln\left|\Omega\right|-K\ln\left(2\pi\right)-K\right)
        """
        params = np.asarray(params)
        omega = np.asarray(omega)
        logdet = np_slogdet(omega)
        if logdet[0] == -1:
            raise ValueError("Omega matrix is not positive definite")
        elif logdet[0] == 0:
            raise ValueError("Omega matrix is singluar")
        else:
            logdet = logdet[1]
        avobs = self.avobs
        neqs = self.neqs
        return -(avobs/2.)*(neqs*np.log(2*np.pi)+logdet+neqs)

#-------------------------------------------------------------------------------
# VARProcess interface

    @cache_readonly
    def coefs(self):
        # Each matrix needs to be transposed
        reshaped = self.params[1:].reshape((self.p, self.neqs, self.neqs))

        # Need to transpose each coefficient matrix
        return reshaped.swapaxes(1, 2).copy()

    @property
    def intercept(self):
        return self.params[0]

    @cache_readonly
    def params(self):
        return self._est_params()

    @cache_readonly
    def sigma_u(self):
        return self._est_sigma_u()

    @cache_readonly
    def sigma_u_mle(self):
        return self.sigma_u * self.df_resid / self.T

    @cache_readonly
    def resid(self):
        # Lutkepohl p75, this is slower
        # middle = np.eye(self.T) - chain_dot(z, self._zzinv, z.T)
        # return chain_dot(y.T, middle, y) / self.df_resid

        # about 5x faster
        return self._y_sample - np.dot(self.Z, self.params)

#-------------------------------------------------------------------------------
# Auxiliary variables for estimation

    @cache_readonly
    def Z(self):
        """
        Predictor matrix for VAR(p) process

        Z := (Z_0, ..., Z_T).T (T x Kp)
        Z_t = [1 y_t y_{t-1} ... y_{t - p + 1}] (Kp x 1)

        Ref: Lutkepohl p.70 (transposed)
        """
        y = self.y
        p = self.p

        # Ravel C order, need to put in descending order
        Z = mat([y[t-p : t][::-1].ravel() for t in xrange(p, self.nobs)])

        # Add intercept
        return np.concatenate((np.ones((self.T, 1)), Z), axis=1)

    @cache_readonly
    def _zz(self):
        return np.dot(self.Z.T, self.Z)

    @cache_readonly
    def _zzinv(self):
        try:
            zzinv = L.inv(self._zz)
        except np.linalg.LinAlgError:
            zzinv = L.pinv(self._zz)

        return zzinv

    @cache_readonly
    def _y_sample(self):
        # drop presample observations
        return self.y[self.p:]

    #------------------------------------------------------------
    # Coefficient estimation

    def _est_params(self):
        res = np.linalg.lstsq(self.Z, self._y_sample)
        # coefs = chain_dot(self._zzinv, self.Z.T, self._y_sample)
        return res[0]

    def _est_sigma_u(self):
        """
        Unbiased estimate of covariance matrix $\Sigma_u$ of the white noise
        process $u$

        equivalent definition

        .. math:: \frac{1}{T - Kp - 1} Y^\prime (I_T - Z (Z^\prime Z)^{-1}
        Z^\prime) Y

        Ref: Lutkepohl p.75
        """
        # df_resid right now is T - Kp - 1, which is a suggested correction
        return np.dot(self.resid.T, self.resid) / self.df_resid

    def _est_var_ybar(self):
        Ainv = L.inv(np.eye(self.neqs) - self.coefs.sum(0))
        return chain_dot(Ainv, self.sigma_u, Ainv.T)

    def _t_mean(self):
        self.mean() / np.sqrt(np.diag(self._est_var_ybar()))

    @property
    def _cov_alpha(self):
        """
        Estimated covariance matrix of model coefficients ex intercept
        """
        # drop intercept
        return self.cov_beta[self.neqs:, self.neqs:]

    @cache_readonly
    def _cov_sigma(self):
        """
        Estimated covariance matrix of vech(sigma_u)
        """
        D_K = tsa.duplication_matrix(self.neqs)
        D_Kinv = npl.pinv(D_K)

        sigxsig = np.kron(self.sigma_u, self.sigma_u)
        return 2 * chain_dot(D_Kinv, sigxsig, D_Kinv.T)

    @cache_readonly
    def cov_beta(self):
        """
        Covariance of vec(B), where B is the matrix

        [intercept, A_1, ..., A_p] (K x (Kp + 1))

        Notes
        -----
        Adjusted to be an unbiased estimator

        Ref: Lutkepohl p.74-75

        Returns
        -------
        cov_beta : ndarray (K^2p + K x K^2p + K) (# parameters)
        """
        return np.kron(L.inv(self._zz), self.sigma_u)

    @cache_readonly
    def stderr(self):
        """
        Standard errors of coefficients, reshaped to match in size
        """
        stderr = np.sqrt(np.diag(self.cov_beta))
        return stderr.reshape((self.df_model, self.neqs), order='C')

    bse = stderr  # statsmodels interface?

    def t(self):
        """
        Compute t-statistics. Use Student-t(T - Kp - 1) = t(df_resid) to test
        significance.
        """
        return self.params / self.stderr

    @cache_readonly
    def pvalues(self):
        return stats.t.sf(np.abs(self.t()), self.df_resid)*2

    def forecast_interval(self, steps, alpha=0.05):
        """
        Construct forecast interval estimates assuming the y are Gaussian

        Parameters
        ----------

        Notes
        -----
        Lutkepohl pp. 39-40

        Returns
        -------
        (lower, mid, upper) : (ndarray, ndarray, ndarray)
        """
        return VARProcess.forecast_interval(
            self, self.y[-self.p:], steps, alpha=alpha)

    def plotforc(self, steps, alpha=0.05):
        """

        """
        mid, lower, upper = self.forecast_interval(steps, alpha=alpha)
        plotting.plot_var_forc(self.y, mid, lower, upper, names=self.names)

    # Forecast error covariance functions

    def forecast_cov(self, steps=1):
        """
        Compute forecast covariance matrices for desired number of steps

        Parameters
        ----------
        steps : int

        Notes
        -----
        .. math:: \Sigma_{\hat y}(h) = \Sigma_y(h) + \Omega(h) / T

        Ref: Lutkepohl pp. 96-97

        Returns
        -------
        covs : ndarray (steps x k x k)
        """
        mse = self.mse(steps)
        omegas = self._omega_forc_cov(steps)
        return mse + omegas / self.T

    def _omega_forc_cov(self, steps):
        # Approximate MSE matrix \Omega(h) as defined in Lut p97
        G = self._zz
        Ginv = L.inv(G)

        # memoize powers of B for speedup
        # TODO: see if can memoize better
        B = self._bmat_forc_cov()
        _B = {}
        def bpow(i):
            if i not in _B:
                _B[i] = np.linalg.matrix_power(B, i)

            return _B[i]

        phis = self.ma_rep(steps)
        sig_u = self.sigma_u

        omegas = np.zeros((steps, self.neqs, self.neqs))
        for h in range(1, steps + 1):
            if h == 1:
                omegas[h-1] = self.df_model * self.sigma_u
                continue

            om = omegas[h-1]
            for i in range(h):
                for j in range(h):
                    Bi = bpow(h - 1 - i)
                    Bj = bpow(h - 1 - j)
                    mult = np.trace(chain_dot(Bi.T, Ginv, Bj, G))
                    om += mult * chain_dot(phis[i], sig_u, phis[j].T)

        return omegas

    def _bmat_forc_cov(self):
        # B as defined on p. 96 of Lut
        upper = np.zeros((1, self.df_model))
        upper[0,0] = 1

        lower_dim = self.neqs * (self.p - 1)
        I = np.eye(lower_dim)
        lower = np.column_stack((np.zeros((lower_dim, 1)), I,
                                 np.zeros((lower_dim, self.neqs))))

        return np.vstack((upper, self.params.T, lower))

    def summary(self):
        from scikits.statsmodels.tsa.var.output import VARSummary
        return VARSummary(self)

    def irf(self, periods=10, var_decomp=None):
        """
        Analyze impulse responses to shocks in system

        Parameters
        ----------
        periods : int
        var_decomp : ndarray (k x k), lower triangular
            Must satisfy Omega = P P', where P is the passed matrix. Defaults to
            Cholesky decomposition of Omega

        Returns
        -------

        """
        from scikits.statsmodels.tsa.var.irf import IRAnalysis
        return IRAnalysis(self, P=var_decomp, periods=periods)

    def fevd(self, periods=10, var_decomp=None):
        """
        Compute forecast error variance decomposition ("fevd")

        Returns
        -------
        fevd : FEVD instance
        """
        return FEVD(self, P=var_decomp, periods=periods)

#-------------------------------------------------------------------------------
# VAR Diagnostics: Granger-causality, whiteness of residuals, normality, etc.

    def test_causality(self, equation, variables, kind='f', signif=0.05,
                       verbose=True):
        """
        Compute test statistic for null hypothesis of Granger-noncausality,
        general function to test joint Granger-causality of multiple variables

        Parameters
        ----------
        equation : string or int
            Equation to test for causality
        variables : sequence (of strings or ints)
            List, tuple, etc. of variables to test for Granger-causality
        kind : {'f', 'wald'}
            Perform F-test or Wald (chi-sq) test
        signif : float, default 5%
            Significance level for computing critical values for test,
            defaulting to standard 0.95 level

        Notes
        -----
        Null hypothesis is that there is no Granger-causality for the indicated
        variables

        Returns
        -------
        results : dict
        """
        k, p = self.neqs, self.p

        # number of restrictions
        N = len(variables) * self.p

        # Make restriction matrix
        C = np.zeros((N, k ** 2 * self.p + k), dtype=float)

        eq_index = self.get_eq_index(equation)
        vinds = mat([self.get_eq_index(v) for v in variables])

        # remember, vec is column order!
        offsets = np.concatenate([k + k ** 2 * j + k * vinds + eq_index
                                  for j in range(p)])
        C[np.arange(N), offsets] = 1

        # Lutkepohl 3.6.5
        Cb = np.dot(C, vec(self.params.T))
        middle = L.inv(chain_dot(C, self.cov_beta, C.T))

        # wald statistic
        lam_wald = chain_dot(Cb, middle, Cb)

        if kind.lower() == 'wald':
            test_stat = lam_wald
            df = N
            dist = stats.chi2(df)
            pvalue = stats.chi2.sf(test_stat, N)
            crit_value = stats.chi2.ppf(1 - signif, N)
        elif kind.lower() == 'f':
            test_stat = lam_wald / N
            df = (N, self.df_resid)
            dist = stats.f(*df)
        else:
            raise Exception('kind %s not recognized' % kind)

        pvalue = dist.sf(test_stat)
        crit_value = dist.ppf(1 - signif)

        conclusion = 'fail to reject' if test_stat < crit_value else 'reject'
        results = {
            'test_stat' : test_stat,
            'crit_value' : crit_value,
            'pvalue' : pvalue,
            'df' : df,
            'conclusion' : conclusion,
            'signif' :  signif
        }

        if verbose:
            self._causality_summary(results, variables, equation, signif, kind)

        return results

    def test_whiteness(self):
        pass

    def test_normality(self):
        pass

    @cache_readonly
    def info_criteria(self):
        # information criteria for order selection
        nobs = self.T
        neqs = self.neqs
        lag_order = self.p
        free_params = lag_order * neqs ** 2 + neqs * self.trendorder

        ld = np.log(L.det(self.sigma_u_mle))

        st()

        aic = ld + (2. / nobs) * free_params
        bic = ld + (np.log(nobs) / nobs) * (lag_order * free_params)
        hqic = ld + 2. * np.log(np.log(nobs)) * lag_order * free_params / nobs
        fpe = ((nobs + self.df_model) / self.df_resid) ** neqs * ld

        return {
            'aic' : aic,
            'bic' : bic,
            'hq' : hqic,
            'sic' : bic,
            'fpe' : fpe
            }

    @property
    def aic(self):
        # Akaike information criterion
        return self.info_criteria['aic']

    @property
    def fpe(self):
        """
        Lutkepohl p. 147, see info_criteria
        """
        # Final Prediction Error (FPE)
        return self.info_criteria['fpe']

    @property
    def hqic(self):
        # Hannan-Quinn criterion
        return self.info_criteria['hqic']

    @property
    def bic(self):
        # Bayesian information criterion
        return self.info_criteria['bic']

    @property
    def sic(self):
        # Schwarz criterion a.k.a. Bayesian i.c.
        return self.info_criteria['sic']

class FEVD(object):
    """
    Compute and plot Forecast error variance decomposition and asymptotic
    standard errors
    """
    def __init__(self, model, P=None, periods=None):
        self.periods = periods

        self.model = model
        self.neqs = model.neqs
        self.names = model.names

        self.irfobj = model.irf(var_decomp=P, periods=periods)
        self.orth_irfs = self.irfobj.orth_irfs

        # cumulative impulse responses
        irfs = (self.orth_irfs[:periods] ** 2).cumsum(axis=0)

        rng = range(self.neqs)
        mse = self.model.mse(periods)[:, rng, rng]

        # lag x equation x component
        fevd = np.empty_like(irfs)

        for i in range(periods):
            fevd[i] = (irfs[i].T / mse[i]).T

        # switch to equation x lag x component
        self.decomp = fevd.swapaxes(0, 1)

    def summary(self):
        buf = StringIO()

        rng = range(self.periods)
        for i in range(self.neqs):
            ppm = output.pprint_matrix(self.decomp[i], rng, self.names)

            print >> buf, 'FEVD for %s' % self.names[i]
            print >> buf, ppm

        print buf.getvalue()

    def cov(self, lag):
        """
        Compute asymptotic standard errors

        Returns
        -------
        """
        pass

    def plot(self, periods=None, figsize=(10,10), **plot_kwds):
        """
        Plot graphical display of FEVD

        Parameters
        ----------
        periods : int, default None
            Defaults to number originally specified. Can be at most that number
        """
        import matplotlib.pyplot as plt

        k = self.neqs
        periods = periods or self.periods

        fig, axes = plt.subplots(nrows=k, figsize=(10,10))

        fig.suptitle('Forecast error variance decomposition (FEVD)')

        colors = [str(c) for c in np.arange(k, dtype=float) / k]
        ticks = np.arange(periods)

        limits = self.decomp.cumsum(2)

        for i in range(k):
            ax = axes[i]

            this_limits = limits[i].T

            handles = []

            for j in range(k):
                lower = this_limits[j - 1] if j > 0 else 0
                upper = this_limits[j]
                handle = ax.bar(ticks, upper - lower, bottom=lower,
                                color=colors[j], label=self.names[j],
                                **plot_kwds)

                handles.append(handle)

            ax.set_title(self.names[i])

        # just use the last axis to get handles for plotting
        handles, labels = ax.get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper right')
        plotting.adjust_subplots(right=0.85)

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    from scikits.statsmodels.tsa.var.alt import VAR2
    import scikits.statsmodels.api as sm

    """
    from scikits.statsmodels.tsa.var.util import parse_data

    path = 'scikits/statsmodels/tsa/var/data/%s.dat'
    sdata, dates = parse_data(path % 'e1')

    names = sdata.dtype.names
    data = util.struct_to_ndarray(sdata)

    adj_data = np.diff(np.log(data), axis=0)
    # est = VAR(adj_data, p=2, dates=dates[1:], names=names)
    model = VAR(adj_data[:-16], dates=dates[1:-16], names=names)
    est = model.fit(maxlags=2)
    irf = est.irf()

    y = est.y[-2:]

    est2 = VAR2(adj_data[:-16])
    res2 = est2.fit(maxlag=2)
    """
    # irf.plot_irf()

    # i = 2; j = 1
    # cv = irf.cum_effect_cov(orth=True)
    # print np.sqrt(cv[:, j * 3 + i, j * 3 + i]) / 1e-2

    # data = np.genfromtxt('Canada.csv', delimiter=',', names=True)
    # data = data.view((float, 4))

    mdata = sm.datasets.macrodata.load().data
    data = mdata[['realinv','realgdp','realcons']].view((float,3))
    data = np.diff(np.log(data), axis=0)

    model = VAR(data)
    model2 = VAR2(data)

    est = model.fit(maxlags=2)
    est2 = model2.fit(maxlag=2)
    irf = est.irf()


