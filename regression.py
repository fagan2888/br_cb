import pandas as pd
import numpy as np

path = r"C:\Users\Alex\Desktop\\br_cb_Data\Butterfly Currencies\\"

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
	df = pd.read_csv(filename)

	curr_order_arr = []
	df_butt_arr = []
	grouped = df.groupby('Currency')
	for name, group in grouped:
		curr_order_arr.append(name)
		df_butt_arr.append(group)		

if __name__ == '__main__':
	#func('MS', 'monthly')	# MS = month start
	#func('AS', 'yearly')	# AS = year start

	filename = 'All_Butterfly_Spreads_monthly.csv'
	Set_Up_Regression_Vars(filename)


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