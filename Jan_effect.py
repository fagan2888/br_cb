# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 12:45:37 2016

@author: leicui

@content: January effects
"""

import datacleaning
import pandas as pd
import numpy as np

#colname for the data
"""
['IssueDate',
 'Benchmark',
 'Benchmark Treasury',
 'Bond Type',
 'BondTypeCode',
 'Business Description',
 'Coupon(%)',
 'DenominationsCurrency2',
 'DomicileNationCode',
 'FitchRating',
 'Foreign Issue Flag(eg Yankee)(Y/N)',
 'Industry',
 'IssueType2',
 'Issuer',
 'LiborSpread',
 'Marketplace',
 'Maturity',
 'MoodyRating',
 'Nation',
 'OfferYieldto Maturity(%)',
 'PrincipalAmount($ mil)',
 'PrincipalAmountIn Currency(mil)',
 'PrincipalAmt - inthis Mkt(euro mil)',
 'Prncpl Amtin Curr ofIss - in thisMkt (mil)',
 'Prncpl Amtin Curr ofIss - in thisMkt (mil).1',
 'SpreadtoBench-Mark',
 "Stan-dard&Poor's",
 'Treasury',
 'TypeofSecurity',
 'Domicile',
 'Issue_year',
 'Issue_month',
 'bond_terms']
"""

if __name__ == '__main__':
    
    SSA_df = pd.read_csv("/Users/leicui/blackrock_data/SSA.csv")
    corp_df = pd.read_csv("/Users/leicui/blackrock_data/corp.csv")
    
    datacleaning.notionalAmountByYearPlot(SSA_df, 'Issue_year', 'Issue_month', 'PrincipalAmount($ mil)', 'notional_bymoth_SSA.jpg')
    datacleaning.notionalAmountByYearPlot(corp_df, 'Issue_year', 'Issue_month', 'PrincipalAmount($ mil)', 'notional_bymoth_corp.jpg')
    '''
    jan_SSA_df = SSA_df[SSA_df.Issue_month == 1]
    jan_corp_df = corp_df[corp_df.Issue_month == 1]
    
    datacleaning.numIssueByYearPie(jan_SSA_df, 'Issue_year', 'Domicile', 5, 'Dom_jan_SSA.jpg')
    datacleaning.numIssueByYearPie(jan_corp_df, 'Issue_year', 'Domicile', 5, 'Dom_jan_corp.jpg')
    '''
    china_SSA_df = SSA_df[SSA_df.Domicile == "China"]
    china_corp_df = corp_df[corp_df.Domicile == "China"]
    
    #datacleaning.numIssueByYearBar(china_SSA_df, 'Issue_year', 'Marketplace', 'china_mp_SSA.jpg')
    datacleaning.numIssueByYearBar(china_corp_df, 'Issue_year', 'Marketplace', 'china_mp_corp.jpg')
    #datacleaning.numIssueByYearBar(china_SSA_df, 'Issue_year', 'DenominationsCurrency2', 'china_currency_SSA.jpg')
    datacleaning.numIssueByYearBar(china_corp_df, 'Issue_year', 'DenominationsCurrency2', 'china_currency_corp.jpg')
    #datacleaning.numIssueByYearBar(china_SSA_df, 'Issue_year', 'TypeofSecurity', 'china_type_SSA.jpg')
    datacleaning.numIssueByYearBar(china_corp_df, 'Issue_year', 'TypeofSecurity', 'china_type_corp.jpg')
    
    
    