#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys

def main():
	input_path = "../data/all_ncaa_aa.csv"
	df = pd.read_csv(input_path)
	df = df.filter(['Team']).drop_duplicates(subset=['Team'])
	print(df)
	df.to_csv('../data/school_list.csv')

if __name__ == '__main__':
	main()
