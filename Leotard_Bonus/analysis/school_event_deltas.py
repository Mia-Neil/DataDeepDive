#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys
import requests
from bs4 import BeautifulSoup


def main():
	school_data_path = '../data/output/school_data.csv'
	school_data = pd.read_csv(school_data_path)
	conference_data = pd.read_csv('../data/school_list.csv')

	school_rank_data_path = '../data/output/school_final_ranks.csv'
	school_rank_data = pd.read_csv(school_rank_data_path)

	vt_data_path = '../data/output/athlete_data_VT_2.csv'
	vt_data = pd.read_csv(vt_data_path)
	vt_data = drop_zeros(vt_data, 'VT')

	ub_data_path = '../data/output/athlete_data_UB_2.csv'
	ub_data = pd.read_csv(ub_data_path)
	ub_data = drop_zeros(ub_data, 'UB')

	bb_data_path = '../data/output/athlete_data_BB_2.csv'
	bb_data = pd.read_csv(bb_data_path)
	bb_data = drop_zeros(bb_data, 'BB')

	fx_data_path = '../data/output/athlete_data_FX_2.csv'
	fx_data = pd.read_csv(fx_data_path)
	fx_data = drop_zeros(fx_data, 'FX')

	aa_data_path = '../data/output/athlete_data_AA_2.csv'
	aa_data = pd.read_csv(aa_data_path)
	aa_data = drop_zeros(aa_data, 'AA')

	output_list = []
	no_deltas_count = 0
	for index, row in school_data.iterrows():
		school = row['Team']
		conf_row = conference_data.loc[conference_data['Team'] == school]
		conf = conf_row['Conf'].to_string(index=False)
		year = row['Year']
		ranks = school_rank_data.loc[(school_rank_data['Team'] == school) & (school_rank_data['Year'] == year)]
		final_rank = float(ranks['Overall'].to_string(index=False))
		final_rank = int(final_rank)
		current_row = {
			'School': school,
			'Conference': conf,
			'Year': year,
			'Final Rank': final_rank,
			'NQS': row['NQS'],
			'Home Average': row['Home Average'],
			'Away Average': row['Away Average'],
			'Location Delta': row['Location Delta'],
			'Scores >= 9.9': row['Scores >= 9.9'],
			'VT Delta': get_delta(vt_data, school, year, 'VT'),
			'UB Delta': get_delta(ub_data, school, year, 'UB'),
			'BB Delta': get_delta(bb_data, school, year, 'BB'),
			'FX Delta': get_delta(fx_data, school, year, 'FX'),
			'AA Delta': get_delta(aa_data, school, year, 'AA')
		}

		# if current_row['VT Delta'] == 1000 and current_row['UB Delta'] == 1000 and \
		# 	current_row['BB Delta'] == 1000 and current_row['FX Delta'] == 1000 and \
		# 	current_row['AA Delta'] == 1000:
		# 	no_deltas_count = no_deltas_count + 1
		# else:
		# 	output_list.append(current_row)
		output_list.append(current_row)

	pd_output = pd.DataFrame.from_records(output_list)
	print(pd_output)
	pd_output.to_csv('../data/output/school_rank_delta.csv')

def drop_zeros(event_data, event):
	# print("Event: {}".format(event))
	# print("Initial Size: {}".format(event_data.shape[0]))
	col = 'NCAA_High_'+event
	event_data = event_data.loc[event_data[col] != 0]
	col = 'L10_High_'+event
	event_data = event_data.loc[event_data[col] != 0]
	# print("New Size: {}".format(event_data.shape[0]))
	return(event_data)

def get_delta(event_data, school, year, event):
	#Not enough values in one year
	data = event_data.loc[(event_data['School'] == school) & (event_data['Freshman'] == year)]
	# print(data)
	col_name = event+'_delta'
	num_rows = data.shape[0]
	if num_rows == 0:
		return 1000
	sum = 0
	for index, row in data.iterrows():
		sum = sum + row[col_name]
	avg_delta = round(sum/num_rows, 3)
	# print("Average Delta for {},{} on {}: {}".format(school, year, event, avg_delta))
	return(avg_delta)


if __name__ == '__main__':
	main()
