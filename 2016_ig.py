import pandas as pd 
import numpy as np


def main():
	path = 'C:\Users\Alex\Desktop\\'	# modify to own path for running
	filename = 'csv IG issuance since Jan 2016.csv'

	use_cols = ['Maturity\n(mm/dd/yyyy)', 'Issuer', 'Nation', 'Issue\nDate',
				'Primary\nExchange\nWhere\nIssuer\'s\nStock\nTrades', 'Coupon\n (%)', 
				'Offer\nYield\nto Maturity\n (%)', 'Stan-\ndard\n &\nPoor\'s\nRating', 
				'Interest\nPayment\nFrequency', 'Cpn\nType', 'Marketplace']

	df = pd.read_csv(path + filename, index_col='Issue\nDate', usecols=use_cols,
					parse_dates=True, infer_datetime_format=True, na_values=['nan'])

	Group_Monthly(df)

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