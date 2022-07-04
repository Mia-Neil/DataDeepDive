#!/usr/bin/env python3
import pandas as pd
import numpy as np

def main():
	college_data_path = "../data/all_ncaa.csv"
	college_df = pd.read_csv(college_data_path)
	college_df.loc[:,'Location'] = np.where(college_df['Host'] == college_df['Team'] , 'Home', 'Away')
	college_df = college_df.drop(['Opponents','Host'], axis=1)

	df = calculate_aa_scores(college_df)
	df.to_csv('../data/all_ncaa_aa.csv')


def calculate_aa_scores(df):
	meets = df.filter(['Meet ID','Team','Location','Season'], axis=1).drop_duplicates(subset=['Meet ID', 'Team'])

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
				season = meets.loc[(meets['Meet ID'] == meet_id)].iloc[0]['Season']
				aa_score = {
				"Meet ID": meet_id,
				"Team": team,
				"Name": index,
				"Gymnast ID": gymnast_id,
				"Event": "AA",
				"Score": '{:.3f}'.format(score),
				"Location": location,
				"Season": season
				}

				score = pd.DataFrame(aa_score, index=[0])
				df = pd.concat([df, score], ignore_index=True)
	return(df)

if __name__ == '__main__':
	main()
