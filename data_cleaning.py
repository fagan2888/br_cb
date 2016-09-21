import pandas as pd 
import numpy as np
from dateutil import relativedelta as rdelta
import time
import datetime
from pandas.tseries.offsets import *

   
CREDIT_DICT = {  'australia': 'AUD Australia Corporate A+, A, A- Spread Curve monthly.csv' , \
            'canada': 'CAD Canada Corporate A+, A, A- Spread Curve monthly.csv', \
            'euro': 'EUR Europe Corporate A+, A, A- Spread Curve monthly.csv',\
            'japanese': 'JPY Japan Corporate A+, A, A- Spread Curve monthly.csv',\
            'sweden': 'SEK Europe Corporate AA+ , AA , AA- Spread Curve monthly.csv',\
            'us': 'USD US Corporate A+, A, A- Spread Curve monthly.csv', \
                 'norway': 'NOK Europe Agency & Regionals Spread Curve monthly.csv',\
                 'new zealand': 'NZD New Zealand Financials AA+ , AA , AA- Spread Curve monthly.csv',\
                 'uk': 'GBP Europe Composite AA+ , AA , AA- Spread Curve monthly.csv'}

NATION_CURRENCY_DICT = {'australia': 'AUD', \
                        'uk': 'GBP', \
                        'sweden': 'SEK',  \
                        'canada': 'CAD', \
                        'norway': 'NOK', \
                        'japanese': 'JPY', \
                        'euro': 'EUR', \
                        'us': 'USD', \
                        'new zealand': 'NZD'}

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print ('%s function took %0.3f s' % (f.__name__, (time2-time1)*1.0))
        return ret
    return wrap

@timing
def Remove_Chars_From_Cols(cols):
    cols = [x.replace('\r', '') for x in cols]
    cols = [x.replace('\n', '') for x in cols]
    return cols    

@timing
def Clean_Time_Cols(df):
    """
        Convert all time based columns to pandas datetime objects.
        Remove all empty or mislabeled rows in each of these columns.
        Create three new columns of "Issue Year", "Issue month", and "bond_terms".
        Return cleaned dataframe.
    """
    iss_date_col = "IssueDate"
    iss_type_col = "IssueType"

    # Issue date data cleaning
    df[iss_date_col] = pd.to_datetime(df[iss_date_col], infer_datetime_format = True)
    df = df[~df["Maturity"].isin(['n/a', 'Perpet.', 'NaT', 'BAD DATE', '2013-30'])]
    df = df[~df[iss_type_col].isin(['n/a', 'Perpet.'])]

    df["Maturity"] = pd.to_datetime(df["Maturity"], infer_datetime_format=True, errors='coerce')
    df.dropna(subset=['Maturity'], inplace=True)

    df = Fix_Maturities(df)    # Converts all years from 1900's to 2000's

    # separate issue date into separate columns
    df["Issue_year"] = df[iss_date_col].dt.year
    df["Issue_month"] = df[iss_date_col].dt.month
    df["bond_terms"] = calterm(df, iss_date_col, 'Maturity')

    df = df[df['bond_terms'] > 0]

    return df

@timing
def Fix_Maturities(df):
    """
        Converts all maturities with years in the 1900's to 2000's. 
        Takes year modulus 100 and adds 2000 to it. For example, 
        1976 % 100 = 76. 76 + 2000 + 2076. 2076 is new year.
    """
    for i in range(df.shape[0]):
        try:
            new_date = pd.Timestamp(df['Maturity'].values[i]).to_pydatetime()
            if new_date.year < 2000:            
                new_date = new_date.replace(year = (new_date.year % 100) + 2000)
                df['Maturity'].values[i] = np.datetime64(new_date)
        except:
            df['Maturity'].values[i] = np.nan

    return df

