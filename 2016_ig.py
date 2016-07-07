import pandas as pd 
import numpy as np


def main():
	path = 'C:\Users\Alex\Desktop\\br_cb_Data\\'	# modify to own path for running
	data_path = 'C:\Users\Alex\Desktop\\br_cb\Data\\'
	filename = 'csv IG issuance since Jan 2016.csv'
	filename2 = 'domicile_dictionary.csv'
	filename3 = 'Euro_countries_list.csv'
	filename4 = 'non convertible bonds issuance since Jan 2016.csv'
	filename5 = 'currency codes.csv'

	data_0809 = '2008-2009 cleaned.csv'
	df_0809 = pd.read_csv(path + data_0809, index_col='IssueDate', #usecols=use_cols,
					parse_dates=True, infer_datetime_format=True, na_values=np.nan)

	df = df_0809

	'''df = pd.read_csv(path + filename4, index_col='Issue\nDate', #usecols=use_cols,
					parse_dates=True, infer_datetime_format=True, na_values=np.nan)'''

	df_domicile = pd.read_csv(data_path + filename2)
	df_euro_list = pd.read_csv(data_path + filename3)
	df_curr_codes = pd.read_csv(data_path + filename5)

	df = Convert_Column_Types(df)

	dom_name_np = Convert_Dom_Codes(df, df_domicile)
	#curr_code_np = Convert_Curr_Codes(df, df_curr_codes)
	df['Domicile'] = dom_name_np

	df_cb = Compare_Dom_Mktplc(df, df_euro_list)
	#df_cb = Compare_Nation_Mktplc(df, df_euro_list)
	df_cb = Add_Global_Bonds(df_cb, df)

	Flag_vs_Grouping(df, df_cb)

def Merge_Dfs(data_filenames, path):
	frames = []
	for file in data_filenames:
		df = pd.read_csv(path + file, index_col='IssueDate', #usecols=use_cols,
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

def Convert_Curr_Codes(df, df_curr_codes):
	dict_curr_codes = df_curr_codes.set_index('Code')['Country'].to_dict()

	curr_code_arr = df['DenominationsCurrency2']	# currency column in SDC data
	curr_name_arr = []
	miss_code = []
	for code in curr_code_arr:
		# append nan values to keep same size as original df
		if code == 'nan':
			curr_name_arr.append('nan')
		else:
			try:
				curr_name_arr.append(dict_domicile[code])
			except:
				miss_code.append(code)
				pass

	# Make sure no missed country codes
	assert (len(miss_code) == 0), np.unique(miss_code)

	curr_name_np = np.array(curr_name_arr)

	return curr_name_np	

def Convert_Dom_Codes(df, df_domicile):
	"""
		Define cross-border as differing nation and currency, of differing nation and 
		exchange location.
		Domicile nation code = country of issuance. 
		Convert Domicile Nation Code to the actual country name using df_domicile as dictionary.
	"""
	dict_domicile = df_domicile.set_index('abbreviation')['name'].to_dict()

	dom_code_arr = df['DomicileNationCode']
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
		if 	row["Domicile"] not in row["Marketplace"] and \
			(row['Domicile'] in df_euro['Country'].values and \
		   	'Euro' not in row['Marketplace'] and 'EURO' not in row['Marketplace']) and \
		   	row['Domicile'] != 'nan':
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
	print df_merged.shape[0]

	return df_merged

def Flag_vs_Grouping(df_orig, df_cb):
	df_for = df_orig[df_orig['Foreign Issue Flag(eg Yankee)(Y/N)'] == 'Yes']

	print 'Number of foreign flagged bonds: ', df_for.shape[0]
	print 'Number of cross-border bonds found: ', df_cb.shape[0]
	print 'Number of cross-border bonds without foreign flag: ', \
			df_cb[df_cb['Foreign Issue Flag(eg Yankee)(Y/N)'] != 'Yes'].shape[0]

	df_cb[df_cb['Foreign Issue Flag(eg Yankee)(Y/N)'] != 'Yes'].to_csv('cb but not foreign flagged.csv')

if __name__ == '__main__':
	main()
