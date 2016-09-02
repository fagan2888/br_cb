# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 11:10:44 2016

@author: leicui

content: blackrock project
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from dateutil import relativedelta as rdelta

plt.style.use("ggplot")

FOREIGN_BOND_TYPE_CODE = ('AL', 'AR', 'BD', 'DA', 'DR', 'GA','KG', 'KA', 'MP', 'MA', 'MT', 'NA', 'RB', 'SA', 'SI', 'SO', 'YA')

#change the root directory to your own
ROOTDIR = "/Users/leicui/blackrock_data/figures/new/"


#his_df = pd.read_excel("/Users/leicui/blackrock_data/bond issuance excluding domestic market.xlsx",\
#                         sheetname = "Sheet1")

#since16_df = pd.read_excel("/Users/leicui/blackrock_data/all IG issuance since Jan 2016.xlsx", \
#                            sheetname = "Request 3")

#test_df = since16_df[since16_df['Bond\nType\nCode'].isin(FOREIGN_BOND_TYPE_CODE)]
 
"""
['Unnamed:0',
 'IssueDate',
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
 'CurrAbbrev']
"""

def dateStamp2datetime(DateSeries):
    date_ls = []
    
    for date in DateSeries:
        try:
            date_ls.append(date.to_datetime())
        except:
            date_ls.append("Perpuity")
        
    return date_ls
    
#calculate number of issuance and notional amount each time period
def issueNum_notional(df, postfix,date_col, notional_col):
    if notional_col not in list(df):
        raise Exception(notional_col +  " is not in the dataframe!")
    
    grouped_year = df.groupby([date_col])
    
    issueNum_ls = []
    notional_ls = []
    key_ls = []
    
    for key, group in grouped_year:
        issueNum_ls.append(len(group[notional_col]))
        notional_ls.append(group[notional_col].sum())
        key_ls.append(str(key))
    
    return_dict = {"Issue Num " + postfix: issueNum_ls, "Notional " + postfix: notional_ls}
    return_df = pd.DataFrame(return_dict, index = key_ls)
    
    return return_df
    
#plot number of issuance and notional amount each time period
def plotissueNum_notional(df, bar_cols, line_cols, filename):
    #fig = plt.figure(figsize = (18, 12))
    
    ax = df[bar_cols].plot(kind = 'bar', use_index = True)
    ax.set_ylabel("Total notional amount (mil)")
    ax.legend(bar_cols, loc = 0, fontsize = 8)
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
    ax2 = ax.twinx()
    
    ax2.plot(ax.get_xticks(),df[line_cols].values, linestyle='-', marker='o', linewidth=2.0)
    ax2.set_ylabel("Number of issuance")
    ax2.legend(line_cols,loc = 0, fontsize = 8)
    ax2.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
    
    fig = ax.get_figure()
    fig.savefig(ROOTDIR + filename, format = "jpg", dpi = 150)
    fig.clear()
    
        
    
#plot number of issuance each year according to split type
def notionalAmountByYearPlot(df, date_col, splitType, notionalType, filename, top = None):
    grouped_year = df.groupby([date_col])
    i= 1
    fig = plt.figure(figsize = (24, 24))
    
    for k, group in grouped_year:
        subgroups = group.groupby([splitType])
        amount_ls = []
        type_ls = []
        
        for subkey, subgroup in subgroups:
            type_ls.append(subkey)
            amount_ls.append(subgroup[notionalType].sum())
            
        amount_sr = pd.Series(amount_ls, index = type_ls)

        if top != None:
            amount_sr = amount_sr.order(ascending = False)
            subsum = amount_sr[(top + 1):].sum()
            amount_sr = amount_sr[:(top + 1)].append(pd.Series([subsum], index = ["Others"]))
    
            
        
        ax = fig.add_subplot(3, 3, i)
        y_pos = np.arange(len(amount_sr.index))
        rects = ax.bar(y_pos, amount_sr.values, align='center')
        ax.set_xticks(y_pos)
        ax.set_xticklabels(amount_sr.index)
        ax.set_ylabel(notionalType)
        ax.set_title("year " + str(k))
        i+=1
        
            #add label to each bar
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., height, '%d' % int(height),ha='center', va='bottom')
       
    fig.savefig(ROOTDIR + filename, format = "jpg", dpi = 200)
    fig.clear()
        

#plot notional amount of issuance each year according to split type
def numIssueByYearBar(df, date_col, splitType, filename, top = None):
    
    grouped_year = df.groupby([date_col])
    i= 1
    fig = plt.figure(figsize = (24, 24))
    
    for k, group in grouped_year:
        if top != None:
            type_count_df = group[splitType].value_counts().order(ascending = False)
            subsum = type_count_df[(top + 1):].sum()
            type_count_df = type_count_df[:(top + 1)].append(pd.Series([subsum], index = ["Others"]))
        else:
            type_count_df = group[splitType].value_counts()            
        
        ax = fig.add_subplot(3, 3, i)
        type_list = list(type_count_df.index)
        y_pos = np.arange(len(type_list))
        rects = ax.bar(y_pos, type_count_df.values, align='center')
        ax.set_xticks(y_pos)
        ax.set_xticklabels(type_list)
        ax.set_ylabel("Number of issuance")
        ax.set_title("year " + str(k))
        i+=1
        
        #add label to each bar
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., height, '%d' % int(height),ha='center', va='bottom')
        
    fig.savefig(ROOTDIR + filename, format = "jpg", dpi = 200)
    fig.clear()
    