@timing
def Naming_Fixes(df):
    df['Currency'] = [str(item).lower() for item in df['Currency']]
    df['Nation'] = [str(item).lower() for item in df['Nation']]
    df['Nation.1'] = [str(item).lower() for item in df['Nation.1']]
    df['Marketplace'] = [str(item).lower() for item in df['Marketplace']]
    df['Domicile'] = [str(item).lower() for item in df['Domicile']]

    ## US
    df['Nation'] = np.where(df['Nation'] == 'united states', 'us', df['Nation'])
    df['Domicile'] = np.where(df['Domicile'] == 'u.s.', 'us', df['Domicile'])
    df['Marketplace'] = np.where(df['Marketplace'] == 'u.s. public', 'us', df['Marketplace'])
    df['Marketplace'] = np.where(df['Marketplace'] == 'u.s. private', 'us', df['Marketplace'])

    ## China
    df['Currency'] = np.where(df['Currency']=='hong kong', 'china', df['Currency'])
    df['Nation'] = np.where(df['Nation']=='hong kong', 'china', df['Nation'])
    df['Marketplace'] = np.where(df['Marketplace']=='hong kong public', 'china', df['Marketplace'])
    df['Marketplace'] = np.where(df['Marketplace']=='hong kong private', 'china', df['Marketplace'])

    ## Czech
    df['Marketplace'] = np.where(df['Marketplace']=='czech republic pu', 'czech republic', df['Marketplace'])

    ## UK
    df['Nation'] = np.where(df['Nation']=='united kingdom', 'uk', df['Nation'])

    ## Thailand
    df['Nation'] = np.where(df['Nation']=='laos', 'thailand', df['Nation'])

    return df

@timing
def calterm(df, issue_date, maturity_date):
    """
        Calculate term of the bonds accroding to issue_date and maturity date.
    """
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

@timing
def Get_Curr_Names(curr_codes, df_curr_codes, df_euro_list):
    """
        Create a dictionary mapping of currency codes to country names from SDC
        currency codes list. Map every currency code from dataset to country name.
        Special case if country in euro, then currency name set to EURO.
    """
    dict_curr = df_curr_codes.set_index('Code')['Country'].to_dict()

    curr_name_arr = []
    miss_code = []
    for code in curr_codes:
        # append nan values to keep same size as original df
        if code == np.nan or str(code) == 'nan':
            curr_name_arr.append(np.nan)
        else:
            try:
                # check if currency issuer country is in euro
                # if it is set currency name to euro instead of issuer country
                curr_name = dict_curr[code]
                if curr_name in df_euro_list['Country'].values:
                    curr_name_arr.append('EURO')
                # else set currency name to issuing country name
                else:
                    curr_name_arr.append(curr_name)
            except:
                #print '--' + str(code) + '---'
                miss_code.append(code)
                pass

    # Make sure no missed country codes, otherwise print missed codes
    assert (len(miss_code) == 0), np.unique(miss_code)

    curr_name_np = np.array(curr_name_arr)

    return curr_name_np

@timing
def Parse_Curr_Codes(df, df_curr_codes):
    """ 
        Parse currency codes from prinicipal and currency in single column.
        format: [<prinicipal dollar amount i.e. (100.00)> <country code i.e. (BA)].
        Then assign the codes to countries by using the SDC currency dictionary.
    """
    dict_curr_codes = df_curr_codes.set_index('Code')['Country'].to_dict()

    # format: [<prinicipal dollar amount i.e. (100.00)> <country code i.e. (BA)]
    princ_col = 'Prncpl Amt w/Curr of Iss - in thisMkt (mil)'
    curr_princ_arr = df[princ_col].values
    curr_princ_arr = [str(x).lower() for x in curr_princ_arr]

    curr_code_arr = []

    split_arr = np.array([str.split(x) for x in curr_princ_arr])
    for item in split_arr:
        try:
            curr_code_arr.append(item[1])
        except:
            curr_code_arr.append(np.nan)

    # Make sure no missed country codes
    assert (len(curr_code_arr) == len(curr_princ_arr))

    return curr_code_arr

@timing
def Convert_Dom_Codes(df, df_domicile):
    """
        Define cross-border as differing nation and currency, of differing nation and 
        exchange location.
        Domicile nation code = country of issuance. 
        Convert Domicile Nation Code to the actual country name using df_domicile as dictionary.
    """
    dict_domicile = df_domicile.set_index('abbreviation')['name'].to_dict()
    
    domicile_col = 'DomicileNationCode'
    dom_code_arr = df[domicile_col].values
    dom_code_arr = [str(x).lower() for x in dom_code_arr]

    dom_name_arr = []
    miss_code = []
    for code in dom_code_arr:
        # append nan values to keep same size as original df
        if code == np.nan or code == 'nan':
            dom_name_arr.append(np.nan)
        else:
            try:
                dom_name_arr.append(dict_domicile[code])
            except:
                miss_code.append(code)
                pass

    # Make sure no missed country codes
    assert (len(miss_code) == 0), np.unique(miss_code)

    dom_name_np = np.array(dom_name_arr)

    return dom_name_np    

