#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys

def main():
	# Gather setup import files
	mms_data_path = "../data/mms_since_2011.csv"
	df = pd.read_csv(mms_data_path)
	df = df.drop(['Unique ID','MMS Club','Meet ID','Meet Name','Exclude?'], axis=1)

	college_data_path = "../data/all_ncaa_aa.csv"
	college_df = pd.read_csv(college_data_path)
	college_df = college_df.drop(['Unnamed: 0'], axis=1)

	name_data_path = '../data/c-mms_athlete_names.csv'
	# name_data_path = 'athlete_list_test.csv'
	athlete_names = pd.read_csv(name_data_path)
	athlete_names = athlete_names.drop_duplicates(ignore_index=True)

	output_list = []
	events = ['AA','VT','UB','BB','FX']
	for index, row in athlete_names.iterrows():
		name = row['MMS Name']
		name_split = name.split(", ")
		if len(name_split) > 2:
			sys.exit("Failed on {}".format(name))
		else:
			name_forwards = name_split[1]+ ' ' + name_split[0]
		print("Current Athlete: {}".format(name_forwards))
		# Level 10
		mms_scores = mms_aa_nqs(df, name)

		college_scores = calculate_athlete(college_df, name_forwards)
		if college_scores == 0:
			college_scores = {
				'num_scores': 0,
				'school': 'na',
				'year': 'na'
			}
		if 'num_scores' not in college_scores.keys():
			school = college_scores['school']
			year = college_scores['year']
			current_athlete_output = {
				'Name': name_forwards,
				'School': school,
				'L10_High_AA': mms_scores['mms_aa_high'],
				'L10_Ave_AA': mms_scores['mms_aa_ave'],
				'L10_High_VT': mms_scores['mms_vt_high'],
				'L10_Ave_VT': mms_scores['mms_vt_ave'],
				'L10_High_UB': mms_scores['mms_ub_high'],
				'L10_Ave_UB': mms_scores['mms_ub_ave'],
				'L10_High_BB': mms_scores['mms_bb_high'],
				'L10_Ave_BB': mms_scores['mms_bb_ave'],
				'L10_High_FX': mms_scores['mms_fx_high'],
				'L10_Ave_FX': mms_scores['mms_fx_ave'],
				'Freshman': college_scores['year'],
				'NCAA_High_AA': college_scores['AA_high'],
				'NCAA_Ave_AA': college_scores['AA_ave'],
				'NCAA_High_VT': college_scores['VT_high'],
				'NCAA_Ave_VT': college_scores['VT_ave'],
				'NCAA_High_UB': college_scores['UB_high'],
				'NCAA_Ave_UB': college_scores['UB_ave'],
				'NCAA_High_BB': college_scores['BB_high'],
				'NCAA_Ave_BB': college_scores['BB_ave'],
				'NCAA_High_FX': college_scores['FX_high'],
				'NCAA_Ave_FX': college_scores['FX_ave']
			}

			for event in events:
				key_name = event + '_nqs'
				delta_key_name = event + '_delta'
				# delta = round(current_athlete_output['NCAA_Ave_'+event]-current_athlete_output['L10_Ave_'+event],3)
				delta = round(current_athlete_output['NCAA_High_'+event]-current_athlete_output['L10_High_'+event],3)
				if key_name in college_scores.keys():
					current_athlete_output.update({key_name: college_scores[key_name]})
				else:
					current_athlete_output.update({key_name: 0})
				current_athlete_output.update({delta_key_name: delta})

			output_list.append(current_athlete_output)

	# Setup output files
	for event in events:
		event_fields = ('Name','School','L10_High_'+event, 'L10_Ave_'+event, 'Freshman', 'NCAA_High_'+event, 'NCAA_Ave_'+event, event+'_nqs', event+'_delta')
		curr_event_output_list = []
		for item in output_list:
			curr_event_output_list.append({k:item[k] for k in event_fields if k in item})
		event_output = pd.DataFrame.from_records(curr_event_output_list)
		event_output.to_csv('../data/output/athlete_data_'+event+'_2.csv')
	print("*** Completed Successfully ***")

