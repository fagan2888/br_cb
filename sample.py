import pandas as pd
import numpy as np

filename1 = '2007-2008 DATA with ISIN.csv'
filename2 = '2009-2010 DATA with ISIN.csv'
filename3 = '2011 DATA with ISIN.csv'
filename4 = '2012 DATA with ISIN.csv'
filename5 = '2013 DATA with ISIN.csv'
filename6 = '2014 DATA with ISIN.csv'
filename7 = '2015 DATA with ISIN.csv'
filename8 = '2016 DATA with ISIN.csv'
path = 'C:\Users\Alex\Desktop\\br_cb_Data\\'

files = [filename1, filename2, filename3, filename4, filename5, filename6, filename7,
		filename8]

df_list = []

for file in files:
	df = pd.read_csv(path + file)
	df_list.append(df)

df_list[4]['temp'] = df_list[4]['Nation']
df_list[4]['temp2'] = df_list[4]['Nation.1'] 
df_list[4]['Nation'] = df_list[4]['temp2'] 
df_list[4]['Nation.1'] = df_list[4]['temp']

df_list[5]['temp'] = df_list[5]['Nation']
df_list[5]['temp2'] = df_list[5]['Nation.1'] 
df_list[5]['Nation'] = df_list[5]['temp2'] 
df_list[5]['Nation.1'] = df_list[5]['temp']


frames = []
for df in df_list:
	frames.append(df)

df_new = pd.concat(frames)
df_new.to_csv('2007-2016 DATA with ISIN.csv')
