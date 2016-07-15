# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 11:10:44 2016

@author: leicui

content: blackrock project
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dateutil import relativedelta as rdelta

plt.style.use("ggplot")

FOREIGN_BOND_TYPE_CODE = ('AL', 'AR', 'BD', 'DA', 'DR', 'GA','KG', 'KA', 'MP', 'MA', 'MT', 'NA', 'RB', 'SA', 'SI', 'SO', 'YA')
ROOTDIR = "/Users/leicui/blackrock_data/figures/"
#his_df = pd.read_excel("/Users/leicui/blackrock_data/bond issuance excluding domestic market.xlsx",\
#                         sheetname = "Sheet1")

#since16_df = pd.read_excel("/Users/leicui/blackrock_data/all IG issuance since Jan 2016.xlsx", \
#                            sheetname = "Request 3")

#test_df = since16_df[since16_df['Bond\nType\nCode'].isin(FOREIGN_BOND_TYPE_CODE)]
 
"""
['Issue Date',
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
 'Domicile']
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
def notionalAmountByYearPlot(df, date_col, splitType, notionalType, filename):
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
        
        ax = fig.add_subplot(3, 3, i)
        y_pos = np.arange(len(type_ls))
        rects = ax.bar(y_pos, amount_ls, align='center')
        ax.set_xticks(y_pos)
        ax.set_xticklabels(type_ls)
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
def numIssueByYearBar(df, date_col, splitType, filename):
    
    grouped_year = df.groupby([date_col])
    i= 1
    fig = plt.figure(figsize = (24, 24))
    
    for k, group in grouped_year:
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
        


if __name__ == '__main__':
    #cleaned_df = pd.read_excel("/Users/leicui/blackrock_data/All Cross Border Issuance all since 2008 with Foreign Bond Type.xlsx", \
    #                            sheetname = "Request 3",parse_dates=True ,infer_datetime_format=True)
    
    #raw1_df = pd.read_csv("/Users/leicui/blackrock_data/2008-2009 cleaned.csv", sep = ',', parse_dates = True, infer_datetime_format=True) 
    #del raw1_df['Unnamed: 27']
    #raw2_df = pd.read_csv("/Users/leicui/blackrock_data/2010-2012 cleaned.csv", sep = ',', parse_dates = True, infer_datetime_format=True)     
    #raw3_df = pd.read_csv("/Users/leicui/blackrock_data/2013-2016 cleaned.csv", sep = ',', parse_dates = True, infer_datetime_format=True)
    #del raw3_df['Unnamed: 27']   

    #cleaned_df = raw1_df.append(raw2_df, ignore_index = True)
    #cleaned_df = cleaned_df.append(raw3_df, ignore_index = True)
    

    #only select data with foreign bond flag to be yes
    cleaned_df = pd.read_csv("/Users/leicui/blackrock_data/All cross-border & foreign flagged.csv", sep = ',', parse_dates = True, infer_datetime_format=True)    
      
    #cleaned_df = cleaned_df.ix[cleaned_df["Foreign Issue Flag(eg Yankee)(Y/N)"] == "Yes", ]
    #convert IsssueDate and Maturity to datetime type
    
    cleaned_df["IssueDate"] = pd.to_datetime(cleaned_df["IssueDate"], infer_datetime_format = True)
    cleaned_df["IssueDate"] = dateStamp2datetime(cleaned_df["IssueDate"])
    cleaned_df = cleaned_df[cleaned_df.Maturity != "2013-30"]
    temp1_df = cleaned_df[(cleaned_df["Maturity"] != 'n/a') & ( cleaned_df["Maturity"] != 'Perpet.')]
    temp2_df = cleaned_df[cleaned_df["IssueType2"].isin(['n/a', 'Perpet.'])]
    temp1_df["Maturity"] = pd.to_datetime(temp1_df["Maturity"], infer_datetime_format=True)
    temp1_df["Maturity"] = dateStamp2datetime(temp1_df["Maturity"])
    cleaned_df = temp1_df.append(temp2_df, ignore_index = True)
    
    cleaned_df["PrincipalAmountIn Currency(mil)"] = [float(notional) for notional in cleaned_df["PrincipalAmountIn Currency(mil)"]]
    
    
    
    cleaned_df["Issue_year"] = cleaned_df["IssueDate"].dt.year
    cleaned_df["Issue_month"] = cleaned_df["IssueDate"].dt.month
    cleaned_df["bond_terms"] = calterm(cleaned_df,'IssueDate', 'Maturity')
    
    
    

    #split data to SSA and corporate bonds
    SSA_df = cleaned_df[cleaned_df['IssueType2'] == 'AS']
    SSA_df.index = np.arange(len(SSA_df.Issue_month))
    corporate_ls = ['IG',  'EMIG', 'FC', 'HY', 'EM']
    corporate_df = cleaned_df[cleaned_df["IssueType2"].isin(corporate_ls)]
    corporate_df.index = np.arange(len(corporate_df.Issue_month))
    
    #number of issuance each year and total notional amount each year
    issueNum_SSA_df = issueNum_notional(SSA_df, "SSA","Issue_year", 'PrincipalAmount($ mil)')
    issueNum_corp_df = issueNum_notional(corporate_df, "corp", "Issue_year", 'PrincipalAmount($ mil)')
    
    issueNum_df = pd.concat([issueNum_SSA_df,issueNum_corp_df], axis = 1)
    plotissueNum_notional(issueNum_df, ['Notional SSA', 'Notional corp'], ['Issue Num SSA', 'Issue Num corp'], "issueNum_notional.jpg")
    
    '''
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
    '''
    #corporates or SSA in which country issue cross-border bonds most
    numIssueByYearPie(SSA_df, "Issue_year", 'Domicile', 5,"Issue_nation_SSA.jpg")
    numIssueByYearPie(corporate_df, "Issue_year", 'Domicile', 5, "Issue_nation_corp.jpg")
    

    
    
    
    
    
    
    
    
    
    
    
    


