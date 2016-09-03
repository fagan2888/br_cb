import pandas as pd
import numpy as np
from pandas.stats.api import ols
from datetime import datetime
from dateutil.relativedelta import relativedelta

ROOT_DIR = 'C:/Users/Philippe/Documents/blackrock project/'

MARKET_DICT = {'AUD': 'Australia TS SSA.csv' , \
			'CAD': 'Canada TS SSA.csv', \
			'EUR': 'EURO TS SSA.csv',\
			'GBP': 'UK TS SSA.csv', \
			'JPY': 'Japanese TS SSA.csv',\
			'SEK': 'Sweden TS SSA.csv',\
			'USD': 'US TS SSA.csv'}

CREDIT_DICT = {  'AUD': 'AUD Australia Corporate A+, A, A- Spread Curve monthly.csv' , \
			'CAD': 'CAD Canada Corporate A+, A, A- Spread Curve monthly.csv', \
			'EUR': 'EUR Europe Corporate A+, A, A- Spread Curve monthly.csv',\
			'JPY': 'JPY Japan Corporate A+, A, A- Spread Curve monthly.csv',\
			'SEK': 'SEK Europe Corporate AA+ , AA , AA- Spread Curve monthly.csv',\
			'USD': 'USD US Corporate A+, A, A- Spread Curve monthly.csv', \
                 'NOK': 'NOK Europe Agency & Regionals Spread Curve monthly.csv',\
                 'NZD': 'NZD New Zealand Financials AA+ , AA , AA- Spread Curve monthly.csv',\
                 'GBP': 'GBP Europe Composite AA+ , AA , AA- Spread Curve monthly.csv'}
   
NATION_CURRENCY_DICT = {'Australia': 'AUD', \
                        'UK': 'GBP', \
                        'Sweden': 'SEK',  \
                        'Canada': 'CAD', \
                        'Norway': 'NOK', \
                        'Japanese': 'JPY', \
                        'EURO': 'EUR', \
                        'US': 'USD', \
                        'New Zealand': 'NZD'}
#Keys for JPY, Euro, US, UK have changed


def regression(Currency,typ):
    
    """
    computes the 3 OLS regressions on the notional, 12-month standardized and 24-month standardized notionals
    
    Inputs:
    
    Currency:    string
                 currency of denomination
    typ:         string
                 SSA or Corp
    
    Outputs:
    
    res1:       pd structure
                results of the OLS regression over notional 
    res2:       pd structure
                results of the OLS regression over 12-month standardized notional
    res3:       pd structure
                results of the OLS regression over 24-month standardized notional
    
    reg_df:     pd database
                data for the regression filtered by currency of denomination
    correl_matrix:    pd database
                      correlation matrix between the regressors
    
    """
    
    
    #nation of interest 
    reg_df=pd.read_excel(ROOT_DIR  + 'cleaned data/regression data/' + typ +'/' + Currency + '_' + typ +'.xlsx',)
    key_ccy=list(NATION_CURRENCY_DICT.keys())[list(NATION_CURRENCY_DICT.values()).index(Currency)];
    reg_df=reg_df[reg_df.Currency==key_ccy]

    n=len(reg_df.index);
    mu1=np.zeros(n)
    sigma1=np.zeros(n)
    mu2=np.zeros(n)
    sigma2=np.zeros(n)
    for i in range(n):
        date_obs=reg_df['Date'][i]
        mu1[i]=np.mean(reg_df[(reg_df['Date']>date_obs+relativedelta(months=-12)) & (reg_df['Date']<=date_obs)]['PrincipalAmount($mil)'])
        mu2[i]=np.mean(reg_df[(reg_df['Date']>date_obs+relativedelta(months=-24)) & (reg_df['Date']<=date_obs)]['PrincipalAmount($mil)'])
        sigma1[i]=np.std(reg_df[(reg_df['Date']>date_obs+relativedelta(months=-12)) & (reg_df['Date']<=date_obs)]['PrincipalAmount($mil)'])
        sigma2[i]=np.std(reg_df[(reg_df['Date']>date_obs+relativedelta(months=-24)) & (reg_df['Date']<=date_obs)]['PrincipalAmount($mil)'])
    
    
    reg_df['normal_amount_1y'] = (reg_df['PrincipalAmount($mil)'] - mu1)/sigma1
    reg_df['normal_amount_2y'] = (reg_df['PrincipalAmount($mil)'] - mu2)/sigma2
    cols = reg_df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    reg_df = reg_df[cols]
    
    res1 = ols(y = reg_df['PrincipalAmount($mil)'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile','credit_market','credit_domicile']])
    res2 = ols(y = reg_df['normal_amount_1y'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile','credit_market','credit_domicile']])
    res3 = ols(y = reg_df['normal_amount_2y'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile','credit_market','credit_domicile']])
    
    correl_matrix=reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile','credit_market','credit_domicile']].corr()
    
    return res1, res2, res3, reg_df, correl_matrix
