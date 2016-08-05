import pandas as pd 
import numpy as np
from dateutil import relativedelta as rdelta
pd.options.mode.chained_assignment = None  # default='warn'
import time

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap

@timing
def main():
	path = 'C:\Users\Alex\Desktop\\br_cb_Data\\'	# modify to own path for running
	data_path = 'C:\Users\Alex\Desktop\\br_cb\Data\\'	# modify to own path for running
	filename1 = '2007-2016 DATA with ISIN.csv'
	filename2 = 'domicile_dictionary.csv'
	filename3 = 'Euro_countries_list.csv'
	filename4 = 'currency codes_mod.csv'
	filename5 = 'currency_codes_dict.csv'
	filename6 = 'ratings_dict.csv'
	rating_cols_df = ['Fitch\r\nRating', 'Moody\r\nRating', 'Stan-\r\ndard\r\n &\r\nPoor\'s\r\nRating']
	rating_cols_dict = ['Fitch', 'Moody\'s', 'S&P']

	df = pd.read_csv(path + filename1, low_memory=False)

	#print df.columns.values
	df = Clean_Data(df)

	df_domicile = pd.read_csv(data_path + filename2)
	df_euro_list = pd.read_csv(data_path + filename3)
	df_curr_codes = pd.read_csv(data_path + filename5)
	df_ratings_dict = pd.read_csv(data_path + filename6)

	#print df_euro_list['Country'].values

	df = Convert_Column_Types(df)

	df['Domicile'] = Convert_Dom_Codes(df, df_domicile)
	curr_codes = Parse_Curr_Codes(df, df_curr_codes)
	df['Currency'] = Get_Curr_Names(curr_codes, df_curr_codes, df_euro_list)
	df.dropna(subset=['Currency'], inplace=True)	# removing any empty currencies
	df = df[df['Currency'] != 'nan']				# removing any empty currencies
	df['Overall Rating S&P'] = Average_Ratings(df, df_ratings_dict, rating_cols_df, rating_cols_dict)

	df_cb_curr_dom = Compare_Curr_Dom(df, df_euro_list)
	df_cb_dom_dom = Compare_Dom_Mktplc(df, df_euro_list)
	df_cb_dom_dom = Remove_Curr_Filter_From_Mkt_Filter(df_cb_curr_dom, df_cb_dom_dom, df_euro_list)

	df_cb_curr_nat = Compare_Curr_Nation(df, df_euro_list)
	df_cb_dom_nat = Compare_Nation_Mktplc(df, df_euro_list)
	df_cb_dom_nat = Remove_Curr_Filter_From_Mkt_Filter(df_cb_curr_nat, df_cb_dom_nat, df_euro_list)
	#df_cb_glob = Add_Global_Bonds(df_cb, df)

	outfile_dom = 'All cross-border & foreign flagged v_2 domicile.csv'
	outfile_nation = 'All cross-border & foreign flagged v_2 nation.csv'
	Flag_vs_Grouping(df, df_cb_curr_dom, df_cb_dom_dom, df_euro_list, outfile_dom)
	Flag_vs_Grouping(df, df_cb_curr_nat, df_cb_dom_nat, df_euro_list, outfile_nation)