def numIssueByYearPie(df, date_col, splitType, top, filename, col = 3, row = 3):
    grouped_year = df.groupby([date_col])
    i = 1
    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral', "pink", 'red', "green"]
    fig = plt.figure(figsize = (8*col, 8*row))
    for k, group in grouped_year:
        type_count_df = group[splitType].value_counts().order(ascending = False)
        subsum = type_count_df[(top + 1):].sum()
        type_count_df = type_count_df[:(top+1)].append(pd.Series([subsum], index = ["others"]))
        ax = fig.add_subplot(row, col, i)
        ax.pie(type_count_df.values, labels = type_count_df.index,  autopct='%1.1f%%', colors = colors)
        ax.set_title("year " + str(k))
        i+=1
    
    fig.savefig(ROOTDIR + filename, format = "jpg", dpi = 200)
    fig.clear()
    
    

#calculate term of the bonds accroding to issue_date and maturity date
def calterm(df, issue_date, maturity_date):
    timedelta_ls = []
    
    for mat, issue in zip(df[maturity_date], df[issue_date]):
        try:
            timedelta_ls.append(rdelta.relativedelta(mat, issue))
        except:
            timedelta_ls.append(None)
    
        
    year_diff_ls = []
        
    for timedelta in timedelta_ls:
        try:
            year_diff_ls.append(timedelta.years + float(timedelta.months/12.0) + float(timedelta.days/365.0))
        except:
            year_diff_ls.append(None)
            
    return year_diff_ls
            
    
#plot histogram each year according to class_col
def plotHistogram(df, date_col, class_col, filename, *argv):
    grouped_year = df.groupby([date_col])
    i = 1
    fig = plt.figure(figsize = (24,24))
    
    for k, group in grouped_year:
        group.index = np.arange(len(group[date_col]))
        
        ax = fig.add_subplot(3,3, i)
        ax.hist(group[class_col].dropna(how="any"), bins = 10)
        ax.set_xlabel(class_col)
        ax.set_title("year " + str(k))
        i += 1
            
    fig.savefig(ROOTDIR + filename, format = "jpg", dpi = 200)
    fig.clear()
        
def cleaningData(filename):
    cleaned_df = pd.read_csv("/Users/leicui/blackrock_data/" + filename, sep = ',', parse_dates = True, infer_datetime_format=True)    
    
    #remove '\n' '\r' in the column names
    rawname_ls = list(cleaned_df)
    name_ls = []
   
    for name in rawname_ls:
        name = name.replace('\r','',20)
        name = name.replace('\n','',20)
        name = name.replace(' ','', 20)
        name_ls.append(name)
        
    cleaned_df.columns = name_ls
    #del cleaned_df['Unnamed:0']
 
    #cleaned_df = cleaned_df.ix[cleaned_df["Foreign Issue Flag(eg Yankee)(Y/N)"] == "Yes", ]
    #convert IsssueDate and Maturity to datetime type
    
    cleaned_df["IssueDate"] = pd.to_datetime(cleaned_df["IssueDate"], infer_datetime_format = True)
    cleaned_df["IssueDate"] = dateStamp2datetime(cleaned_df["IssueDate"])
    cleaned_df = cleaned_df[cleaned_df.Maturity != "2013-30"]
    #temp1_df = cleaned_df[(cleaned_df["Maturity"] != 'n/a') & ( cleaned_df["Maturity"] != 'Perpet.')]
    cleaned_df = cleaned_df[~cleaned_df["Maturity"].isin(['n/a', 'Perpet.', 'NaT'])]
    cleaned_df["Maturity"] = pd.to_datetime(cleaned_df["Maturity"], infer_datetime_format=True)
    cleaned_df["Maturity"] = dateStamp2datetime(cleaned_df["Maturity"])
    
    #cleaned_df = temp1_df.append(temp2_df, ignore_index = True)
        
    #cleaned_df["PrincipalAmountIn Currency(mil)"] = [float(notional) for notional in cleaned_df["PrincipalAmountIn Currency(mil)"]]
   
    cleaned_df["Issue_year"] = cleaned_df["IssueDate"].dt.year
    cleaned_df["Issue_month"] = cleaned_df["IssueDate"].dt.month
    
    #convert the wrong Maturity, some maturity with only 2 digits for year are converted to 19** by excel.
    cleaned_df['Maturity_year'] = cleaned_df.Maturity.dt.year
    cleaned_df['Maturity_month'] = cleaned_df.Maturity.dt.month
    cleaned_df['Maturity_day'] = cleaned_df.Maturity.dt.day
    
    #cleaned_df.loc[cleaned_df.Maturity_year < 2000, 'Maturity_year'] = cleaned_df.loc[cleaned_df.Maturity_year < 2000, 'Maturity_year'] + 100
    year_ls = []

    for year in cleaned_df.Maturity_year:
        if year < 2000.0:
            year_ls.append(year + 100)
        else:
            year_ls.append(year)
            
    cleaned_df['Maturity_year'] = year_ls
    
    mat_ls = [dt.datetime(year = int(yr), month = int(mn), day = int(dy)) for yr, mn, dy in\
              zip(cleaned_df.Maturity_year, cleaned_df.Maturity_month, cleaned_df.Maturity_day)]
    cleaned_df.Maturity = mat_ls
    cleaned_df["bond_terms"] = calterm(cleaned_df,'IssueDate', 'Maturity')
    cleaned_df = cleaned_df[cleaned_df.bond_terms > 0]
    
    cleaned_df =  cleaned_df.drop(['DenominationsCurrency', 'Maturity_year', 'Maturity_month', 'Maturity_day'], axis = 1)
    #clean issue type
        
    cleaned_df = cleaned_df[~cleaned_df.IssueType.isnull()]
    issue_type_ls = [isType.replace('\r', '', 10) for isType in cleaned_df.IssueType] 
    cleaned_df['IssueType'] = issue_type_ls

    cleaned_df.to_csv("/Users/leicui/blackrock_data/cleaned.csv", index = False)
    
    #split data to SSA and corporate bonds
    SSA_df = cleaned_df[cleaned_df['IssueType'] == 'AS']
    SSA_df.index = np.arange(len(SSA_df.Issue_month))
   
    
    corporate_ls = ['IG',  'EMIG', 'FC', 'HY', 'EM']
    corporate_df = cleaned_df[cleaned_df["IssueType"].isin(corporate_ls)]
    corporate_df.index = np.arange(len(corporate_df.Issue_month))
    SSA_df.to_csv("/Users/leicui/blackrock_data/SSA.csv", index = False)
    corporate_df.to_csv("/Users/leicui/blackrock_data/corp.csv", index = False)
    
    