@timing
def Average_Ratings(df, df_ratings_dict, rating_cols_df, rating_cols_dict):
    """ 
        Average ratings across Fitch, Moody's, and S&P to get average rating. Map average rating
        back to S&P rating.
    """
    df_ratings = df[rating_cols_df]
    average_ratings_val = []
    for index, row in df.iterrows():
        sum_rating = 0
        divisor = 0
        # iterate through the three credit ratings
        for i in range(0, len(rating_cols_df)):
            rating = row[rating_cols_df[i]]
            # check if rating can be mapped to rating dictionary
            try:
                value = int(df_ratings_dict[df_ratings_dict[rating_cols_dict[i]] == rating]['Value'].values)
                # if value = 0 (NR) then don't increment divisor or sum
                if value != 0:
                    sum_rating += value
                    divisor += 1
            # rating can't be mapped to ratings dictionary
            except:
                value = None

        #get average rating
        if divisor != 0:
            rating = int(round(float(sum_rating) / float(divisor)))
        else:
            rating = 0

        average_ratings_val.append(rating)

    average_rating_SnP = []
    for i in range(len(average_ratings_val)):
        average_rating_SnP.append(df_ratings_dict[df_ratings_dict['Value'] == \
                                    average_ratings_val[i]]['S&P'].values[0])
    return average_rating_SnP

@timing
def Compare_Curr_Nation(df, df_euro_list):
    """
        Compare issuance currency and marketplace. If they are different then add bond to 
        cb_arr. Speical case if bond is part of European Union, then check if the marketplace 
        isn't the EURO. 
    """
    cb_arr = []

    for index, row in df.iterrows():
        if ((row['Currency'] != row['Nation']) and (row['Currency'] != row['Nation.1']) and \
            \
            ((row['Nation'] in df_euro_list['Country'].values and \
             row['Currency'] != 'euro')  or \
            \
            (row['Nation'] not in df_euro_list['Country'].values))) and \
            \
            (row['Currency'].replace('.', '') != row['Nation'].replace('.', '')) \
            and (row['Currency'] != 'nan'):

               #print row['Currency'].lower(), ':', row['Domicile'].lower()
               cb_arr.append(row)

    return pd.DataFrame(cb_arr)

@timing
def Compare_Nation_Mktplc(df, df_euro):
    """
        Compare country of domicile and marketplace. If they are different then add bond to 
        cb_arr. Speical case if bond is part of European Union, then check if the marketplace 
        isn't the EURO. 
    """
    cb_arr = []    #cross_border array

    for index, row in df.iterrows():
        # if domicile and marketplace don't match
        # if they don't match, then if country is part of EU and marketplace isn't EU
        # if they are nan, don't consider them
        if  (row["Nation"] not in row["Marketplace"] and \
            ((row['Nation'] in df_euro['Country'].values and \
               'Euro' not in row['Marketplace'] and 'euro' not in row['Marketplace'].lower()) or \
            \
               (row['Nation'] not in df_euro['Country'].values))) and \
            \
               (row['Nation'].replace('.', '').lower() not in \
                row['Marketplace'].replace('.', '').lower()) and \
               (row['Nation'] != np.nan or row['Nation'] != 'nan'):

            # print (index, '.', row['Maturity'], row['Nation'], ', ', row['Marketplace'])
            cb_arr.append(row)

    return pd.DataFrame(cb_arr)

@timing
def Remove_Curr_Filter_From_Mkt_Filter(df_cb_mkt, df_euro_list):
    """
        Gets the bonds classified by the domestic, marketplace filter and not classified by
        the domestic currency filter and remove from those classified by marketplace filter. 
        Special case if currency is EURO. Then if country in the euro as well remove it as well.
    """
    df_cb_mkt_no = df_cb_mkt[df_cb_mkt['Foreign Issue Flag(eg Yankee)(Y/N)'] != 'Yes']
    country_arr = df_euro_list['Country'].values

    df_cb_final = []

    arr = []
    counter = 0
    for index, row in df_cb_mkt_no.iterrows():
        if not ((row['Currency'] == row['Domicile']) or \
        (row['Currency'] == 'EURO' and row['Domicile'] in country_arr)):
            df_cb_final.append(row)

    return pd.DataFrame(df_cb_final)