def mms_aa_nqs(df, name):
	events = ['AA','VT','UB','BB','FX']
	results = {
		'mms_aa_ave':0,
		'mms_aa_high':0,
		'mms_vt_ave':0,
		'mms_vt_high':0,
		'mms_ub_ave':0,
		'mms_ub_high':0,
		'mms_bb_ave':0,
		'mms_bb_high':0,
		'mms_fx_ave':0,
		'mms_fx_high':0
	}
	athlete_results = df.loc[(df['MMS Name'] == name) & (df['Level'] == '10')]
	# num_scores = athlete_results.shape[0]
	for event in events:
		high_key = 'mms_'+event.lower()+'_high'
		ave_key = 'mms_'+event.lower()+'_ave'
		athlete_events = athlete_results.loc[(athlete_results[event] != 0)]
		athlete_events = athlete_events.sort_values(by=[event], ascending=[False])
		num_scores = athlete_events.shape[0]
		if athlete_events.empty:
			results.update({high_key:0,ave_key:0})
			continue
		high_score = athlete_events.iloc[0][event]
		num_drops = round(num_scores/10)
		if num_scores > 5:
			# Drop highest and lowest 10% of scores
			for i in range(0,num_drops):
				curr_size = athlete_events.shape[0]
				athlete_events = athlete_events.drop(athlete_events.index[curr_size-1])
				athlete_events = athlete_events.drop(athlete_events.index[0])

		nqs_average = 0
		for index, row in athlete_events.iterrows():
			nqs_average = nqs_average + float(row[event])/athlete_results.shape[0]
		results.update({high_key:high_score,ave_key:nqs_average})
	return(results)

def calculate_athlete(df, athlete_name):
	events = ['AA', 'VT', 'UB', 'BB', 'FX']
	results = {'AA_nqs': 0, 'VT_nqs': 0, 'UB_nqs': 0, 'BB_nqs': 0, 'FX_nqs': 0}
	df_athlete = pd.DataFrame()
	sorted_year = df.loc[df['Name'] == athlete_name]
	if sorted_year.empty:
		return(0)

	sorted_year = sorted_year.sort_values(by=['Season'], ascending=True)
	season = sorted_year.iloc[0]['Season']
	results.update({'year': int(season)})

	school = sorted_year.iloc[0]['Team']
	results.update({'school':school})
	for event in events:
		key1 = event+'_high'
		key2 = event+'_ave'
		df_athlete = sorted_year.loc[(sorted_year['Name'] == athlete_name) &
			(sorted_year['Event'] == event)]

		if df_athlete.empty:
			results.update({key1:0})
			results.update({key2:0})
			continue

		num_rows = df_athlete.shape[0]

		# Calculate high and Average
		df_athlete = df_athlete.sort_values(by=['Score'], ascending=False)
		high = float(df_athlete.iloc[0][9])
		ave = 0
		for index, row in df_athlete.iterrows():
			ave = ave + float(row[9])

		ave = round(ave/num_rows, 3)

		results.update({key1:high})
		results.update({key2:ave})

		if df_athlete.shape[0] >= 6:
			df_athlete = df_athlete.sort_values(by=['Location', 'Score'], ascending=[True, False])
			# Make sure there are enough away scores
			if df_athlete.loc[(df_athlete['Location'] == 'Away')].shape[0] < 3:
				continue
			# Get top 3 away scores and re-sort dataframe
			nqs = df_athlete.head(3)
			df_athlete = df_athlete.drop(df_athlete.index[range(3)])
			df_athlete = df_athlete.sort_values(by=['Score'], ascending=False)
			# Get remaining top 3 scores
			nqs = pd.concat([nqs, df_athlete.head(3)])
			# Sort and drop highest score
			nqs = nqs.sort_values(by=['Score'], ascending=False)
			nqs = nqs.drop(nqs.index[0])

			nqs_average = 0
			for index, row in nqs.iterrows():
				nqs_average = nqs_average + float(row[9])/5

			nqs = round(nqs_average, 3)
			key3 = event+'_nqs'

			results.update({key3:nqs})

	return(results)

if __name__ == '__main__':
	main()
