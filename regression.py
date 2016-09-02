import pandas as pd
import numpy as np
import os

def func(term, name):
	curr_files = ['AUD.xlsx', 'CAD.xlsx', 'EUR.xlsx', 'GBP.xlsx', 'JPY.xlsx', 
				  'SEK.xlsx', 'USD.xlsx']
	df_curr = []

	for curr_file in curr_files:
		df = pd.read_excel(path + curr_file)
		df.set_index('Dates', inplace=True)
		curr = df['Currency'][0]
		df = df.resample(term, how='mean', axis=0)
		df['Currency'] = [curr] * df.shape[0]
		df_curr.append(df)

	df_concat = pd.concat(df_curr)
	df_concat.drop(['Year', 'Month', 'Day'], axis=1, inplace=True)

	df_concat.to_csv('All_Butterfly_Spreads_' + name + '.csv')


def Set_Up_Regression_Vars(filename):
	""" Separate dataframes for each individual currency.
		Columns to access each regression variable:
			'Butterfly 10y' --> (ex. df_butt_arr[0]['Butterfly 10y'])
			'Curve 10y'
			'Currency'
	"""
	df = pd.read_csv(filename, index_col='Dates')

	curr_order_arr = []
	df_regr_arr = []
	grouped = df.groupby('Currency')
	for name, group in grouped:
		curr_order_arr.append(name)
		df_regr_arr.append(group)	

	return curr_order_arr, df_regr_arr	

def Get_Regression_Vars(curr_order_arr, df_regr_arr):
	"""
		dictionaries for:
			10 Year interest rate
			butterfly spread
			10 year curve rate
		keys are currency abbreviations: ['AUD', 'CAD', 'EUR', 'GBP', 'JPY', 'SEK', 'USD']
	"""

	df_10_yr_int_rate_dict = {}
	df_10_yr_butt_rate_dict = {}
	df_10_yr_curr_rate_dict = {}

	for i in range(len(df_regr_arr)):
		df_10_yr_int_rate_dict[curr_order_arr[i]] = df_regr_arr[i]['10Y']
		df_10_yr_butt_rate_dict[curr_order_arr[i]] = df_regr_arr[i]['Butterfly 10y']
		df_10_yr_curr_rate_dict[curr_order_arr[i]] = df_regr_arr[i]['Curve 10y']

	return df_10_yr_int_rate_dict, df_10_yr_butt_rate_dict, df_10_yr_curr_rate_dict

def Get_Curr_Basis_Swap(filename_arr, folder=''):
	df_us_curr_swap_arr = []
	for filename in filename_arr:
		file_path = os.getcwd() + '\\' + folder + '\\' + filename
		df_us_curr_swap_arr.append(pd.read_csv(file_path))

	return df_us_curr_swap_arr

def Create_Regression_Dfs(filename, curr_arr, curr_abbrev_dict, df_10_yr_int_rate_dict, 
						  df_10_yr_butt_rate_dict, df_10_yr_curr_rate_dict, 
						  df_us_curr_swap_arr):
	df = pd.read_csv(filename, index_col='IssueDate')

	count = 0
	for index, row in df.iterrows():
		if row['Currency'] in curr_abbrev_dict:
			count += 1

	print (count)

if __name__ == '__main__':
	#func('MS', 'monthly')	# MS = month start
	#func('AS', 'yearly')	# AS = year start

	filename_cleaned_data = 'All cross-border & foreign flagged v_9 nation.csv'
	filename_euro_countries = 'Euro_countries_list.csv'
	df = pd.read_csv(filename_cleaned_data)
	df_euro_list = pd.read_csv(filename_euro_countries)

	df.Nation in df_euro_list: df.Ntaion = 'EURO'


	filename_butterfly = 'All_Butterfly_Spreads_monthly.csv'

	# curr order: ['AUD', 'CAD', 'EUR', 'GBP', 'JPY', 'SEK', 'USD']
	curr_arr, df_regr_arr = Set_Up_Regression_Vars(filename_butterfly)
	curr_abbrev_dict = {'US':'USD', 'Australia':'AUD', 'Canada':'CAD', 'EURO':'EUR', 
						'Japanese':'JPY', 'UK':'GBP', 'Sweden':'SEK'}
	nation_abbrev_dict = {'U.S.':'USD', 'Australia':'AUD', 'Canada':'CAD', 'EURO':'EUR', 
						'Japanese':'JPY', 'UK':'GBP', 'Sweden':'SEK'}

	df_10_yr_int_rate_dict, df_10_yr_butt_rate_dict, df_10_yr_curr_rate_dict = \
				Get_Regression_Vars(curr_arr, df_regr_arr)

	filename_curr_swaps_arr = ['AUD Basis Swaps Curve monthly.csv', 
							   'CAD Basis Swaps Curve monthly.csv',
							   'CHF Basis Swaps Curve monthly.csv',
							   'CNY Basis Swaps Curve monthly.csv',
							   'EUR Basis Swaps Curve monthly.csv',
							   'GBP Basis Swaps Curve monthly.csv',
							   'JPY Basis Swaps Curve monthly.csv',
							   'SEK Basis Swaps Curve monthly.csv']
	folder = 'Monthly CCY vs. USD curves'		#**** change to folder that contains curr swap files

	df_us_curr_swap_arr = Get_Curr_Basis_Swap(filename_curr_swaps_arr, folder)

	Create_Regression_Dfs(filename_cleaned_data, curr_arr, curr_abbrev_dict, 
						  df_10_yr_int_rate_dict, df_10_yr_butt_rate_dict, 
						  df_10_yr_curr_rate_dict, df_us_curr_swap_arr)

	#df = pd.DataFrame(df_10_yr_int_rate_dict[curr_arr[0]])
	#print (df)



'''
B   business day frequency
C   custom business day frequency (experimental)
D   calendar day frequency
W   weekly frequency
M   month end frequency
BM  business month end frequency
MS  month start frequency
BMS business month start frequency
Q   quarter end frequency
BQ  business quarter endfrequency
QS  quarter start frequency
BQS business quarter start frequency
A   year end frequency
BA  business year end frequency
AS  year start frequency
BAS business year start frequency
H   hourly frequency
T   minutely frequency
S   secondly frequency
L   milliseconds
U   microseconds
'''