@timing
def Flag_vs_Grouping(df_orig, df_cb_curr, df_cb_dom, df_euro_list, outfile, path):
    for_flag_col = 'Foreign Issue Flag(eg Yankee)(Y/N)'
    df_for = df_orig[df_orig[for_flag_col] == 'Yes']
    df_cb_curr_no = df_cb_curr[df_cb_curr[for_flag_col] != 'Yes']
    df_cb_dom_no = df_cb_dom[df_cb_dom[for_flag_col] != 'Yes']

    df_merge = df_cb_curr_no.merge(df_cb_dom_no, how='outer')
    df_concat = pd.concat([df_merge, df_for])
    df_concat.set_index('IssueDate', inplace=True)
    df_concat.sort_index(inplace=True)
    df_concat.reset_index(inplace = True)
    #df_concat.drop('Unnamed: 0', inplace=True)  # unneeded column added by concat
    

    print ('Number of foreign flagged bonds: ', df_for.shape[0])
    print ('Number of cross-border currency without foreign flag: ', df_cb_curr_no.shape[0])
    print ('Number of cross-border marketplace without foreign flag: ', df_cb_dom_no.shape[0])
    print ('Total number of cross-border bonds with all filters:', df_concat.shape[0])

    df_concat.to_csv(path + outfile, index=False)

    return df_concat

def Filter_Out_SSA(df):
    """
        Split data to SSA and corporate bonds.
        Return split SSA and corporate dataframes.
    """
    SSA_df = df[df['IssueType'] == 'AS']
    SSA_df.index = np.arange(len(SSA_df.Issue_month))
    corporate_ls = ['IG',  'EMIG', 'FC', 'HY', 'EM']
    corporate_df = df[df["IssueType"].isin(corporate_ls)]
    corporate_df.index = np.arange(len(corporate_df.Issue_month))
    SSA_df.to_csv("SSA CB Bonds.csv", index = False)
    corporate_df.to_csv("Corporate CB Bonds.csv", index = False)

    print ('Number of corp bonds: ', corporate_df.shape[0])
    print ('Number of SSA bonds: ', SSA_df.shape[0])

    return SSA_df, corporate_df

#==============================================================================
# generate_notional_ts and add_nation_dummy are 
# functions only called by generate_notional_time_series
#==============================================================================

def generate_notional_ts(data,isCorp):
    #EUROZONE countries list
    EUROZONE=['austria','cyprus','estonia','finland','france','germany',\
    'greece','ireland-Rep','italy','latvia','lithuania',\
    'luxembourg','malta','netherlands','portugal','slovakia','slovenia','spain']
    
    
    #pivot data by date and currency, and group by sum
    #column=data.columns
    #useful_col=[0,37,20,35,23]
    useful_dat=data[['IssueDate', 'Currency', 'Nation', 'PrincipalAmount($ mil)']]
    useful_dat['IssueDate']=pd.to_datetime(useful_dat['IssueDate'], infer_datetime_format = True)
    
    for i in range(len(useful_dat)):
        if useful_dat['Nation'][i] in EUROZONE:
            useful_dat['Nation'][i]='eurozone'

    useful_dat.set_index('IssueDate',inplace=True)
    ts_notional=pd.DataFrame()
    for keys, df in useful_dat.groupby(['Currency','Nation']):
        ts_notional=pd.concat([ts_notional,df.resample("MS", 
                how={'Currency':min,'Nation':min,'PrincipalAmount($ mil)':sum})])
    
    col=['IssueDate','Currency','Nation','PrincipalAmount($ mil)']
    ts_notional=pd.DataFrame(ts_notional).reset_index()[col]
    return ts_notional
    
def add_nation_dummy(CCY,data): 
    data=data[data['Currency']==CCY]
    data=data.sort(['Nation'],ascending=True)   
    data=data.reset_index(drop=True)
    nation_list=list(data['Nation'].unique())
    print(nation_list)
    temp=list(range(len(data)))
    for nation in nation_list:
        for i in range(len(data)):
            if data['Nation'][i]==nation:        
                temp[i]=1
            else:
                temp[i]=0
        data[str(nation)+'_Dummy']=temp   
    data.sort(['IssueDate'],ascending=[True],inplace=True)              
    return data    

@timing
def generate_notional_time_series(SSA_df,corporate_df):
    ccy_list= ['australia', 'canada', 'euro', 'japanese', 'sweden', 'uk', 'us']
    ts_notional_SSA=generate_notional_ts(SSA_df,isCorp=False)
    ts_notional_corp=generate_notional_ts(corporate_df,isCorp=True)
    whole_ts_notional_by_nation_SSA = {}
    whole_ts_notional_by_nation_corp = {}
    for ccy in ccy_list:  
        whole_ts_notional_by_nation_SSA[ccy]=add_nation_dummy(ccy,ts_notional_SSA)
        whole_ts_notional_by_nation_corp[ccy]=add_nation_dummy(ccy,ts_notional_corp)
    return whole_ts_notional_by_nation_SSA,whole_ts_notional_by_nation_corp

