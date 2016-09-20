import pandas as pd 
import numpy as np
import sys
import data_cleaning as dc
import importlib
pd.options.mode.chained_assignment = None  # z='warn'

dc = importlib.reload(dc)

def Read_Data(path, data_path, filename_data, filename_domicile, filename_euro_list, 
              filename_curr_codes, filename_ratings, rating_cols_df, rating_cols_dict):
    ### Read main data file & dictionary files into dfs
    df = pd.read_csv(path + filename_data, low_memory=False)

    # remove all \r and \n from dataframe column names
    df.columns = dc.Remove_Chars_From_Cols(df.columns)

    # Read dictionaries necessary to identify bonds by their characteristics
    df_domicile = pd.read_csv(path + filename_domicile)
    df_euro_list = pd.read_csv(path + filename_euro_list)
    df_curr_codes = pd.read_csv(path + filename_curr_codes)
    df_ratings_dict = pd.read_csv(path + filename_ratings)

    return df, df_domicile, df_euro_list, df_curr_codes, df_ratings_dict

def Clean_And_Parse_Data(df, df_domicile, df_euro_list, df_curr_codes, df_ratings_dict):
    ### Clean and format columns of main data frame
    # Convert all date based cols to datetime objects to help with indexing
    df = dc.Clean_Time_Cols(df)

    # format domicile, curr, and rating columns based on external dicts above
    df['Domicile'] = dc.Convert_Dom_Codes(df, df_domicile)
    curr_codes = dc.Parse_Curr_Codes(df, df_curr_codes)

    df['Currency'] = dc.Get_Curr_Names(curr_codes, df_curr_codes, df_euro_list)
    df.dropna(subset=['Currency'], inplace=True)    # removing any empty currencies
    df = df[df['Currency'] != np.nan]               # removing any empty currencies

    ### Averaging ratings
    # Already done in the 'Filtered' data set to save time
    #df['Overall Rating S&P'] = dc.Average_Ratings(df, df_ratings_dict, 
    #                                           rating_cols_df, rating_cols_dict)

    return df

def Compare_Country_Cols(df, df_euro_list):
    ### Compare issuance currency and marketplace with NATION
    
    ## fix specific naming problems with currencies, nations, and marketplaces
    df = dc.Naming_Fixes(df)

    df_cb_curr_nat = dc.Compare_Curr_Nation(df, df_euro_list)
    df_cb_mkt_nat = dc.Compare_Nation_Mktplc(df, df_euro_list)
    df_cb_mkt_nat = dc.Remove_Curr_Filter_From_Mkt_Filter(df_cb_mkt_nat, df_euro_list)

    return (df_cb_curr_nat, df_cb_mkt_nat)

def Filter_CB_and_SSA(df_cb_curr_nat, df_cb_dom_nat, outfile_nation):

    #### Nation
    df_nation = dc.Flag_vs_Grouping(df, df_cb_curr_nat, df_cb_dom_nat, 
                                 df_euro_list, outfile_nation)

    ## For some reason filters wouldn't pick up the us issue. Added this conditional.
    df_nation = df_nation.drop((df_nation['Nation']=='us') & \
                               (df_nation['Currency']=='us') & \
                               (df_nation['Marketplace']=='us'))

    df_nation_corp, df_nation_ssa = dc.Filter_Out_SSA(df_nation)
    
    currency_dict = {'australia': 'australia', \
                     'canada': 'canada', \
                     'japan': 'japanese', \
                     'united kingdom': 'uk', \
                     'united states': 'us'}

    df_nation_corp['Nation'] = [nat if nat not in currency_dict.keys() else currency_dict[nat] for nat in df_nation_corp['Nation'] ]
    df_nation_ssa['Nation'] =  [nat if nat not in currency_dict.keys() else currency_dict[nat] for nat in df_nation_ssa['Nation'] ]   

    return df_nation_corp, df_nation_ssa

