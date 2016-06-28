import pandas as pd 
import numpy as np


def main():
	path = 'C:\Users\Alex\Desktop\\'	# modify to own path for running
	filename = 'csv IG issuance since Jan 2016.csv'

	use_cols = ['Maturity\n(mm/dd/yyyy)', 'Issuer', 'Nation', 
				'Primary\nExchange\nWhere\nIssuer\'s\nStock\nTrades', 'Coupon\n (%)', 
				'Offer\nYield\nto Maturity\n (%)', 'Stan-\ndard\n &\nPoor\'s\nRating', 
				'Interest\nPayment\nFrequency', 'Cpn\nType', 'Marketplace']

	df = pd.read_csv(path + filename, index_col='Issue\nDate', usecols=use_cols,
					parse_dates=True, na_values=['nan'])

if __name__ == '__main__':
	main()