@timing
def Clean_Data(cleaned_df):
	cleaned_df["Issue\r\nDate"] = pd.to_datetime(cleaned_df["Issue\r\nDate"], infer_datetime_format = True)
	cleaned_df["Issue\r\nDate"] = dateStamp2datetime(cleaned_df["Issue\r\nDate"])
	cleaned_df = cleaned_df[cleaned_df.Maturity != "2013-30"]
	temp1_df = cleaned_df[(cleaned_df["Maturity"] != 'n/a') & ( cleaned_df["Maturity"] != 'Perpet.') & \
						  (cleaned_df['Maturity'] != 'BAD DATE')]

	temp2_df = cleaned_df[cleaned_df["Issue\r\nType"].isin(['n/a', 'Perpet.'])]
	temp1_df["Maturity"] = pd.to_datetime(temp1_df["Maturity"], infer_datetime_format=True, errors='coerce')
	temp1_df["Maturity"] = dateStamp2datetime(temp1_df["Maturity"])
	cleaned_df = temp1_df.append(temp2_df, ignore_index = True)

	#cleaned_df["PrincipalAmountIn Currency(mil)"] = [float(notional) for notional in cleaned_df["PrincipalAmountIn Currency(mil)"]]

	cleaned_df["Issue_year"] = cleaned_df["Issue\r\nDate"].dt.year
	cleaned_df["Issue_month"] = cleaned_df["Issue\r\nDate"].dt.month
	cleaned_df["bond_terms"] = calterm(cleaned_df,'Issue\r\nDate', 'Maturity')

	return cleaned_df

	#split data to SSA and corporate bonds
	SSA_df = cleaned_df[cleaned_df['IssueType'] == 'AS']
	SSA_df.index = np.arange(len(SSA_df.Issue_month))
	corporate_ls = ['IG',  'EMIG', 'FC', 'HY', 'EM']
	corporate_df = cleaned_df[cleaned_df["IssueType"].isin(corporate_ls)]
	corporate_df.index = np.arange(len(corporate_df.Issue_month))
	SSA_df.to_csv("/Users/leicui/blackrock_data/SSA.csv", index = False)
	corporate_df.to_csv("/Users/leicui/blackrock_data/corp.csv", index = False)

@timing
def dateStamp2datetime(DateSeries):
    date_ls = []
    
    for date in DateSeries:
        try:
            date_ls.append(date.to_datetime())
        except:
            date_ls.append("Perpuity")
        
    return date_ls

