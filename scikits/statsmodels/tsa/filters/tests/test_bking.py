from numpy.testing import assert_almost_equal
from numpy import array
from scikits.statsmodels.datasets import macrodata
from scikits.statsmodels.tsa.filters import baxter_king

def test_bking1d():
    """
    Test Baxter King band-pass filter. Results are taken from Stata
    """
    bking_results = array([7.320813, 2.886914, -6.818976, -13.49436, 
                -13.27936, -9.405913, -5.691091, -5.133076, -7.273468, 
                -9.243364, -8.482916, -4.447764, 2.406559, 10.68433, 
                19.46414, 28.09749, 34.11066, 33.48468, 24.64598, 9.952399, 
                -4.265528, -12.59471, -13.46714, -9.049501, -3.011248, 
                .5655082, 2.897976, 7.406077, 14.67959, 18.651, 13.05891, 
                -2.945415, -24.08659, -41.86147, -48.68383, -43.32689, 
                -31.66654, -20.38356, -13.76411, -9.978693, -3.7704, 10.27108, 
                31.02847, 51.87613, 66.93117, 73.51951, 73.4053, 69.17468, 
                59.8543, 38.23899, -.2604809, -49.0107, -91.1128, -112.1574, 
                -108.3227, -86.51453, -59.91258, -40.01185, -29.70265, 
                -22.76396, -13.08037, 1.913622, 20.44045, 37.32873, 46.79802, 
                51.95937, 59.67393, 70.50803, 81.27311, 83.53191, 67.72536, 
                33.78039, -6.509092, -37.31579, -46.05207, -29.81496, 1.416417,
                28.31503, 
                32.90134, 8.949259, -35.41895, -84.65775, -124.4288, -144.6036, 
                -140.2204, -109.2624, -53.6901, 15.07415, 74.44268, 104.0403, 
                101.0725, 76.58291, 49.27925, 36.15751, 36.48799, 37.60897, 
                27.75998, 4.216643, -23.20579, -39.33292, -36.6134, -20.90161, 
                -4.143123, 5.48432, 9.270075, 13.69573, 22.16675, 33.01987, 
                41.93186, 47.12222, 48.62164, 47.30701, 40.20537, 22.37898, 
                -7.133002, -43.3339, -78.51229, -101.3684, -105.2179, 
                -90.97147, 
                -68.30824, -48.10113, -35.60709, -31.15775, -31.82346, 
                -32.49278, -28.22499, -14.42852, 10.1827, 36.64189, 49.43468, 
                38.75517, 6.447761, -33.15883, -62.60446, -72.87829, -66.54629, 
                -52.61205, -38.06676, -26.19963, -16.51492, -7.007577, 
                .6125674, 
                7.866972, 14.8123, 22.52388, 30.65265, 39.47801, 49.05027, 
                59.02925, 
                72.88999, 95.08865, 125.8983, 154.4283, 160.7638, 130.6092, 
                67.84406, -7.070272, -68.08128, -99.39944, -104.911, 
                -100.2372, -98.11596, -104.2051, -114.0125, -113.3475, 
                -92.98669, -51.91707, -.7313812, 43.22938, 64.62762, 64.07226,
                59.35707, 67.06026, 91.87247, 124.4591, 151.2402, 163.0648, 
                154.6432])
    X = macrodata.load().data['realinv']
    Y = baxter_king(X, 6, 32, 12)
    assert_almost_equal(Y,bking_results,4)

