import pandas as pd 
import numpy as np
from dateutil import relativedelta as rdelta
import time
import datetime

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

	df = Fix_Maturities(df)	# Converts all years from 1900's to 2000's

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

	curr_princ_arr = [str(x) for x in curr_princ_arr]

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

	dom_code_arr = df[domicile_col]
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

	df['Currency'] = [str(item).lower() for item in df['Currency']]
	df['Nation'] = [str(item).lower() for item in df['Nation']]
	df['Nation.1'] = [str(item).lower() for item in df['Nation.1']]

	for index, row in df.iterrows():
		if 	((row['Currency'] != row['Nation']) and (row['Currency'] != row['Nation.1']) and \
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
	df['Nation'] = np.where(df['Nation'] == 'United States', 'U.S.', df['Nation'])

	cb_arr = []	#cross_border array

	for index, row in df.iterrows():
		# if domicile and marketplace don't match
		# if they don't match, then if country is part of EU and marketplace isn't EU
		# if they are nan, don't consider them
		if 	(row["Nation"] not in row["Marketplace"] and \
			((row['Nation'] in df_euro['Country'].values and \
		   	'Euro' not in row['Marketplace'] and 'euro' not in row['Marketplace'].lower()) or \
			\
		   	(row['Nation'] not in df_euro['Country'].values))) and \
			\
		   	(row['Nation'].replace('.', '').lower() not in \
				row['Marketplace'].replace('.', '').lower()) and \
		   	(row['Nation'] != np.nan or row['Nation'] != 'nan'):

	 		#print index, '.', row['Maturity'], row['Domicile'], ', ', row['Marketplace']
			cb_arr.append(row)

	return pd.DataFrame(cb_arr)

@timing
def Add_Global_Bonds(df_cb, df):
	"""
		Add all global bonds not filtered by foreign flag and merge with
		already created list of cross_border bonds.
	"""
	df_global = df[df['TypeofSecurity'].str.contains('Global')]
	df_global = df_global[df_global['Foreign Issue Flag(eg Yankee)(Y/N)'] == 'No']
	df_merged = df_cb.merge(df_global, how="outer")

	return df_merged

@timing
def Remove_Curr_Filter_From_Mkt_Filter(df_cb_curr, df_cb_dom, df_euro_list):
	"""
		Gets the bonds classified by the domestic, marketplace filter and not classified by
		the domestic currency filter and remove from those classified by marketplace filter. 
		Special case if currency is EURO. Then if country in the euro as well remove it as well.
	"""
	df_cb_curr_no = df_cb_curr[df_cb_curr['Foreign Issue Flag(eg Yankee)(Y/N)'] != 'Yes']
	df_cb_dom_no = df_cb_dom[df_cb_dom['Foreign Issue Flag(eg Yankee)(Y/N)'] != 'Yes']

	arr = []
	counter = 0
	for index, row in df_cb_dom_no.iterrows():
		#counter += 1
		#print counter
		if (row['Currency'] == row['Domicile']) or \
		(row['Currency'] == 'EURO' and row['Domicile'] in df_euro_list['Country'].values):
			df_cb_dom_no.drop(index, inplace=True)

	return df_cb_dom_no

@timing
def Flag_vs_Grouping(df_orig, df_cb_curr, df_cb_dom, df_euro_list, outfile):
	for_flag_col = 'Foreign Issue Flag(eg Yankee)(Y/N)'
	df_for = df_orig[df_orig[for_flag_col] == 'Yes']
	df_cb_curr_no = df_cb_curr[df_cb_curr[for_flag_col] != 'Yes']
	df_cb_dom_no = df_cb_dom[df_cb_dom[for_flag_col] != 'Yes']

	df_merge = df_cb_curr_no.merge(df_cb_dom_no, how='outer')
	df_concat = pd.concat([df_merge, df_for])
	df_concat.set_index('IssueDate', inplace=True)
	df_concat.sort_index(inplace=True)

	df_cb_dom_no.reset_index(drop=True, inplace=True)
	df_cb_curr_no.reset_index(drop=True, inplace=True)

	print ('Number of foreign flagged bonds: ', df_for.shape[0])
	print ('Number of cross-border currency without foreign flag: ', df_cb_curr_no.shape[0])
	print ('Number of cross-border marketplace without foreign flag: ', df_cb_dom_no.shape[0])
	print ('Total number of cross-border bonds with all filters:', df_concat.shape[0])

	df_concat.to_csv(outfile, index=False)

	return df_concat

def	Filter_Out_SSA(df):
	"""
		Split data to SSA and corporate bonds.
		Return split SSA and corporate dataframes.
	"""
	SSA_df = df[df['IssueType'] == 'AS']
	SSA_df.index = np.arange(len(SSA_df.Issue_month))
	corporate_ls = ['IG',  'EMIG', 'FC', 'HY', 'EM']
	corporate_df = df[df["IssueType"].isin(corporate_ls)]
	corporate_df.index = np.arange(len(corporate_df.Issue_month))
	SSA_df.to_csv("SSA.csv", index = False)
	corporate_df.to_csv("corp.csv", index = False)

	print ('Number of corp bonds: ', corporate_df.shape[0])
	print ('Number of SSA bonds: ', SSA_df.shape[0])

	return SSA_df, corporate_df






