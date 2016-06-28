import pandas as pd 
import numpy as np


def main():
	path = 'C:\Users\Alex\Desktop\\'	# modify to own path for running
	filename = 'csv IG issuance since Jan 2016.csv'

	df = pd.read_csv(path + filename, index_col='Issue\nDate', 
					parse_dates=True, na_values=['nan'])
	df.drop('Maturity', axis=1, inplace=True)	# duplicate of 'Maturity\n(mm/dd/yyyy)' col
	# add usecols=['Date', 'Adj Close'] paramter to select column subset

	print df.head()


if __name__ == '__main__':
	main()