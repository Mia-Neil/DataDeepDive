#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys

def main():
	input_path = "../data/all_ncaa_aa.csv"
	df = pd.read_csv(input_path)
	# for year in range(2009,2022):
	year = 2022
	df_year = df.loc[(df['Season'] == year)]
	output_path = '../data/'+str(year)+'_rtn.csv'
	df_year.to_csv(output_path)

if __name__ == '__main__':
	main()
