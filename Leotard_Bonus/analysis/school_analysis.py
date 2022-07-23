#!/usr/bin/env python3
import pandas as pd
import numpy as np
import logging

def main():
	school_name_path = '../data/school_list.csv'
	schools = pd.read_csv(school_name_path)

	column_names = ['Team','Year','NQS','High Score','Home Average','Away Average', 'Location Delta', 'Scores >= 9.9']
	df_output = pd.DataFrame(columns = column_names)
	for year in range(2009,2023):
		if year == 2020:
			continue
		input_data_path = '../data/'+str(year)+'_rtn.csv'
		df = pd.read_csv(input_data_path)
		for index,row in schools.iterrows():
			school = row['Team']
			print("School: {}".format(school))
			school_scores = df.loc[df['Team'] == school]
			if school_scores.empty:
				continue
			meets = school_scores.filter(['Meet ID','Team','Location'], axis=1).drop_duplicates(subset=['Meet ID', 'Team'])
			meets = calculate_meet_scores(school_scores, meets)
			if meets.empty:
				continue
			meets = meets.sort_values(by=['Team Score'], ascending=[False])
			x = calculate_team_nqs_events(meets)
			nqs = x[0]
			home_ave = round(x[1],3)
			away_ave = round(x[2],3)
			location_delta = round((home_ave-away_ave),3)
			high_score = round(meets.iloc[0]['Team Score'],3)
			score_percentage = scores_over_9_9(school_scores)
			df_output.loc[len(df_output.index)] = [school, year, nqs['Team Score'], high_score, home_ave, away_ave, location_delta, score_percentage['Total']]

	df_output.to_csv('../data/output/school_data.csv')
	print(df_output)

def scores_over_9_9(school_scores):
	events = ['VT', 'UB', 'BB', 'FX']
	results = {}
	for event in events:
		curr_event_scores = school_scores.loc[school_scores['Event'] == event]
		curr_event_highs = curr_event_scores.loc[curr_event_scores['Score'] >= 9.9]
		percentage = curr_event_highs.shape[0] / curr_event_scores.shape[0] * 100
		results.update({event: round(percentage,1)})

	total_scores = school_scores.loc[(school_scores['Event'] != 'AA')]
	total_highs = total_scores.loc[total_scores['Score'] >= 9.9]
	total_percentage = total_highs.shape[0] / total_scores.shape[0] * 100
	results.update({'Total': round(total_percentage,1)})

	return(results)

def calculate_team_nqs_events(meets):
	team_results = meets.filter(['Team']).drop_duplicates(subset=['Team'])
	columns = ['VT','UB','BB','FX','Team Score']
	nqs_result = {}
	for index, row in team_results.iterrows():
		for event in columns:
			nqs_result.update({event:calculate_team_nqs(meets, row[0], event)})
		home_scores = meets.loc[meets['Location'] == 'Home']
		home_ave = 0
		for index, row in home_scores.iterrows():
			home_ave = home_ave + row['Team Score'] / home_scores.shape[0]
		away_scores = meets.loc[meets['Location'] == 'Away']
		away_ave = 0
		for index, row in away_scores.iterrows():
			away_ave = away_ave + row['Team Score'] / away_scores.shape[0]
	return [nqs_result, home_ave, away_ave]

def calculate_team_nqs(meets, school, event):
	df = meets.loc[(meets['Team'] == school)]

	if (df.shape[0] < 6):
		print("Not enough scores to calculate NQS for {} on {}".format(school, event))
		return 0

	df = df.sort_values(by=['Location', event], ascending=[True, False])

	if df.loc[(df['Location'] == 'Away')].shape[0] < 3:
		print("Not enough away scores to calculate NQS for {} on {}".format(school, event))
		return 0
	# Get top 3 away scores and re-sort dataframe
	nqs = df.head(3)

	df = df.drop(df.index[range(3)])
	df = df.sort_values(by=[event], ascending=False)
	# Get remaining top 3 scores
	nqs = pd.concat([nqs, df.head(3)])
	# Sort and drop highest score
	nqs = nqs.sort_values(by=[event], ascending=False)
	nqs = nqs.drop(nqs.index[0])

	nqs_average = 0
	for index, row in nqs.iterrows():
		nqs_average = nqs_average + row[event]/5
	return('{:.3f}'.format(nqs_average))
	return(nqs_average)

def calculate_meet_scores(df, meets):
	events = ['VT', 'UB', 'BB', 'FX']
	team_score = 0
	for index, row in meets.iterrows(): #For each meet
		skip_meet = False
		meet_id = row['Meet ID']
		# df_chunk: all scores for {meet_id}
		df_chunk = df[(df['Meet ID']==meet_id)]
		if df_chunk.shape[0] < 20:
			meets = meets.loc[(meets["Meet ID"] != meet_id)]
			continue
		for event in events: #For each event
			# df_chunk_event: all {event} scores for {meet_id}
			df_chunk_event = df_chunk.loc[(df['Event'] == event)].sort_values(by=['Score'])
			if df_chunk_event.shape[0] < 5:
				meets = meets.loc[(meets["Meet ID"] != meet_id)]
				skip_meet = True
			if df_chunk_event.shape[0] == 6:
				df_chunk_event = df_chunk_event.drop(df_chunk_event.index[0])
			if df_chunk_event.shape[0] > 6: # exhibitions
				drops = df_chunk_event.shape[0] - 5
				for i in range(0,drops):
					df_chunk_event = df_chunk_event.drop(df_chunk_event.index[0])

			if not skip_meet:
				score = np.around(df_chunk_event[(df_chunk_event['Event']==event)]["Score"].sum(),4)
				meets.loc[meets["Meet ID"] == meet_id, event] = score

		if not skip_meet:
			for event in events:
				team_score = team_score + meets.loc[meets['Meet ID'] == meet_id, event].iloc[0]
				meets.loc[meets["Meet ID"] == meet_id, "Team Score"] = team_score
		team_score = 0

	return meets


if __name__ == '__main__':
	main()
