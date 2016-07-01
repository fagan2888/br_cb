# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 11:10:44 2016

@author: leicui

content: blackrock project
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
#plot number of issuance each year according to split type
def notionalAmountByYearPlot(df, date_col, splitType, notionalType, filename):
    grouped_year = df.groupby([date_col])
    i= 1
    fig = plt.figure(figsize = (24, 8))
    
    for k, group in grouped_year:
        subgroups = group.groupby([splitType])
        amount_ls = []
        type_ls = []
        
        for subkey, subgroup in subgroups:
            type_ls.append(subkey)
            amount_ls.append(subgroup[notionalType].sum())
                    
        ax = fig.add_subplot(2, 5, i)
        y_pos = np.arange(len(type_ls))
        rects = ax.bar(y_pos, amount_ls, align='center')
        ax.set_xticks(y_pos)
        ax.set_xticklabels(type_ls)
        ax.set_title("year " + str(k))
        i+=1
        
        #add label to each bar
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., height, '%d' % int(height),ha='center', va='bottom')
        
    fig.savefig(filename, format = "jpg", dpi = 200)
    fig.clear()
        

#plot notional amount of issuance each year according to split type
def numIssueByYearPlot(df, date_col, splitType, filename):
    
    grouped_year = df.groupby([date_col])
    i= 1
    fig = plt.figure(figsize = (24, 8))
    
    for k, group in grouped_year:
        type_count_df = group[splitType].value_counts()
        ax = fig.add_subplot(2, 5, i)
        type_list = list(type_count_df.index)
        y_pos = np.arange(len(type_list))
        rects = ax.bar(y_pos, type_count_df.values, align='center')
        ax.set_xticks(y_pos)
        ax.set_xticklabels(type_list)
        ax.set_title("year " + str(k))
        i+=1
        
        #add label to each bar
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., height, '%d' % int(height),ha='center', va='bottom')
        
    fig.savefig(filename, format = "jpg", dpi = 200)
    fig.clear()


if __name__ == '__main__':
    cleaned_df = pd.read_excel("/Users/leicui/blackrock_data/All Cross Border Issuance all since 2008 with Foreign Bond Type.xlsx", \
                                sheetname = "Request 3")
    
    cleaned_df["Issue_year"] = cleaned_df["Issue\nDate"].dt.year
    cleaned_df["Issue_month"] = cleaned_df["Issue\nDate"].dt.month
    
    #split data to SSA and corporate bonds
    SSA_df = cleaned_df[cleaned_df['Issue\nType\nDescription'] == 'Agency, Supranational, Sovereign']
    corporate_ls = ['Investment Grade Corporate', 'Emerging Market Corporate\nInvestment Grade Corporate','High Yield Corporate', 'Federal Credit Agency']
    corporate_df = cleaned_df[cleaned_df["Issue\nType\nDescription"].isin(corporate_ls)]
    
    #number of issuance each year in different market
    #numIssueByYearPlot(SSA_df, "Issue_year", "Bond\nType\nCode", "numIssueByYear_SSA.jpg")
    #numIssueByYearPlot(corporate_df, "Issue_year", "Bond\nType\nCode", "numIssueByYear_corp.jpg")
    
    #number of issuance for each ratings
    numIssueByYearPlot(SSA_df, "Issue_year","Stan-\ndard\n &\nPoor's\nRating", "ratings_SSA.jpg")
    numIssueByYearPlot(corporate_df, "Issue_year","Stan-\ndard\n &\nPoor's\nRating", "ratings_corp.jpg")
    
    
    notionalAmountByYearPlot(SSA_df, "Issue_year", "Stan-\ndard\n &\nPoor's\nRating", 'Principal\nAmount\n($ mil)',"notionalamount_SSA.jpg")
    notionalAmountByYearPlot(corporate_df, "Issue_year", "Stan-\ndard\n &\nPoor's\nRating", 'Principal\nAmount\n($ mil)',"notionalamount_corp.jpg")
    
    
    
    
    


