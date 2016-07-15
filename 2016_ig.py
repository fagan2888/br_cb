import pandas as pd 
import numpy as np


def main():
	path = 'C:\Users\Alex\Desktop\\br_cb_Data\\'	# modify to own path for running
	data_path = 'C:\Users\Alex\Desktop\\br_cb\Data\\'
	filename1 = '2007-2016 DATA with ISIN.csv'
	filename2 = 'domicile_dictionary.csv'
	filename3 = 'Euro_countries_list.csv'
	filename4 = 'currency codes_mod.csv'

	df = pd.read_csv(path + filename1)

	df_domicile = pd.read_csv(data_path + filename2)
	df_euro_list = pd.read_csv(data_path + filename3)
	df_curr_codes = pd.read_csv(data_path + filename4)

	df = Convert_Column_Types(df)

	df['Domicile'] = Convert_Dom_Codes(df, df_domicile)
	curr_codes = Parse_Curr_Codes(df, df_curr_codes)
	df['Currency'] = Get_Curr_Names(curr_codes, df_curr_codes)

	df_cb_curr = Compare_Curr_Mkt(df, df_euro_list)

	df_cb_dom = Compare_Dom_Mktplc(df, df_euro_list)
	#df_cb = Compare_Nation_Mktplc(df, df_euro_list)
	#df_cb = Add_Global_Bonds(df_cb, df)

	Flag_vs_Grouping(df, df_cb_curr, df_cb_dom)

def Merge_Dfs(data_filenames, path):
	frames = []
	for file in data_filenames:
		df = pd.read_csv(path + file, index_col='Issue\nDate', #usecols=use_cols,
					parse_dates=True, infer_datetime_format=True, na_values=np.nan,
					low_memory=False)
		frames.append(df)

	return pd.concat(frames)

def Convert_Column_Types(df):
	for y in df.columns:
		if(df[y].dtype == np.float64 or df[y].dtype == np.int64):
			df[y] = df[y].astype(float, copy=False)
		else:
			df[y] = df[y].astype(str, copy=False)

	return df

def Get_Curr_Names(curr_codes, df_curr_codes):
	"""
		Create a dictionary mapping of currency codes to country names from SDC
		currency codes list. Map every currency code from dataset to country name.
	"""
	dict_curr = df_curr_codes.set_index('Code')['Country'].to_dict()

	curr_name_arr = []
	miss_code = []
	for code in curr_codes:
		# append nan values to keep same size as original df
		if code == 'NaN':
			curr_name_arr.append('NaN')
		else:
			try:
				curr_name_arr.append(dict_curr[code])
			except:
				miss_code.append(code)
				pass

	# Make sure no missed country codes, otherwise print missed codes
	assert (len(miss_code) == 0), np.unique(miss_code)

	curr_name_np = np.array(curr_name_arr)

	return curr_name_np

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
			curr_code_arr.append('NaN')

	# Make sure no missed country codes
	assert (len(curr_code_arr) == len(curr_princ_arr))

	return curr_code_arr

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
		if code == 'nan':
			dom_name_arr.append('nan')
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

def Compare_Curr_Mkt(df, df_euro_list):
	"""
		Compare issuance currency and marketplace. If they are different then add bond to 
		cb_arr. Speical case if bond is part of European Union, then check if the marketplace 
		isn't the EURO. 
	"""
	curr_names = [str.split(x)[0] for x in df['Currency'].values]
	df['Curr Abbrev'] = curr_names

	cb_arr = []

	for index, row in df.iterrows():
		if 	row['Curr Abbrev'].lower() not in row['Marketplace'].lower() \
			and (row['Curr Abbrev'] not in df_euro_list['Country'].values and \
				'euro' in row['Marketplace'].lower()) \
			and row['Curr Abbrev'] != 'NaN':

		   	#print row['Currency'].lower(), ':', row['Marketplace'].lower()
		   	cb_arr.append(row)

	return pd.DataFrame(cb_arr)

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
		    and	row['Domicile'] != 'nan':
		   	#print row['Domicile'], ':', row['Marketplace']
			cb_arr.append(row)

	return pd.DataFrame(cb_arr)

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
		   	row['Nation'] != 'nan':

	 		#print index, '.', row['Maturity'], row['Domicile'], ', ', row['Marketplace']
			cb_arr.append(row)

	return pd.DataFrame(cb_arr)

def Add_Global_Bonds(df_cb, df):
	"""
		Add all global bonds not filtered by foreign flag and merge with
		already created list of cross_border bonds.
	"""
	df_global = df[df['TypeofSecurity'].str.contains('Global')]
	df_global = df_global[df_global['Foreign Issue Flag(eg Yankee)(Y/N)'] == 'No']
	df_merged = df_cb.merge(df_global, how="outer")

	return df_merged

def Flag_vs_Grouping(df_orig, df_cb_curr, df_cb_dom):
	df_for = df_orig[df_orig['Foreign Issue Flag\r\n(eg Yankee)\r\n(Y/N)'] == 'Yes']
	df_cb_curr_no = df_cb_curr[df_cb_curr['Foreign Issue Flag\r\n(eg Yankee)\r\n(Y/N)'] != 'Yes']
	df_cb_dom_no = df_cb_dom[df_cb_dom['Foreign Issue Flag\r\n(eg Yankee)\r\n(Y/N)'] != 'Yes']

	df_merge = df_cb_curr_no.merge(df_cb_dom_no, how='outer')
	df_concat = pd.concat([df_merge, df_for])
	df_concat.sort_index(inplace=True)

	print 'Number of foreign flagged bonds: ', df_for.shape[0]
	print 'Number of cross-border currency without foreign flag: ', df_cb_curr_no.shape[0]
	print 'Number of cross-border dominicile without foreign flag: ', df_cb_dom_no.shape[0]
	print 'Total number of cross-border bonds with all filters:', df_concat.shape[0]

	df_concat.to_csv('All cross-border & foreign flagged.csv')

if __name__ == '__main__':
	main()