def add_value(target_df, data_df,  group_col, typ, dropbox_path):
    '''
    Help function for regression_data
    '''
    df_ls = []
    grouped = pd.groupby(target_df, group_col)
    
    for key, sub_df in grouped:
        if typ == 'swap':
            nation_swap = data_df[data_df.Currency == NATION_CURRENCY_DICT[key]]
            df_ls.append(sub_df.join(nation_swap[['5Y', 'Butterfly 5y', 'Curve 5y']]))
        elif typ == 'credit':
            credit_df = pd.read_csv(dropbox_path + 'cleaned data/Monthly credit spread curves/' + CREDIT_DICT[key],parse_dates = True, infer_datetime_format=True )
            credit_df.Date = pd.to_datetime(credit_df.Date, infer_datetime_format = True)
            credit_df.set_index('Date', inplace = True)
                
            df_ls.append(sub_df.join(credit_df['5Y']))
    return pd.concat(df_ls)
    
def regression_data(Currency, reg_df, dropbox_path):
    '''
    Assemble data for regression for each , columns: notional amount, butterfly rate, curve rate, interest level
    Return a dataframe 
    '''
    
    reg_df = reg_df[['IssueDate','Currency','Nation','PrincipalAmount($ mil)']]
    reg_df.IssueDate = pd.to_datetime(reg_df.IssueDate, infer_datetime_format = True)
    reg_df.set_index('IssueDate', inplace = True)
    #nation of interest 
    nation_ls = ['australia', 'uk', 'sweden', 'canada', 'norway', 'japan', 'euro', 'us', 'new zealand']
 
    reg_df = reg_df[reg_df.Nation.isin(nation_ls)]
    swap_df = pd.read_csv(dropbox_path + 'cleaned data/regression data/All_Butterfly_Spreads_monthly.csv',  parse_dates = True, infer_datetime_format=True)
    swap_df.Date = pd.to_datetime(swap_df.Date, infer_datetime_format = True)
    swap_df.set_index('Date', inplace = True)
    market_swap_df = swap_df[swap_df.Currency == NATION_CURRENCY_DICT[Currency]]
    
     
    reg_df = reg_df.join(market_swap_df[['5Y', 'Butterfly 5y', 'Curve 5y']]) 
    #rename colunms
    reg_df.rename(columns = {'5Y': 'r_market', 'Butterfly 5y': 'Butterfly_market', 'Curve 5y': 'Curve_market'}, inplace = True)
    #add interest rate level, butterfly rate, curve rate for domicile nation    
    reg_df = add_value(reg_df, swap_df, 'Nation','swap', dropbox_path)
    reg_df.rename(columns = {'5Y': 'r_domicile', 'Butterfly 5y': 'Butterfly_domicile', 'Curve 5y': 'Curve_domicile'}, inplace = True)
        
    #add credit spread for market
    credit_df = pd.read_csv(dropbox_path + 'cleaned data/Monthly credit spread curves/' + CREDIT_DICT[Currency],parse_dates = True, infer_datetime_format=True )
    credit_df.Date = pd.to_datetime(credit_df.Date, infer_datetime_format = True)
    credit_df.set_index('Date', inplace = True)
    reg_df = reg_df.join(credit_df['5Y'])
    reg_df.rename(columns = {'5Y': 'credit_market'}, inplace = True)
    reg_df = add_value(reg_df, swap_df, 'Nation', 'credit', dropbox_path)
    
    reg_df.rename(columns = {'5Y': 'credit_domicile'}, inplace = True)
    
    return reg_df
    
def get_reg_dict(Currency_ls, na_dict, dropbox_path):
    
    reg_dict = {}
    for cur in Currency_ls:
        reg_dict[cur] = regression_data(cur, na_dict[cur], dropbox_path)
        
    return reg_dict
    
def weighted_average(data,weight):
    weight=weight/np.nansum(weight)
    return np.nansum(data.multiply(weight))

def clear_cur_eq_nation_obs(data):
    data=data[(data['Currency']!=data['Nation'])]
    #data=data[(data['Currency']!='EURO') | (data['Nation']!='Eurozone')]
    #data=data[(data['Currency']!='Japanese') | (data['Nation']!='Japan')]
    #data=data[(data['Currency']!='US') | (data['Nation']!='U.S.')]
    #data=data[(data['Currency']!='UK') | (data['Nation']!='United Kingdom')]
    return data

