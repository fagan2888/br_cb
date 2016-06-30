import pandas as pd 
import numpy as np


def main():
	path = 'C:\Users\Alex\Desktop\\'	# modify to own path for running
	data_path = 'C:\Users\Alex\Desktop\\br_cb\Data\\'
	filename = 'csv IG issuance since Jan 2016.csv'
	filename2 = 'domicile_dictionary.csv'
	filename3 = 'Euro_countries_list.csv'
	filename4 = 'non convertible bonds issuance since Jan 2016.csv'

	test_filename = 'test'

	use_cols = ['Maturity\n(mm/dd/yyyy)', 'Issuer', 'Nation', 'Issue\nDate',
				'Primary\nExchange\nWhere\nIssuer\'s\nStock\nTrades', 'Coupon\n (%)', 
				'Offer\nYield\nto Maturity\n (%)', 'Stan-\ndard\n &\nPoor\'s\nRating', 
				'Interest\nPayment\nFrequency', 'Cpn\nType', 'Marketplace', 'Market\nArea',
				'Domicile\nNation\nCode', 'Foreign Issue Flag\n(eg Yankee)\n(Y/N)']

	df = pd.read_csv(path + filename4, index_col='Issue\nDate', #usecols=use_cols,
					parse_dates=True, infer_datetime_format=True, na_values=np.nan)

	df_domicile = pd.read_csv(data_path + filename2)
	df_euro_list = pd.read_csv(data_path + filename3)

	df = Convert_Column_Types(df)

	dom_name_np = Convert_Dom_Codes(df, df_domicile)
	df['Domicile'] = dom_name_np

	df_cb = Compare_Dom_Mktplc(df, df_euro_list)

	Flag_vs_Grouping(df, df_cb)

def Foreign_Issue(df):
	df_for = df['Foreign Issue Flag\n(eg Yankee)\n(Y/N)']

def Convert_Column_Types(df):
	for y in df.columns:
		if(df[y].dtype == np.float64 or df[y].dtype == np.int64):
			df[y] = df[y].astype(float, copy=False)
		else:
			df[y] = df[y].astype(str, copy=False)

	return df

def Convert_Dom_Codes(df, df_domicile):
	"""
		Define cross-border as differing nation and currency, of differing nation and 
		exchange location.
		Domicile nation code = country of issuance. 
		Convert Domicile Nation Code to the actual country name using df_domicile as dictionary.
	"""
	dict_domicile = df_domicile.set_index('abbreviation')['name'].to_dict()

	dom_code_arr = df['Domicile\nNation\nCode']
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
		   	#print row['Domicile'], row['Marketplace']
			cb_arr.append(row)

	return pd.DataFrame(cb_arr)

def Flag_vs_Grouping(df_orig, df_cb):
	df_for = df_orig[df_orig['Foreign Issue Flag\n(eg Yankee)\n(Y/N)'] == 'Yes']

	print 'Number of foreign flagged bonds: ', df_for.shape[0]
	print 'Number of cross-border bonds found: ', df_cb.shape[0]
	print 'Number of cross-border bonds without foreign flag: ', \
			df_cb[df_cb['Foreign Issue Flag\n(eg Yankee)\n(Y/N)'] != 'Yes'].shape[0]
	

def Group_Monthly(df):
	""" 
		Group data into subsections of month and nation. 
		Create a dataframe of the subsections with the month, nation, and number of 
		entries in a subsection as the 'count' column.
		Sort by decreasing 'count'.

	"""
	grouped = df.groupby([pd.TimeGrouper(freq='M'), 'Nation'])
	df_mth_nat_ct = pd.DataFrame(
						data=np.array(
							[[name[0], name[1], group.shape[0]] for name,group in grouped]
						),
						columns=['date', 'nation', 'count']).set_index('date')

	df_mth_nat_ct.sort(columns=['count', 'nation'], ascending=False, inplace=True)

	print df_mth_nat_ct

if __name__ == '__main__':
	main()
