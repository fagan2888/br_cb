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

#his_df = pd.read_excel("/Users/leicui/blackrock_data/bond issuance excluding domestic market.xlsx",\
#                         sheetname = "Sheet1")

#since16_df = pd.read_excel("/Users/leicui/blackrock_data/all IG issuance since Jan 2016.xlsx", \
#                            sheetname = "Request 3")

#test_df = since16_df[since16_df['Bond\nType\nCode'].isin(FOREIGN_BOND_TYPE_CODE)]
 
"""
column names for cleaned_df:
'Issuer',
 'Issue\nType',
 'Issue\nType\nDescription',
 'Bond\nType\nCode',
 'Bond Type',
 'Business Description',
 'Nation',
 'Ticker\nSymbol',
 'Industry',
 'Issue\nDate',
 'Maturity',
 'Denominations\nCurrency',
 'Coupon\n (%)',
 'Offer\nYield\nto Maturity\n (%)',
 "Stan-\ndard\n &\nPoor's\nRating",
 'Prncpl Amt \nin Curr of \nIss - in this\nMkt (mil)',
 'Principal\nAmount\nIn Currency\n(mil)',
 'Principal\nAmount\n($ mil)',
 'Principal \nAmt - in \nthis Mkt \n(euro mil)' 
"""
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
    fig = plt.figure(figsize = (18, 12))
    
    ax = df[bar_cols].plot(kind = 'bar', use_index = True)
    ax.set_ylabel("Total notional amount (mil)")
    ax.legend(bar_cols, loc = 0, fontsize = 8)
    ax2 = ax.twinx()
    
    ax2.plot(ax.get_xticks(),df[line_cols].values, linestyle='-', marker='o', linewidth=2.0)
    ax2.set_ylabel("Number of issuance")
    ax2.legend(line_cols,loc = 0, fontsize = 8)
    fig.savefig("/Users/leicui/blackrock_data/" + filename, format = "jpg", dpi = 200)
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
        
    fig.savefig("/Users/leicui/blackrock_data/" + filename, format = "jpg", dpi = 200)
    fig.clear()
        

#plot notional amount of issuance each year according to split type
def numIssueByYearPlot(df, date_col, splitType, filename):
    
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
        
    fig.savefig("/Users/leicui/blackrock_data/" + filename, format = "jpg", dpi = 200)
    fig.clear()
    
def maturityByYearPlot(df, date_col, issue_date, maturity_date,filename):
    grouped_year = df.groupby([date_col])
    i = 1
    fig = plt.figure(figsize = (24,24))
    
    for k, group in grouped_year:
        group.index = np.arange(len(group[date_col]))
        timedelta_ls = []
        
        for mat, issue in zip(group[maturity_date], group[issue_date]):
            try:
                timedelta_ls.append(rdelta.relativedelta(mat, issue.to_datetime()))
            except:
                continue
        
        
        year_diff = [timedelta.years + float(timedelta.months/12.0) + float(timedelta.days/365.0) for timedelta in timedelta_ls]
        ax = fig.add_subplot(3,3, i)
        ax.hist(year_diff, bins = [0,5,10,15,20,25,30])
        ax.set_xlabel("bond terms")
        ax.set_title("year " + str(k))
        i += 1
            
    fig.savefig("/Users/leicui/blackrock_data/" + filename, format = "jpg", dpi = 200)
    fig.clear()
        


if __name__ == '__main__':
    cleaned_df = pd.read_excel("/Users/leicui/blackrock_data/All Cross Border Issuance all since 2008 with Foreign Bond Type.xlsx", \
                                sheetname = "Request 3",parse_dates=True ,infer_datetime_format=True)
    
    cleaned_df["Issue_year"] = cleaned_df["Issue\nDate"].dt.year
    cleaned_df["Issue_month"] = cleaned_df["Issue\nDate"].dt.month
    
      
    
    #split data to SSA and corporate bonds
    SSA_df = cleaned_df[cleaned_df['Issue\nType\nDescription'] == 'Agency, Supranational, Sovereign']
    SSA_df.index = np.arange(len(SSA_df.Issue_month))
    corporate_ls = ['Investment Grade Corporate', 'Emerging Market Corporate\nInvestment Grade Corporate','High Yield Corporate', 'Federal Credit Agency']
    corporate_df = cleaned_df[cleaned_df["Issue\nType\nDescription"].isin(corporate_ls)]
    corporate_df.index = np.arange(len(corporate_df.Issue_month))
    
    #number of issuance each year and total notional amount each year
    issueNum_SSA_df = issueNum_notional(SSA_df, "SSA","Issue_year", "Principal\nAmount\n($ mil)")
    issueNum_corp_df = issueNum_notional(corporate_df, "corp", "Issue_year", "Principal\nAmount\n($ mil)")
    
    issueNum_df = pd.concat([issueNum_SSA_df,issueNum_corp_df], axis = 1)
    plotissueNum_notional(issueNum_df, ['Notional SSA', 'Notional corp'], ['Issue Num SSA', 'Issue Num corp'], "issueNum_notional.jpg")
    
    """
    #number of issuance each year in different market
    numIssueByYearPlot(SSA_df, "Issue_year", "Bond\nType\nCode", "numIssueByYear_SSA.jpg")
    numIssueByYearPlot(corporate_df, "Issue_year", "Bond\nType\nCode", "numIssueByYear_corp.jpg")
    
    #number of issuance for each ratings
    numIssueByYearPlot(SSA_df, "Issue_year","Stan-\ndard\n &\nPoor's\nRating", "ratings_SSA.jpg")
    numIssueByYearPlot(corporate_df, "Issue_year","Stan-\ndard\n &\nPoor's\nRating", "ratings_corp.jpg")
    
    #notional amount for each rating category each year    
    notionalAmountByYearPlot(SSA_df, "Issue_year", "Stan-\ndard\n &\nPoor's\nRating", 'Principal\nAmount\n($ mil)',"notionalamount_SSA.jpg")
    notionalAmountByYearPlot(corporate_df, "Issue_year", "Stan-\ndard\n &\nPoor's\nRating", 'Principal\nAmount\n($ mil)',"notionalamount_corp.jpg")
    
    # distribution of maturity type each year
    maturityByYearPlot(SSA_df, "Issue_year", 'Issue\nDate', 'Maturity', "Maturity_SSA.jpg")
    maturityByYearPlot(corporate_df, "Issue_year", 'Issue\nDate', 'Maturity', "Maturity_corp.jpg")
    """
    
    
    
    


