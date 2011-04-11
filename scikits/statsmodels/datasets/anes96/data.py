__all__ = ['COPYRIGHT','TITLE','SOURCE','DESCRSHORT','DESCRLONG','NOTE', 'load']

"""American National Election Survey 1996"""

__docformat__ = 'restructuredtext'

COPYRIGHT   = """This is public domain."""
TITLE       = ""
SOURCE      = """
http://www.electionstudies.org/

The American National Election Studies.
"""

DESCRSHORT  = """This data is a subset of the American National Election Studies of 1996."""

DESCRLONG   = DESCRSHORT

NOTE        = """
Number of observations: 944
Numner of variables: 10

Variables name definitions:
        popul : Census place population in 1000s
        TVnews - Number of times per week that respondent watches TV news.
        PID - Party identification of respondent.
            0 - Strong Democrat
            1 - Weak Democrat
            2 - Independent-Democrat
            3 - Independent-Indpendent
            4 - Independent-Republican
            5 - Weak Republican
            6 - Strong Republican
        age : Age of respondent.
        educ - Education level of respondent
            1 - 1-8 grades
            2 - Some high school
            3 - High school graduate
            4 - Some college
            5 - College degree
            6 - Master's degree
            7 - PhD
        income - Income of household
            1 - None or less than $2,999
            2 - $3,000-$4,999                                        
            3 - $5,000-$6,999                                        
            4 - $7,000-$8,999                                        
            5 - $9,000-$9,999                                        
            6 - $10,000-$10,999                                      
            7 - $11,000-$11,999                                      
            8 - $12,000-$12,999                                      
            9 - $13,000-$13,999                                      
            10 - $14,000-$14.999                                      
            11 - $15,000-$16,999                                      
            12 - $17,000-$19,999                                      
            13 - $20,000-$21,999                                      
            14 - $22,000-$24,999                                      
            15 - $25,000-$29,999                                      
            16 - $30,000-$34,999                                      
            17 - $35,000-$39,999                                      
            18 - $40,000-$44,999                                      
            19 - $45,000-$49,999                                      
            20 - $50,000-$59,999                                      
            21 - $60,000-$74,999                                      
            22 - $75,000-89,999                                       
            23 - $90,000-$104,999                                    
            24 - $105,000 and over     
        vote - Expected vote 
            0 - Clinton
            1 - Dole
        The following 3 variables all take the values:
            1 - Extremely liberal
            2 - Liberal
            3 - Slightly liberal
            4 - Moderate
            5 - Slightly conservative
            6 - Conservative
            7 - Extremely Conservative
        selfLR - Respondent's self-reported political leanings from "Left" 
            to "Right".
        ClinLR - Respondents impression of Bill Clinton's political 
            leanings from "Left" to "Right".
        DoleLR  - Respondents impression of Bob Dole's political leanings 
            from "Left" to "Right".
"""

from numpy import recfromtxt, column_stack, array
from scikits.statsmodels.datasets import Dataset
from os.path import dirname, abspath

def load():
    """Load the anes96 data and returns a Dataset class.
   
    Returns
    -------
    Dataset instance: 
        See DATASET_PROPOSAL.txt for more information.
    """
    filepath = dirname(abspath(__file__))
    data = recfromtxt(open(filepath + '/anes96.csv',"rb"), delimiter="\t", 
            names = True, dtype=float)
    names = list(data.dtype.names)
    endog = array(data[names[5]], dtype=float)
    endog_name = names[5]
    exog = column_stack(data[i] for i in names[0:5]+names[6:]).astype(float)
    exog_name = names[0:5]+names[6:]
    dataset = Dataset(data=data, names=names, endog=endog, exog=exog,
            endog_name = endog_name, exog_name=exog_name)
    return dataset