@timing
def calterm(df, issue_date, maturity_date):
	"""
		Calculate term of the bonds accroding to issue_date and maturity date	
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
def Merge_Dfs(data_filenames, path):
	frames = []
	for file in data_filenames:
		df = pd.read_csv(path + file, index_col='Issue\nDate', #usecols=use_cols,
					parse_dates=True, infer_datetime_format=True, na_values=np.nan,
					low_memory=False)
		frames.append(df)

	return pd.concat(frames)

@timing
def Convert_Column_Types(df):
	for y in df.columns:
		if(df[y].dtype == np.float64 or df[y].dtype == np.int64):
			df[y] = df[y].astype(float, copy=False)
		else:
			df[y] = df[y].astype(str, copy=False)

	return df

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
				print '--' + str(code) + '---'
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
	curr_princ_arr = df['Prncpl Amt \r\nw/Curr of \r\nIss - in this\r\nMkt (mil)'].values

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

	dom_code_arr = df['Domicile\r\nNation\r\nCode']
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
def Compare_Curr_Dom(df, df_euro_list):
	"""
		Compare issuance currency and marketplace. If they are different then add bond to 
		cb_arr. Speical case if bond is part of European Union, then check if the marketplace 
		isn't the EURO. 
	"""

	cb_arr = []

	for index, row in df.iterrows():
		if 	row['Currency'].lower() != row['Domicile'].lower() and \
			(row['Domicile'] in df_euro_list['Country'].values and \
			 row['Currency'].lower() != 'euro') and \
			(row['Currency'] != 'nan'):

		   	cb_arr.append(row)

	return pd.DataFrame(cb_arr)

@timing
def Compare_Curr_Nation(df, df_euro_list):
	"""
		Compare issuance currency and marketplace. If they are different then add bond to 
		cb_arr. Speical case if bond is part of European Union, then check if the marketplace 
		isn't the EURO. 
	"""

	cb_arr = []

	for index, row in df.iterrows():
		if 	row['Currency'].lower() != row['Nation'].lower() and \
			(row['Nation'] in df_euro_list['Country'].values and \
			 row['Currency'].lower() != 'euro') and \
			(row['Currency'] != 'nan'):

		   	#print row['Currency'].lower(), ':', row['Domicile'].lower()
		   	cb_arr.append(row)

	return pd.DataFrame(cb_arr)

@timing
def Compare_Dom_Mktplc(df, df_euro):
	"""
		Compare country of domicile and marketplace. If they are different then add bond to 
		cb_arr. Speical case if bond is part of European Union, then check if the marketplace 
		isn't the EURO. 
	"""
	cb_arr = []	#cross_border array

	for index, row in df.iterrows():
		# if domicile and marketplace don't match
		# if they don't match, then if country is part of EU and marketplace isn't EU
		# if they are nan, don't consider them
		if 	row["Domicile"] not in row["Marketplace"] \
			and (row['Domicile'] in df_euro['Country'].values and \
		   		'euro' not in row['Marketplace'].lower()) \
		    and	(row['Domicile'] != np.nan):
		   	#print row['Domicile'], ':', row['Marketplace']
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
		if 	row["Nation"] not in row["Marketplace"] and \
			(row['Nation'] in df_euro['Country'].values and \
		   	'Euro' not in row['Marketplace'] and 'EURO' not in row['Marketplace']) and \
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
def Domestic_Filter_not_Curr_Filter(df_cb_curr, df_cb_dom, df_euro_list):
	"""
		Gets the bonds classified by the domestic, marketplace filter and not classified by
		the domestic currency filter. Special case if currency is EURO. Then if country in the 
		euro as well include it as well in the difference between filters.
	"""
	df_cb_curr_no = df_cb_curr[df_cb_curr['Foreign Issue Flag\r\n(eg Yankee)\r\n(Y/N)'] != 'Yes']
	df_cb_dom_no = df_cb_dom[df_cb_dom['Foreign Issue Flag\r\n(eg Yankee)\r\n(Y/N)'] != 'Yes']

	arr = []
	for index, row in df_cb_dom_no.iterrows():
		if (row['Currency'] == row['Domicile']) or \
		(row['Currency'] == 'EURO' and row['Domicile'] in df_euro_list['Country'].values):
			arr.append(row)

	df = pd.DataFrame(arr)
	df.to_csv('cols.csv')

def Remove_Curr_Filter_From_Mkt_Filter(df_cb_curr, df_cb_dom, df_euro_list):
	"""
		Gets the bonds classified by the domestic, marketplace filter and not classified by
		the domestic currency filter and remove from those classified by marketplace filter. 
		Special case if currency is EURO. Then if country in the euro as well remove it as well.
	"""
	df_cb_curr_no = df_cb_curr[df_cb_curr['Foreign Issue Flag\r\n(eg Yankee)\r\n(Y/N)'] != 'Yes']
	df_cb_dom_no = df_cb_dom[df_cb_dom['Foreign Issue Flag\r\n(eg Yankee)\r\n(Y/N)'] != 'Yes']

	arr = []
	for index, row in df_cb_dom_no.iterrows():
		if (row['Currency'] == row['Domicile']) or \
		(row['Currency'] == 'EURO' and row['Domicile'] in df_euro_list['Country'].values):
			df_cb_dom_no.drop(index, inplace=True)

	return df_cb_dom_no

@timing
def Flag_vs_Grouping(df_orig, df_cb_curr, df_cb_dom, df_euro_list, outfile):
	df_for = df_orig[df_orig['Foreign Issue Flag\r\n(eg Yankee)\r\n(Y/N)'] == 'Yes']
	df_cb_curr_no = df_cb_curr[df_cb_curr['Foreign Issue Flag\r\n(eg Yankee)\r\n(Y/N)'] != 'Yes']
	df_cb_dom_no = df_cb_dom[df_cb_dom['Foreign Issue Flag\r\n(eg Yankee)\r\n(Y/N)'] != 'Yes']

	df_merge = df_cb_curr_no.merge(df_cb_dom_no, how='outer')
	df_concat = pd.concat([df_merge, df_for])
	df_concat.set_index('Issue\r\nDate', inplace=True)
	df_concat.sort_index(inplace=True)

	df_cb_dom_no.reset_index(drop=True, inplace=True)
	df_cb_curr_no.reset_index(drop=True, inplace=True)

	print 'Number of foreign flagged bonds: ', df_for.shape[0]
	print 'Number of cross-border currency without foreign flag: ', df_cb_curr_no.shape[0]
	print 'Number of cross-border domicile/nation without foreign flag: ', df_cb_dom_no.shape[0]
	print 'Total number of cross-border bonds with all filters:', df_concat.shape[0]

	df_concat.to_csv(outfile)

if __name__ == '__main__':
	main()