if __name__ == '__main__':
    
    #only select data with foreign bond flag to be yes
    #cleaned_df = pd.read_csv("/Users/leicui/blackrock_data/All cross-border & foreign flagged v_7 nation.csv", sep = ',', parse_dates = True, infer_datetime_format=True)    
    
    cleaningData("All cross-border & foreign flagged v_7 nation.csv")
    
    
    
    #test the function to draw the figures    
    '''
    #number of issuance each year and total notional amount each year
    issueNum_SSA_df = issueNum_notional(SSA_df, "SSA","Issue_year", 'PrincipalAmount($ mil)')
    issueNum_corp_df = issueNum_notional(corporate_df, "corp", "Issue_year", 'PrincipalAmount($ mil)')
    
    issueNum_df = pd.concat([issueNum_SSA_df,issueNum_corp_df], axis = 1)
    plotissueNum_notional(issueNum_df, ['Notional SSA', 'Notional corp'], ['Issue Num SSA', 'Issue Num corp'], "issueNum_notional.jpg")
    

    #number of issuance each year in different market
    numIssueByYearBar(SSA_df[SSA_df.BondTypeCode.notnull()], "Issue_year", "BondTypeCode", "numIssueByYear_SSA.jpg")
    numIssueByYearBar(corporate_df[corporate_df.BondTypeCode.notnull()], "Issue_year", "BondTypeCode", "numIssueByYear_corp.jpg")
    
    #number of issuance for each ratings
    numIssueByYearBar(SSA_df, "Issue_year","Stan-dard&Poor's", "ratings_SSA.jpg")
    numIssueByYearBar(corporate_df, "Issue_year","Stan-dard&Poor's", "ratings_corp.jpg")
    
    #notional amount for each rating category each year    
    notionalAmountByYearPlot(SSA_df, "Issue_year", "Stan-dard&Poor's", 'PrincipalAmount($ mil)',"notionalamount_SSA.jpg")
    notionalAmountByYearPlot(corporate_df, "Issue_year", "Stan-dard&Poor's", 'PrincipalAmount($ mil)',"notionalamount_corp.jpg")

    # distribution of maturity type each year
    plotHistogram(SSA_df[SSA_df.bond_terms >  0], "Issue_year", 'bond_terms', "Maturity_SSA.jpg")
    plotHistogram(corporate_df[corporate_df.bond_terms > 0], "Issue_year", 'bond_terms', "Maturity_corp.jpg")
    
    #calculate the issue frequecy per month 
    plotHistogram(SSA_df, "Issue_year", "Issue_month", "Issue_frequency_SSA.jpg")
    plotHistogram(corporate_df, "Issue_year", "Issue_month", "Issue_frequency_corp.jpg")
    
    #corporates or SSA in which country issue cross-border bonds most
    numIssueByYearPie(SSA_df, "Issue_year", 'Domicile', 5,"Issue_nation_SSA.jpg")
    numIssueByYearPie(corporate_df, "Issue_year", 'Domicile', 5, "Issue_nation_corp.jpg")
    '''

    
    
    
    
    
    
    
    
    
    
    
    


