#!/usr/bin/env python3
import pandas as pd
import numpy as np
import logging

def main():
	input_data_path = "../data/mms_since_2011.csv"
	df = pd.read_csv(input_data_path)
	athletes = df.filter(['MMS ID','MMS Name'], axis=1).drop_duplicates(subset=['MMS ID'])
	print(athletes)
	athletes.to_csv('../data/athlete_ids.csv')


if __name__ == '__main__':
	main()