def test_bking2d():
    """
    Test Baxter-King band-pass filter with 2d input
    """
    bking_results = array([[7.320813,-.0374475], [2.886914,-.0430094], 
        [-6.818976,-.053456], [-13.49436,-.0620739], [-13.27936,-.0626929], 
        [-9.405913,-.0603022], [-5.691091,-.0630016], [-5.133076,-.0832268], 
        [-7.273468,-.1186448], [-9.243364,-.1619868], [-8.482916,-.2116604],
        [-4.447764,-.2670747], [2.406559,-.3209931], [10.68433,-.3583075], 
        [19.46414,-.3626742], [28.09749,-.3294618], [34.11066,-.2773388], 
        [33.48468,-.2436127], [24.64598,-.2605531], [9.952399,-.3305166], 
        [-4.265528,-.4275561], [-12.59471,-.5076068], [-13.46714,-.537573], 
        [-9.049501,-.5205845], [-3.011248,-.481673], [.5655082,-.4403994],
        [2.897976,-.4039957], [7.406077,-.3537394], [14.67959,-.2687359], 
        [18.651,-.1459743], [13.05891,.0014926], [-2.945415,.1424277],
        [-24.08659,.2451936], [-41.86147,.288541], [-48.68383,.2727282], 
        [-43.32689,.1959127], [-31.66654,.0644874], [-20.38356,-.1158372], 
        [-13.76411,-.3518627], [-9.978693,-.6557535], [-3.7704,-1.003754],
        [10.27108,-1.341632], [31.02847,-1.614486], [51.87613,-1.779089], 
        [66.93117,-1.807459], [73.51951,-1.679688], [73.4053,-1.401012], 
        [69.17468,-.9954996], [59.8543,-.511261], [38.23899,-.0146745],
        [-.2604809,.4261311], [-49.0107,.7452514], [-91.1128,.8879492], 
        [-112.1574,.8282748], [-108.3227,.5851508], [-86.51453,.2351699], 
        [-59.91258,-.1208998], [-40.01185,-.4297895], [-29.70265,-.6821963], 
        [-22.76396,-.9234254], [-13.08037,-1.217539], [1.913622,-1.57367], 
        [20.44045,-1.927008], [37.32873,-2.229565], [46.79802,-2.463154], 
        [51.95937,-2.614697], [59.67393,-2.681357], [70.50803,-2.609654], 
        [81.27311,-2.301618], [83.53191,-1.720974], [67.72536,-.9837123], 
        [33.78039,-.2261613], [-6.509092,.4546985], [-37.31579,1.005751], 
        [-46.05207,1.457224], [-29.81496,1.870815], [1.416417,2.263313], 
        [28.31503,2.599906], [32.90134,2.812282], [8.949259,2.83358], 
        [-35.41895,2.632667], [-84.65775,2.201077], [-124.4288,1.598951], 
        [-144.6036,.9504762], [-140.2204,.4187932], [-109.2624,.1646726], 
        [-53.6901,.2034265], [15.07415,.398165], [74.44268,.5427476], 
        [104.0403,.5454975], [101.0725,.4723354], [76.58291,.4626823], 
        [49.27925,.5840143], [36.15751,.7187981], [36.48799,.6058422], 
        [37.60897,.1221227], [27.75998,-.5891272], [4.216643,-1.249841], 
        [-23.20579,-1.594972], [-39.33292,-1.545968], [-36.6134,-1.275494], 
        [-20.90161,-1.035783], [-4.143123,-.9971732], [5.48432,-1.154264], 
        [9.270075,-1.29987], [13.69573,-1.240559], [22.16675,-.9662656], 
        [33.01987,-.6420301], [41.93186,-.4698712], [47.12222,-.4527797], 
        [48.62164,-.4407153], [47.30701,-.2416076], [40.20537,.2317583], 
        [22.37898,.8710276], [-7.133002,1.426177], [-43.3339,1.652785], 
        [-78.51229,1.488021], [-101.3684,1.072096], [-105.2179,.6496446], 
        [-90.97147,.4193682], [-68.30824,.41847], [-48.10113,.5253419], 
        [-35.60709,.595076], [-31.15775,.5509905], [-31.82346,.3755519], 
        [-32.49278,.1297979], [-28.22499,-.0916165], [-14.42852,-.2531037], 
        [10.1827,-.3220784], [36.64189,-.2660561], [49.43468,-.1358522], 
        [38.75517,-.0279508], [6.447761,.0168735], [-33.15883,.0315687], 
        [-62.60446,.0819507], [-72.87829,.2274033], [-66.54629,.4641401], 
        [-52.61205,.7211093], [-38.06676,.907773], [-26.19963,.9387103], 
        [-16.51492,.7940786], [-7.007577,.5026631], [.6125674,.1224996], 
        [7.866972,-.2714422], [14.8123,-.6273921], [22.52388,-.9124271], 
        [30.65265,-1.108861], [39.47801,-1.199206], [49.05027,-1.19908],
        [59.02925,-1.139046], [72.88999,-.9775021], [95.08865,-.6592603], 
        [125.8983,-.1609712], [154.4283,.4796201], [160.7638,1.100565], 
        [130.6092,1.447148], [67.84406,1.359608], [-7.070272,.8931825], 
        [-68.08128,.2619787], [-99.39944,-.252208], [-104.911,-.4703874], 
        [-100.2372,-.4430657], [-98.11596,-.390683], [-104.2051,-.5647846], 
        [-114.0125,-.9397582], [-113.3475,-1.341633], [-92.98669,-1.567337], 
        [-51.91707,-1.504943], [-.7313812,-1.30576], [43.22938,-1.17151], 
        [64.62762,-1.136151], [64.07226,-1.050555], [59.35707,-.7308369], 
        [67.06026,-.1766731], [91.87247,.3898467], [124.4591,.8135461], 
        [151.2402,.9644226], [163.0648,.6865934], [154.6432,.0115685]])

    X = macrodata.load().data[['realinv','cpi']].view((float,2))
    Y = baxter_king(X, 6, 32, 12)
    assert_almost_equal(Y,bking_results,4)

if __name__ == "__main__":
    import nose
    nose.runmodule(argv=[__file__, '-vvs', '-x', '--pdb'], exit=False)
