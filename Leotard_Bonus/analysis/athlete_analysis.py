#!/usr/bin/env python3
import pandas as pd
import numpy as np

def main():
	# Gather setup import files
	mms_data_path = "../data/mms_since_2011.csv"
	df = pd.read_csv(mms_data_path)
	df = df.drop(['Unique ID','MMS Club','Meet ID','Meet Name','Exclude?'], axis=1)

	college_data_path = "../data/all_ncaa_w_aa.csv"
	college_df = pd.read_csv(college_data_path)
	college_df = college_df.drop(['Unnamed: 0'], axis=1)

	athlete_name_path = '../data/mms_top_100.csv'
	athlete_names = pd.read_csv(athlete_name_path)
	athlete_names = athlete_names.drop(['place', 'score', 'year'], axis=1)
	athlete_names = athlete_names.drop_duplicates(ignore_index=True)

	output_list = []

	for index, row in athlete_names.iterrows():
		name = row['name']
		name_split = name.split(", ")
		if len(name_split) > 2:
			sys.exit("Failed on {}".format(name))
		else:
			name_forwards = name_split[1]+ ' ' + name_split[0]

		# Level 10
		mms_aa_scores = mms_aa_nqs(df, name)
		college_scores = calculate_athlete(college_df, name_forwards, 'AA')
		school = college_scores['school']

		if 'num_scores' not in college_scores.keys():
			current_athlete_output = {
				'Name': name_forwards,
				'School': school,
				'L10_NQS': mms_aa_scores[0],
				'L10_High': mms_aa_scores[1],
				'NCAA_Average': college_scores['ave'],
				'NCAA_High': college_scores['high']
			}
			if 'nqs' in college_scores.keys():
				current_athlete_output.update({'NCAA_NQS': college_scores['nqs']})
			else:
				current_athlete_output.update({'NCAA_NQS': 0})
			output_list.append(current_athlete_output)

	output = pd.DataFrame.from_records(output_list)
	output.to_csv('../data/athlete_data.csv')
	print(output)


def mms_aa_nqs(df, name):
	# Get all of athlete's level 10 scores
	athlete_results = df.loc[(df['MMS Name'] == name) & (df['Level'] == '10')]
	# Drop any meets with a 0
	athlete_results = athlete_results[(athlete_results.VT != 0) & (athlete_results.UB != 0) & (athlete_results.BB !=0) & (athlete_results.FX !=0)]
	num_scores = athlete_results.shape[0]
	athlete_results = athlete_results.sort_values(by=['AA'], ascending=[False])
	high_score = athlete_results.iloc[0][8]
	num_drops = round(num_scores/10)
	if num_scores > 5:
		# Drop highest and lowest 10% of scores
		for i in range(0,num_drops):
			curr_size = athlete_results.shape[0]
			athlete_results = athlete_results.drop(athlete_results.index[curr_size-1])
			athlete_results = athlete_results.drop(athlete_results.index[0])

	nqs_average = 0
	for index, row in athlete_results.iterrows():
		nqs_average = nqs_average + float(row[8])/athlete_results.shape[0]
	return([round(nqs_average, 3), high_score])

def calculate_athlete(df, athlete_name, event):
	df_athlete = pd.DataFrame()
	df_athlete = df.loc[(df['Name'] == athlete_name) & (df['Event'] == event)]
	results = {}
	if df_athlete.empty:
		# print("No AA Scores: {}".format(athlete_name))
		results.update({'num_scores': 0})
		results.update({'school': 'not available'})
		return(results)
	school = df_athlete.iloc[0][6]
	results.update({'school':school})
	num_rows = df_athlete.shape[0]
	# Calculate high and Average
	df_athlete = df_athlete.sort_values(by=['Score'], ascending=False)
	high = float(df_athlete.iloc[0][9])
	ave = 0
	for index, row in df_athlete.iterrows():
		ave = ave + float(row[9])

	ave = round(ave/num_rows, 3)
	results.update({'high':high})
	results.update({'ave':ave})

	if df_athlete.shape[0] < 6:
		return(results)

	df_athlete = df_athlete.sort_values(by=['Location', 'Score'], ascending=[True, False])

	# Make sure there are enough away scores
	if df_athlete.loc[(df_athlete['Location'] == 'Away')].shape[0] < 3:
		return(results)

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
	results.update({'nqs':nqs})

	return(results)

if __name__ == '__main__':
	main()
