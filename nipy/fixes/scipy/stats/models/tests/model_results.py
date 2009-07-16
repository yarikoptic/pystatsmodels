import numpy as np
import os
import models
import glm_test_resids
#TODO: Streamline this with RModelwrap

def generated_data():
    '''
    Returns `Y` and `X` from test_data.bin

    Returns
    -------
    Y : array
        Endogenous Data
    X : array
        Exogenous Data
    '''
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
            "test_data.bin")
    data = np.fromfile(filename, "<f8")
    data.shape = (126,15)
    y = data[:,0]
    x = data[:,1:]
    return y,x

class lbw(object):
    '''
    The LBW data can be found here 

    http://www.stata-press.com/data/r9/rmain.html

    X is the entire data as a record array.
    '''
    def __init__(self):
        # data set up for data not in datasets
        filename="stata_lbw_glm.csv"
        data=np.recfromcsv(filename, converters={4: lambda s: s.strip("\"")})
        data = models.functions.xi(data, col='race', drop=True)
        self.endog = data.low
        design = np.column_stack((data['age'], data['lwt'], 
                    data['black'], data['other'], data['smoke'], data['ptl'], 
                    data['ht'], data['ui']))
        self.exog = models.functions.add_constant(design)
        # Results for Canonical Logit Link
        self.params = (-.02710031, -.01515082, 1.26264728, 
                        .86207916, .92334482, .54183656, 1.83251780, 
                        .75851348, .46122388)
        self.bse = (0.036449917, 0.006925765, 0.526405169, 
                0.439146744, 0.400820976, 0.346246857, 0.691623875, 
                0.459373871, 1.204574885)
        self.aic_R = 219.447991133
        self.aic_Stata = 1.1611
        self.deviance = 201.447991133
        self.scale = 1
        self.llf = -100.7239955662511
        self.null_deviance = 234.671996193219
        self.bic = -742.0665
        self.df_resid = 180
        self.df_model = 8
        self.df_null = 188
        self.pearsonX2 = 182.0233425
        self.resids = glm_test_resids.lbw_resids

class cpunish(object):
    '''
    The following are from the R script in models.datasets.cpunish
    Slightly different than published results, but should be correct
    Probably due to rounding in cleaning?
    '''
    def __init__(self):
        self.params = (2.611017e-04, 7.781801e-02, -9.493111e-02, 2.969349e-01,
                2.301183e+00, -1.872207e+01, -6.801480e+00)
        self.bse = (5.187132e-05, 7.940193e-02, 2.291926e-02, 4.375164e-01, 
                4.283826e-01, 4.283961e+00, 4.146850e+00)
        self.null_deviance = 136.57281747225
        self.df_null = 16
        self.deviance = 18.59164
        self.df_resid = 10
        self.df_model = 6
        self.aic_R = 77.85466   # same as Stata
        self.aic_Stata = 4.579686
        self.bic = -9.740492
        self.llf = -31.92732831
        self.scale = 1
        self.pearsonX2 = 24.75374835
        self.resids = glm_test_resids.cpunish_resids

class scotvote(object):
    def __init__(self):
        self.params = (4.961768e-05, 2.034423e-03, -7.181429e-05, 1.118520e-04,
                -1.467515e-07, -5.186831e-04, -2.42717498e-06, -1.776527e-02)
        self.bse = (1.621577e-05, 5.320802e-04, 2.711664e-05, 4.057691e-05, 
            1.236569e-07, 2.402534e-04, 7.460253e-07, 1.147922e-02)
        self.null_deviance = 0.536072
        self.df_null = 31
        self.deviance = 0.087388516417        
        self.df_resid = 24
        self.df_model = 7
        self.aic_R = 182.947045954721
        self.aic_Stata = 10.72212        
        self.bic = -83.09027
        self.llf = -163.5539382 # from Stata, same as ours with scale = 1
        self.llf_R = -82.47352  # Very close to ours as is
        self.scale = 0.003584283
        self.pearsonX2 = .0860228056
        self.resids = glm_test_resids.scotvote_resids

class star98(object):
    def __init__(self):
        self.params = (-0.0168150366,  0.0099254766, -0.0187242148, 
            -0.0142385609, 0.2544871730,  0.2406936644,  0.0804086739,
            -1.9521605027, -0.3340864748, -0.1690221685,  0.0049167021, 
            -0.0035799644, -0.0140765648, -0.0040049918, -0.0039063958,  
            0.0917143006,  0.0489898381,  0.0080407389,  0.0002220095,
            -0.0022492486, 2.9588779262)
        self.bse = (4.339467e-04, 6.013714e-04, 7.435499e-04, 4.338655e-04,
            2.994576e-02, 5.713824e-02, 1.392359e-02, 3.168109e-01,
            6.126411e-02, 3.270139e-02, 1.253877e-03, 2.254633e-04, 
            1.904573e-03, 4.739838e-04, 9.623650e-04, 1.450923e-02, 
            7.451666e-03, 1.499497e-03, 2.988794e-05, 3.489838e-04, 
            1.546712e+00)
        self.null_deviance = 34345.3688931
        self.df_null = 302
        self.deviance = 4078.76541772        
        self.df_resid = 282
        self.df_model = 20
        self.aic_R = 6039.22511799
        self.aic_Stata = 19.93144        
        self.bic = 2467.494
        self.llf = -2998.612928
        self.scale = 1.
        self.pearsonX2 = 4051.921614
        self.resids = glm_test_resids.star98_resids

class inv_gauss():
    '''
    Data was generated by Hardin and Hilbe using Stata.
    Note only the first 5000 observations are used because
    the models code currently uses np.eye.
    '''
    def __init__(self):
        # set up data #
        filename="inv_gaussian.csv"
        data=np.genfromtxt(filename, delimiter=",", skiprows=1)
        self.endog = data[:5000,0]
        self.exog = data[:5000,1:]
        self.exog = models.functions.add_constant(self.exog)


