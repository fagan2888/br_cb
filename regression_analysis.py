import pandas as pd
import numpy as np
from pandas.stats.api import ols
from datetime import datetime
from dateutil.relativedelta import relativedelta
from statsmodels.stats.outliers_influence import variance_inflation_factor as vif

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

def regression(Currency,typ):
    
    #typ='Corp'
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
    res4 = ols(y = reg_df['PrincipalAmount($mil)'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile']])
    res5 = ols(y = reg_df['normal_amount_1y'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile']])
    res6 = ols(y = reg_df['normal_amount_2y'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile']])
  
    correl_matrix=reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile','credit_market','credit_domicile']].corr()
    
    return res1, res2, res3, res4, res5, res6, reg_df, correl_matrix
    
def regression_without_ccy_nation(Currency,typ):
    
    #typ='Corp'
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
    reg_df=reg_df[reg_df['Currency']!=reg_df['Nation']]
    
    res1 = ols(y = reg_df['PrincipalAmount($mil)'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile','credit_market','credit_domicile']])
    res2 = ols(y = reg_df['normal_amount_1y'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile','credit_market','credit_domicile']])
    res3 = ols(y = reg_df['normal_amount_2y'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile','credit_market','credit_domicile']])
    res4 = ols(y = reg_df['PrincipalAmount($mil)'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile']])
    res5 = ols(y = reg_df['normal_amount_1y'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile']])
    res6 = ols(y = reg_df['normal_amount_2y'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile']])
  
    correl_matrix=reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile','Curve_domicile','credit_market','credit_domicile']].corr()
    
    return res1, res2, res3, res4, res5, res6, reg_df, correl_matrix

Currency='SEK';
typ='Corp';
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
reg_df=reg_df[reg_df['Currency']!=reg_df['Nation']]

# Regression 1

# Without r_domicile

resa = ols(y = reg_df['PrincipalAmount($mil)'], x = reg_df[['r_market','Butterfly_market','Curve_market','Butterfly_domicile','Curve_domicile']])
res1 = ols(y = reg_df['normal_amount_1y'], x = reg_df[['r_market','Butterfly_market','Curve_market','Butterfly_domicile','Curve_domicile']])
res2 = ols(y = reg_df['normal_amount_2y'], x = reg_df[['r_market','Butterfly_market','Curve_market','Butterfly_domicile','Curve_domicile']])

# Without r_domicile and r_market

resb = ols(y = reg_df['PrincipalAmount($mil)'], x = reg_df[['Butterfly_market','Curve_market','Butterfly_domicile','Curve_domicile']])
res3 = ols(y = reg_df['normal_amount_1y'], x = reg_df[['Butterfly_market','Curve_market','Butterfly_domicile','Curve_domicile']])
res4 = ols(y = reg_df['normal_amount_2y'], x = reg_df[['Butterfly_market','Curve_market','Butterfly_domicile','Curve_domicile']])

# Without r_domicile and r_market and curve_domicile

resc = ols(y = reg_df['PrincipalAmount($mil)'], x = reg_df[['Butterfly_market','Curve_market','Butterfly_domicile']])
res5 = ols(y = reg_df['normal_amount_1y'], x = reg_df[['Butterfly_market','Curve_market','Butterfly_domicile']])
res6 = ols(y = reg_df['normal_amount_2y'], x = reg_df[['Butterfly_market','Curve_market','Butterfly_domicile']])

resd = ols(y = reg_df['PrincipalAmount($mil)'], x = reg_df[['r_market','Butterfly_market']])
res7 = ols(y = reg_df['normal_amount_1y'], x = reg_df[['r_market','Butterfly_market']])
res8 = ols(y = reg_df['normal_amount_2y'], x = reg_df[['r_market','Butterfly_market']])

rese = ols(y = reg_df['PrincipalAmount($mil)'], x = reg_df[['Butterfly_market','Butterfly_domicile']])
res9 = ols(y = reg_df['normal_amount_1y'], x = reg_df[['Butterfly_market','Butterfly_domicile']])
res10 = ols(y = reg_df['normal_amount_2y'], x = reg_df[['Butterfly_market','Butterfly_domicile']])



writer = pd.ExcelWriter('Regression_Corp_SEK.xlsx', engine='xlsxwriter')
    
typ='Corp'      
Cur='SEK'
i=0;
maxt = res1.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO r_domicile')

i=1;
maxt = res2.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO r_domicile')

i=2;
maxt = resa.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO r_domicile')



i=0;
maxt = res3.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO r_dom_r_market')

i=1;
maxt = res4.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO r_dom_r_market')

i=2;
maxt = resb.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO r_dom_r_market')

i=0;
maxt = res5.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO r_dom_r_market_curve_dom')

i=1;
maxt = res6.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO r_dom_r_market_curve_dom')

i=2;
maxt = resc.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO r_dom_r_market_curve_dom')


i=0;
maxt = res7.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'r_market_butterfly_mkt')

i=1;
maxt = res8.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'r_market_butterfly_mkt')

i=2;
maxt = resd.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'r_market_butterfly_mkt')

i=0;
maxt = res9.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'butterfly')

i=1;
maxt = res10.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'butterfly')

i=2;
maxt = rese.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'butterfly')

writer.save()

 Currency='USD';
typ='Corp';
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
reg_df=reg_df[reg_df['Currency']!=reg_df['Nation']]

# Regression 1

# Without curve_domicile

res1 = ols(y = reg_df['normal_amount_1y'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile']])
res2 = ols(y = reg_df['normal_amount_2y'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile']])
res3 = ols(y = reg_df['PrincipalAmount($mil)'], x = reg_df[['r_market','Butterfly_market','Curve_market','r_domicile','Butterfly_domicile']])


writer = pd.ExcelWriter('Regression_Corp_USD.xlsx', engine='xlsxwriter')
    
typ='Corp'      
Cur='USD'
i=0;
maxt = res1.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO curve_domicile')

i=1;
maxt = res2.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO curve_domicile')

i=2;
maxt = res3.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO curve_domicile')

writer.save()

Currency='GBP';
typ='Corp';
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
reg_df=reg_df[reg_df['Currency']!=reg_df['Nation']]

# Regression 1

# Without curve_domicile

resa = ols(y = reg_df['PrincipalAmount($mil)'], x = reg_df[['r_market','Curve_market','r_domicile','Curve_domicile']])
res1 = ols(y = reg_df['normal_amount_1y'], x = reg_df[['r_market','Curve_market','r_domicile','Curve_domicile']])
res2 = ols(y = reg_df['normal_amount_2y'], x = reg_df[['r_market','Curve_market','r_domicile','Curve_domicile']])

resb = ols(y = reg_df['PrincipalAmount($mil)'], x = reg_df[['r_market','r_domicile','Curve_domicile']])
res3 = ols(y = reg_df['normal_amount_1y'], x = reg_df[['r_market','r_domicile','Curve_domicile']])
res4 = ols(y = reg_df['normal_amount_2y'], x = reg_df[['r_market','r_domicile','Curve_domicile']])


writer = pd.ExcelWriter('Regression_Corp_GBP.xlsx', engine='xlsxwriter')
    
typ='Corp'      
Cur='GBP'
i=0;
maxt = res1.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO btfly_domicile btfly_mkt')

i=1;
maxt = res2.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO btfly_domicile btfly_mkt')

i=2;
maxt = resa.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO btfly_domicile btfly_mkt')

i=0;
maxt = res3.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO btfly_md_curve_mkt')

i=1;
maxt = res4.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO btfly_md_curve_mkt')

i=2;
maxt = resb.summary_as_matrix.transpose()
ncol = maxt.shape[1]
maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = 'WO btfly_md_curve_mkt')
writer.save()