if __name__ == '__main__':
    
    ### Specify paths to read data files
    #path = '/Users/leicui/blackrock_data/'     # modify to own path for running
    #data_path = '/Users/leicui/br_cb/Data/'    # modify to own path for running
    #dropbox_path = '/Users/leicui/Dropbox (blackrock project)/blackrock project/'

    path = r'C:\Users\Alex\Desktop\\br_cb_Data\\'   # modify to own path for running
    data_path = r'C:\Users\Alex\Desktop\\br_cb\Data\\'  # modify to own path for running

    ### Specify file names of dictionaries to be used 
    #filename_data = 'Filtered with Nations 2007-2016.csv'  # has average ratings
    filename_data = '2007-2016 DATA with ISIN.csv' # doesn't have
    filename_domicile = 'domicile_dictionary.csv'
    filename_euro_list = 'Euro_countries_list.csv'
    filename_curr_codes = 'currency_codes_dict.csv'
    filename_ratings = 'ratings_dict.csv'
    rating_cols_df = ['FitchRating', 'MoodyRating', 'Stan-dard &Poor\'sRating']
    rating_cols_dict = ['Fitch', 'Moody\'s', 'S&P']

    outfile_nation = 'All cross-border & foreign flagged v_10 nation.csv'
    
    # Reading data
    df, df_domicile, df_euro_list, df_curr_codes, df_ratings_dict = \
            Read_Data(path, data_path, filename_data, filename_domicile, filename_euro_list, 
              filename_curr_codes, filename_ratings, rating_cols_df, rating_cols_dict)

    # Parsing columns
    #df = Clean_And_Parse_Data(df, df_domicile, df_euro_list, df_curr_codes, df_ratings_dict)

    #df.to_csv(path + '2007-2016 data with ratings.csv')

    df = pd.read_csv(path + '2007-2016 data with ratings.csv')

    # Comparing country, mktplace, and currencies
    df_cb_curr_nat, df_cb_dom_nat = \
        Compare_Country_Cols(df, df_euro_list)

    # separating cross-border by ssa and corporate
    df_nation_corp, df_nation_ssa = \
        Filter_CB_and_SSA(df_cb_curr_nat, df_cb_dom_nat, outfile_nation)
    
    sys.exit()

    #to accelarate the data generating process, could use All cross-border & foreign flagged v_9 nation.csv directly    
    '''
    df = pd.read_csv(path + 'All cross-border & foreign flagged v_9 nation.csv')
    df.Currency = [str.lower(cur) for cur in df.Currency]
    df.Nation = [str.lower(na) for na in df.Nation]
    df_nation_ssa = df[df['IssueType'] == 'AS']
    df_nation_ssa.index = np.arange(len(df_nation_ssa.Issue_month))
    corporate_ls = ['IG',  'EMIG', 'FC', 'HY', 'EM']
    df_nation_corp = df[df["IssueType"].isin(corporate_ls)]
    df_nation_corp.index = np.arange(len(df_nation_corp.Issue_month))
    
    
    currency_dict = {'australia': 'australia', \
                     'canada': 'canada', \
                     'japan': 'japanese', \
                     'united kingdom': 'uk', \
                     'u.s.': 'us'}

    df_nation_corp['Nation'] = [nat if nat not in currency_dict.keys() else currency_dict[nat] for nat in df_nation_corp['Nation'] ]
    df_nation_ssa['Nation'] =  [nat if nat not in currency_dict.keys() else currency_dict[nat] for nat in df_nation_ssa['Nation'] ]   
    '''
        
    
    #get the notional amont series for 7 issue market 
    dic_notional_corp, dic_notional_SSA = dc.generate_notional_time_series(df_nation_corp, df_nation_ssa)
    
        
    Currency_ls = ['australia', 'canada', 'euro', 'japanese', 'sweden', 'uk', 'us']    
    
    dict_reg_corp = dc.get_reg_dict(Currency_ls, dic_notional_corp, dropbox_path)
    dict_reg_ssa = dc.get_reg_dict(Currency_ls, dic_notional_SSA, dropbox_path)
    
    #combine SSA and corp data and calculate spread (interest spread, butterfly spread, curve spread)
    df_reg_wgt, df_reg_usd = dc.regression_data2(dict_reg_corp, dict_reg_ssa, Currency_ls, dropbox_path)
    
    df_reg_wgt.to_csv('regression_data_combined.csv')
    df_reg_usd.to_csv('regression_data_combined_proxy.csv')
   
    
    
    
    
    
    
    
        
    
