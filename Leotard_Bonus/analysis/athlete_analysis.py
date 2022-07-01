#!/usr/bin/env python3
import pandas as pd
import numpy as np

def main():
	print("************************************************")
	print("************ Athlete Analysis ******************")
	print("************************************************")
	mms_data_path = "../data/mms_since_2011.csv"
	df = pd.read_csv(mms_data_path)
	df = df.drop(['Unique ID','MMS Club','Meet ID','Meet Name','Exclude?'], axis=1)

	# college_data_path = "../data/rtn_2022.csv"
	college_data_path = "../data/ncaa_scores_09-22.csv"
	college_df = pd.read_csv(college_data_path)
	college_df.loc[:,'Location'] = np.where(college_df['Host'] == college_df['Team'] , 'Home', 'Away')
	print("finished marking home away")
	college_df = college_df.drop(['Opponents','Host'], axis=1)

	# name = 'Bowers, Jordan'
	name = 'Wojcik, Natalie'
	name_split = name.split(", ")
	if len(name_split) > 2:
		sys.exit("Failed on {}".format(name))
	else:
		name_forwards = name_split[1]+ ' ' + name_split[0]

	# Level 10
	mms_aa_scores = mms_aa_nqs(df, name)
	print("Done with l10")
	# College
	df = calculate_aa_scores(college_df)
	print("done with AA scores")
	college_scores = calculate_athlete(df, name_forwards, 'AA')
	school = college_scores['school']

	print("Name: {}".format(name_forwards))
	print("School: {}".format(school))
	print("*************************************")
	print("Level Ten Scores")
	print("High : {}".format(mms_aa_scores[1]))
	print("'NQS': {:.4f}".format(mms_aa_scores[0]))
	print("*************************************")
	print("College Scores")
	if 'num_scores' in college_scores:
		print("No college AA scores")
	else:
		if 'nqs' in college_scores:
			print("NQS: {:.4f}".format(college_scores['nqs']))
		print("High: {:.4f}".format(college_scores['high']))
		print("Ave: {:.4f}".format(college_scores['ave']))

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

	return([nqs_average, high_score])

def calculate_aa_scores(df):
	meets = df.filter(['Meet ID','Team','Location'], axis=1).drop_duplicates(subset=['Meet ID', 'Team'])

	for index, row in meets.iterrows():
		meet_id = row['Meet ID']
		location = row['Location']
		# df_chunk: [all scores from a given Meet ID]
		df_chunk = df[(df['Meet ID']==meet_id)]

		# If athlete has 4 scores in the meet, calculate AA Score
		for index, value in df_chunk['Name'].value_counts().items():
			if value == 4:
				score = float(df_chunk[(df_chunk['Name']==index)]["Score"].sum())
				gymnast_id = df_chunk.loc[(df_chunk['Name'] == index)].iloc[0]['Gymnast ID']
				team = meets.loc[(meets['Meet ID'] == meet_id)].iloc[0]['Team']

				aa_score = {
				"Meet ID": meet_id,
				"Team": team,
				"Name": index,
				"Gymnast ID": gymnast_id,
				"Event": "AA",
				"Score": '{:.3f}'.format(score),
				"Location": location
				}

				score = pd.DataFrame(aa_score, index=[0])
				df = pd.concat([df, score], ignore_index=True)
	return(df)

def calculate_athlete(df, athlete_name, event):
	df_athlete = pd.DataFrame()
	df_athlete = df.loc[(df['Name'] == athlete_name) & (df['Event'] == event)]
	results = {}
	school = df_athlete.iloc[0][6]
	results.update({'school':school})
	num_rows = df_athlete.shape[0]
	if num_rows == 0:
		print("No scores available for {} - {}".format(athlete_name, event))
		results.update({'num_scores': 0})
		return(results)
	# Calculate high and Average
	df_athlete = df_athlete.sort_values(by=['Score'], ascending=False)
	high = float(df_athlete.iloc[0][9])
	ave = 0
	for index, row in df_athlete.iterrows():
		ave = ave + float(row[9])

	ave = round(ave/num_rows, 4)
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

	nqs = round(nqs_average, 4)
	results.update({'nqs':nqs})
	# results = {
	# 	"nqs": nqs,
	# 	"high": high,
	# 	"ave": ave
	# }
	return(results)

if __name__ == '__main__':
	main()
