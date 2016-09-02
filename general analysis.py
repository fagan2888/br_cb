# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 01:31:15 2016

@author: leicui

@content: general analysis of the data
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dataprocessing as dp

ROOTDIR = "/Users/leicui/blackrock_data/figures/"


#column names

'''
['IssueDate',
 'Name',
 'BasisPointSpread',
 'BenchmarkTreasury',
 'BondTypeCode',
 'BondType',
 'BusinessDescription',
 'Coupon(%)',
 'DenominationsCurrency',
 'DomicileNationCode',
 'Exch-ange-ableCode',
 'Exchange-ableType',
 'FitchRating',
 'ForeignIssueFlag(egYankee)(Y/N)',
 'ISIN',
 'Industry',
 'IssueType',
 'LiborSpread',
 'Marketplace',
 'Maturity',
 'MoodyRating',
 'Nation',
 'Nation.1',
 'OfferYieldtoMaturity(%)',
 'PrincipalAmount($mil)',
 'PrincipalAmt-inthisMkt(euromil)',
 'PrincipalAmt-sumofallMkts($mil)',
 'PrincipalAmt-sumofallMkts(euromil)',
 'PrncplAmtinCurrofIss-inthisMkt(mil)',
 'PrncplAmtw/CurrofIss-inthisMkt(mil)',
 'PrncplAmtw/CurrofIss-sumofallMkts(mil)',
 'SpreadtoBench-Mark',
 "Stan-dard&Poor'sRating",
 'Domicile',
 'Currency',
 'CurrAbbrev',
 'Issue_year',
 'Issue_month',
 'bond_terms']
'''

plt.style.use("ggplot")

if __name__ == '__main__':
    #dl.cleaningData("All cross-border & foreign flagged v_9 nation.csv")    
    
    SSA_df = pd.read_csv("/Users/leicui/blackrock_data/SSA.csv", sep = ',', parse_dates = True, infer_datetime_format=True)    
    corp_df = pd.read_csv("/Users/leicui/blackrock_data/corp.csv", sep = ',', parse_dates = True, infer_datetime_format = True)    
    cleaned_df = pd.read_csv("/Users/leicui/blackrock_data/cleaned.csv", sep = ',', parse_dates = True, infer_datetime_format = True)
    
    SSA_df = SSA_df[SSA_df.Issue_year > 2007]
    corp_df = corp_df[corp_df.Issue_year > 2007]
    cleaned_df = cleaned_df[cleaned_df.Issue_year > 2007]
    #data with foreign flag == 'No'    
    #SSA_df = SSA_df[(SSA_df.Issue_year > 2007) & (SSA_df['ForeignIssueFlag(egYankee)(Y/N)'] == 'No')]
    #corp_df = corp_df[(corp_df.Issue_year > 2007) & (corp_df['ForeignIssueFlag(egYankee)(Y/N)'] == 'No')]
    
    total_num = np.shape(SSA_df)[0] + np.shape(corp_df)[0]
    SSA_num = np.shape(SSA_df)[0]
    corp_num = np.shape(corp_df)[0]
    print('Total number of bonds: ', total_num)
    print('Number of SSA bonds: ', SSA_num)
    print('Number of corporate bonds: ', corp_num)
    
    num_flag = np.shape(cleaned_df[cleaned_df['ForeignIssueFlag(egYankee)(Y/N)'] == 'Yes'])[0]
    print('Number of bonds with foreign flag: ', num_flag)
    print('Number of bonds without foreign flag: ', total_num - num_flag)
    
    #ratings 
    worating_df = cleaned_df[cleaned_df['OverallRatingS&P'] == 'NR']  
    worating_num = np.shape(cleaned_df[cleaned_df['OverallRatingS&P'] == 'NR'])[0]
    print('Number of bonds without ratings: ', worating_num)
    
    a = worating_df.Nation.value_counts()
    a.to_csv('ratings.csv')
    
    np.sum( worating_df.Currency.value_counts()[15:]) 
    
    
    
    #sitution where a company in country A issue bonds in country B with currency in Country A
    
    
    #number of issuance each year and total notional amount each year
    issueNum_SSA_df = dp.issueNum_notional(SSA_df, "SSA","Issue_year", 'PrincipalAmount($mil)')
    issueNum_corp_df = dp.issueNum_notional(corp_df, "corp", "Issue_year", 'PrincipalAmount($mil)')
    
    issueNum_df = pd.concat([issueNum_SSA_df,issueNum_corp_df], axis = 1)
    dp.plotissueNum_notional(issueNum_df, ['Notional SSA', 'Notional corp'], ['Issue Num SSA', 'Issue Num corp'], "issueNum_notional.jpg")
    
    #split by domicile country
    #corporates or SSA in which country issue cross-border bonds most
    dp.numIssueByYearPie(SSA_df, "Issue_year", 'Nation', 5,"Issue_nation_SSA.jpg")
    dp.numIssueByYearPie(corp_df, "Issue_year", 'Nation', 5, "Issue_nation_corp.jpg")
    
    #Number of issuance split according to currency
    dp.numIssueByYearBar(SSA_df, "Issue_year", 'Currency', 'Issue_currency_SSA.jpg', 5)
    dp.numIssueByYearBar(corp_df, "Issue_year", 'Currency',  'Issue_cureency_corp.jpg', 5)
    
    #Notional amount by currency in USD
    dp.notionalAmountByYearPlot(SSA_df, "Issue_year", "Currency", 'PrincipalAmount($mil)',"notionalamount_SSA.jpg", 5)
    dp.notionalAmountByYearPlot(corp_df, "Issue_year", "Currency", 'PrincipalAmount($mil)',"notionalamount_corp.jpg", 5)
    
    # distribution of maturity type each year
    dp.plotHistogram(SSA_df[SSA_df.bond_terms >  0], "Issue_year", 'bond_terms', "Maturity_SSA.jpg")
    dp.plotHistogram(corp_df[corp_df.bond_terms > 0], "Issue_year", 'bond_terms', "Maturity_corp.jpg")
    
    # distribution of ratings
    
    rating_ls = ['AAA', 'AA+', 'AA', 'A-', 'AA-', 'A+', 'BBB+', 'A', 'BBB', 'BBB-', 'BB', 'B+', 'B-']
    SSA_new_df = SSA_df[SSA_df['OverallRatingS&P'].isin(rating_ls)]
    corp_new_df = corp_df[corp_df['OverallRatingS&P'].isin(rating_ls)]
    dp.numIssueByYearBar(SSA_new_df, "Issue_year",'OverallRatingS&P', "ratings_SSA.jpg")
    dp.numIssueByYearBar(corp_new_df, "Issue_year",'OverallRatingS&P', "ratings_corp.jpg")
    # distribution of maturity type each year   
    dp.plotHistogram(SSA_df, "Issue_year", 'bond_terms', "Maturity_SSA.jpg")
    dp.plotHistogram(corp_df, "Issue_year", 'bond_terms', "Maturity_corp.jpg")
    

    
    
    
    
    
    
    
    