def cal_spread(data,isproxy):
    if isproxy:        
        data['r_diff']=data['r_market']-data['US_r_domicile']
        data['Curve_diff']=data['Curve_market']-data['US_Curve_domicile']
        data['Butterfly_diff']=data['Butterfly_market']-data['US_Butterfly_domicile']
        data['Credit_diff']=data['credit_market']-data['credit_domicile']
        data=data[['Date','Currency','Nation','PrincipalAmount($ mil)','isCorp','r_diff','Curve_diff','Butterfly_diff','Credit_diff']]
    else:
        data['r_diff']=data['r_market']-data['r_domicile']
        data['Curve_diff']=data['Curve_market']-data['Curve_domicile']
        data['Butterfly_diff']=data['Butterfly_market']-data['Butterfly_domicile']
        data['Credit_diff']=data['credit_market']-data['credit_domicile']
        data=data[['Date','Currency','Nation','PrincipalAmount($ mil)','isCorp','r_diff','Curve_diff','Butterfly_diff','Credit_diff']]     
    return data

def agg_data(data):
    group=data.groupby(['Date','Currency','isCorp'])
    aggregated_data=pd.DataFrame(columns=data.columns)
    for key, gp in group:
        this=gp.min()
        this['PrincipalAmount($ mil)']=np.nansum(gp['PrincipalAmount($ mil)'])
        this['r_diff']=weighted_average(gp['r_diff'],gp['PrincipalAmount($ mil)'])
        this['Curve_diff']=weighted_average(gp['Curve_diff'],gp['PrincipalAmount($ mil)'])
        this['Butterfly_diff']=weighted_average(gp['Butterfly_diff'],gp['PrincipalAmount($ mil)'])
        this['Credit_diff']=weighted_average(gp['Credit_diff'],gp['PrincipalAmount($ mil)'])    
        aggregated_data=pd.concat([aggregated_data,pd.DataFrame(this).transpose()],axis=0)
    del aggregated_data['Nation']
    aggregated_data.set_index('Date',inplace=True)
    return aggregated_data

def regression_data2(dict_reg_corp, dict_reg_ssa, Currency_ls, dropbox_path):
    '''
    Function to calculate interest spread, butterfly spread, curve spread between issue market and company's domicile country
    '''
    
    
    typ_ls=['Corp','SSA']
    data=pd.DataFrame() 
    
    for typ, dic in zip(typ_ls, [dict_reg_corp, dict_reg_ssa]):
        for cur in Currency_ls:             
            temp= dic[cur].reset_index()
            temp.rename(columns = {"index": 'Date'}, inplace = True)
            #filling the missing month value wilth zero
            sort_temp = temp.sort_values(by = 'Date', axis = 0)
            startdate = sort_temp.Date[0]
            enddate = sort_temp.Date[len(sort_temp.Date) - 1]
            daterange = pd.date_range(startdate, enddate, freq = 'MS')
            df_benchmark = pd.DataFrame({"Date": daterange})
            temp = pd.merge(df_benchmark, sort_temp, how = 'left', on = 'Date')
            temp['PrincipalAmount($ mil)'].fillna(0)
            temp['isCorp']=0            
            if typ=='Corp':        
                temp['isCorp']=1
            data=pd.concat([data,temp],axis=0)
            
            
    usd_proxy=pd.read_csv(dropbox_path + 'cleaned data/regression data/' + 'All_Butterfly_Spreads_monthly.csv')
    usd_proxy=usd_proxy[['Date','5Y','Butterfly 5y','Curve 5y','Currency']]
    usd_proxy=usd_proxy[usd_proxy['Currency']=='USD']
    usd_proxy['Date']=pd.to_datetime(usd_proxy['Date'])
    del usd_proxy['Currency']
    usd_proxy.columns=['Date','US_r_domicile','US_Curve_domicile','US_Butterfly_domicile']

    data=data.rename(columns = {'index':'Date'})
    data2=pd.merge(data,usd_proxy,on='Date',how='left')
    
    data=clear_cur_eq_nation_obs(data)
    data2=clear_cur_eq_nation_obs(data2)
    
    data=cal_spread(data,isproxy=False)
    data2=cal_spread(data2,isproxy=True)

    #data=data.dropna()
    #data2=data2.dropna()    
    
    data=agg_data(data)
    data2=agg_data(data2)
    
    return data, data2

