import pandas as pd
import numpy as np

path = r"C:\Users\Alex\Desktop\\br_cb_Data\Butterfly Currencies\\"

def func():
	curr_files = ['AUD.xlsx', 'CAD.xlsx', 'EUR.xlsx', 'GBP.xlsx', 'JPY.xlsx', 
				  'SEK.xlsx', 'USD.xlsx']
	df_curr = []

	for curr_file in curr_files:
		df_curr.append(pd.read_excel(path + curr_file))

	df_concat = pd.concat(df_curr)
	df_concat.set_index('Dates', inplace=True)
	df_concat.drop(['Year', 'Month', 'Day'], axis=1, inplace=True)

	df_concat = df_concat.resample("M", how='mean')

	print (df_concat.head(10))

	df_concat.to_csv('All_Butterfly_Spreads.csv')

if __name__ == '__main__':
	func()


