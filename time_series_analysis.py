# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 12:55:09 2016

@author: leicui

@content: For regression
"""

import pandas as pd
import numpy as np
from pandas.stats.api import ols


ROOT_DIR = '/Users/leicui/Dropbox (blackrock project)/blackrock project/'

SSA_DICT = {'AUD': 'Australia TS SSA.csv' , \
			'CAD': 'Canada TS SSA.csv', \
			'EUR': 'EURO TS SSA.csv',\
			'GBP': 'UK TS SSA.csv', \
			'JPY': 'Japanese TS SSA.csv',\
			'SEK': 'Sweden TS SSA.csv',\
			'USD': 'US TS SSA.csv'}
  

CORP_DICT = {'AUD': 'Australia TS Corp.csv' , \
			'CAD': 'Canada TS Corp.csv', \
			'EUR': 'EURO TS Corp.csv',\
			'GBP': 'UK TS Corp.csv', \
			'JPY': 'Japanese TS Corp.csv',\
			'SEK': 'Sweden TS Corp.csv',\
			'USD': 'US TS Corp.csv'}
			
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
                        'United Kingdom': 'GBP', \
                        'Sweden': 'SEK',  \
                        'Canada': 'CAD', \
                        'Norway': 'NOK', \
                        'Japan': 'JPY', \
                        'Eurozone': 'EUR', \
                        'U.S.': 'USD', \
                        'New Zealand': 'NZD'}


def add_value(target_df, data_df,  group_col, typ):
    df_ls = []
    grouped = pd.groupby(target_df, group_col)
	
    for key, sub_df in grouped:
        if typ == 'swap':
            nation_swap = data_df[data_df.Currency == NATION_CURRENCY_DICT[key]]
            df_ls.append(sub_df.join(nation_swap[['10Y', 'Butterfly 10y', 'Curve 10y']]))
        elif typ == 'credit':
            credit_df = pd.read_csv(ROOT_DIR + 'cleaned data/Monthly credit spread curves/' + CREDIT_DICT[NATION_CURRENCY_DICT[key]],parse_dates = True, infer_datetime_format=True )
            credit_df.Date = pd.to_datetime(credit_df.Date, infer_datetime_format = True)
            credit_df.set_index('Date', inplace = True)
                
            df_ls.append(sub_df.join(credit_df['10Y']))
    return pd.concat(df_ls)
	
	
	



def regression_data(Currency, typ):
    
    if typ == 'Corp':
        reg_df = pd.read_csv(ROOT_DIR  + 'cleaned data/Notional Time Series/' + typ +'/' + CORP_DICT[Currency], parse_dates = True, infer_datetime_format=True)
    else:
         reg_df = pd.read_csv(ROOT_DIR  + 'cleaned data/Notional Time Series/' + typ +'/' + SSA_DICT[Currency], parse_dates = True, infer_datetime_format=True)
    
    reg_df = reg_df[['IssueDate','Currency','Nation','PrincipalAmount($mil)']]
    reg_df.IssueDate = pd.to_datetime(reg_df.IssueDate, infer_datetime_format = True)
    reg_df.set_index('IssueDate', inplace = True)
    #nation of interest 
    nation_ls = ['Australia', 'United Kingdom', 'Sweden', 'Canada', 'Norway', 'Japan', 'Eurozone', 'U.S.', 'New Zealand']
 
    reg_df = reg_df[reg_df.Nation.isin(nation_ls)]
    swap_df = pd.read_csv(ROOT_DIR + 'materials/BBG curves/Swap curves/Database Butterfly-Curve/All_Butterfly_Spreads_monthly.csv',  parse_dates = True, infer_datetime_format=True)
    swap_df.Date = pd.to_datetime(swap_df.Date, infer_datetime_format = True)
    swap_df.set_index('Date', inplace = True)
    market_swap_df = swap_df[swap_df.Currency == Currency]
    
     
    reg_df = reg_df.join(market_swap_df[['10Y', 'Butterfly 10y', 'Curve 10y']]) 
    #rename colunms
    reg_df.rename(columns = {'10Y': 'r_market', 'Butterfly 10y': 'Butterfly_market', 'Curve 10y': 'Curve_market'}, inplace = True)
    #add interest rate level, butterfly rate, curve rate for domicile nation    
    reg_df = add_value(reg_df, swap_df, 'Nation','swap')
    reg_df.rename(columns = {'10Y': 'r_domicile', 'Butterfly 10y': 'Butterfly_domicile', 'Curve 10y': 'Curve_domicile'}, inplace = True)
        
    #add credit spread for market
    credit_df = pd.read_csv(ROOT_DIR + 'cleaned data/Monthly credit spread curves/' + CREDIT_DICT[Currency],parse_dates = True, infer_datetime_format=True )
    credit_df.Date = pd.to_datetime(credit_df.Date, infer_datetime_format = True)
    credit_df.set_index('Date', inplace = True)
    reg_df = reg_df.join(credit_df['10Y'])
    reg_df.rename(columns = {'10Y': 'credit_market'}, inplace = True)
    reg_df = add_value(reg_df, swap_df, 'Nation', 'credit')
    
    reg_df.rename(columns = {'10Y': 'credit_domicile'}, inplace = True)
    
    return reg_df
    

if __name__ == '__main__':

    #writer = pd.ExcelWriter('Regression.xlsx', engine='xlsxwriter')
    
    
    Currency_ls = ['AUD', 'CAD', 'EUR', 'JPY', 'SEK', 'USD', 'GBP']
    '''    
    for Cur in Currency_ls:
        result = regression(Cur)
        for i in range(len(result)):
            if i < len(result) - 1:
                maxt = result[i].summary_as_matrix.transpose()
                ncol = maxt.shape[1]
                maxt.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = Cur)
            else:
                if Cur != 'USD':
                    df = result[i][['10Y','Butterfly 10y', 'Curve 10y', 'r_level', 'PrincipalAmount($mil)', 'normal_amount']]
                else:
                    df = result[i][['10Y','Butterfly 10y', 'Curve 10y', 'PrincipalAmount($mil)', 'normal_amount']]
                    df.to_excel(writer, startcol = (ncol + 2)*i, startrow = 1, sheet_name = Cur)
    writer.save()
    '''
    
    for typ in ['Corp', 'SSA']:
        for Cur in Currency_ls:
            if typ == 'Corp':
                writer = pd.ExcelWriter(ROOT_DIR + 'cleaned data/regression data/Corp/' + Cur + '_' + typ + '.xlsx', engine = 'xlsxwriter')
            else:
                writer = pd.ExcelWriter(ROOT_DIR + 'cleaned data/regression data/SSA/' + Cur + '_' + typ + '.xlsx', engine = 'xlsxwriter')
            df = regression_data(Cur, typ)
            
            df.to_excel(writer)
            
            writer.save()
            
    

	