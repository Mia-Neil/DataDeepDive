#!/usr/bin/env python3
import pandas as pd
import numpy as np
import logging

logging.basicConfig(filename='log_output.txt',
                            filemode='w',
                            format='%(levelname)s %(message)s',
                            level=logging.DEBUG)
def main():
    logging.info("*************************************************")
    logging.info("Running NQS Calculator")
    logging.info("*************************************************")
    input_data_path = "prospect_rtn_data.csv"
    df = pd.read_csv(input_data_path)
    df.loc[:,'Location'] = np.where(df['Home Team'] == df['Team'] , 'Home', 'Away')
    df = df.drop(['Meet Date','Away Team(s)','Home Team'], axis=1)

    score_array = calculate_aa_scores(df)
    df = score_array[0]
    meets = score_array[1]

    # Create athlete output table
    athlete_results = df.filter(['Gymnast ID','Name','Team'], axis=1)
    athlete_results = athlete_results.drop_duplicates(subset=['Gymnast ID'])
    athlete_results["VT"] = 0
    athlete_results["UB"] = 0
    athlete_results["BB"] = 0
    athlete_results["FX"] = 0
    athlete_results["AA"] = 0

    athletes_no_nqs = []
    for index, row in athlete_results.iterrows():
        athlete_results.at[index, 'VT'] = calculate_athlete(df, row[1], 'VT')
        athlete_results.at[index, 'UB'] = calculate_athlete(df, row[1], 'UB')
        athlete_results.at[index, 'BB'] = calculate_athlete(df, row[1], 'BB')
        athlete_results.at[index, 'FX'] = calculate_athlete(df, row[1], 'FX')
        athlete_results.at[index, 'AA'] = calculate_athlete(df, row[1], 'AA')
    # Drop athletes who have no NQS rankings on any event
        if (athlete_results.at[index, 'VT'] == 0) & \
        (athlete_results.at[index, 'UB'] == 0) & \
        (athlete_results.at[index, 'BB'] == 0) & \
        (athlete_results.at[index, 'FX'] == 0) & \
        (athlete_results.at[index, 'AA'] == 0):
            logging.info("{} has no events with an NQS. Dropping from results table".format(row[1]))
            athletes_no_nqs.append(row[0])
    for athlete_id in athletes_no_nqs:
        athlete_results = athlete_results.drop(athlete_results[athlete_results['Gymnast ID'] == athlete_id].index)

    meets = calculate_meet_scores(df, meets)
    team_results = calculate_team_nqs_events(meets)
    logging.info("*************************************************")
    logging.info("Team Results (full results in output file)")
    logging.info(team_results)
    logging.info("*************************************************")
    logging.info("Individual Results (full results in output file)")
    logging.info(athlete_results)
    logging.info("*************************************************")
    team_results.to_csv('output/team_results.csv')
    athlete_results.to_csv('output/athlete_results.csv')
    df.to_csv('output/modified_input.csv')


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
    return [df, meets]

def calculate_team_nqs_events(meets):
    team_results = meets.filter(['Team']).drop_duplicates(subset=['Team'])
    columns = ['VT','UB','BB','FX','Team Score']
    for index, row in team_results.iterrows():
        for event in columns:
            team_results.at[index, event] = calculate_team_nqs(meets, row[0], event)
    return team_results

def calculate_team_nqs(meets, school, event):
    df = meets.loc[(meets['Team'] == school)]
    if (df.shape[0] < 6):
        logging.info("Not enough scores to calculate NQS for {} on {}".format(school, event))
        return 0

    df = df.sort_values(by=['Location', event], ascending=[True, False])

    if df.loc[(df['Location'] == 'Away')].shape[0] < 3:
        logging.info("Not enough away scores to calculate NQS for {} on {}".format(school, event))
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
        for event in events: #For each event
            meet_id = row['Meet ID']
            # df_chunk: all scores for {meet_id}
            df_chunk = df[(df['Meet ID']==meet_id)]
            # df_chunk_event: all {event} scores for {meet_id}
            df_chunk_event = df_chunk.loc[(df['Event'] == event)].sort_values(by=['Score'])
            if df_chunk_event.shape[0] == 6:
                df_chunk_event = df_chunk_event.drop(df_chunk_event.index[0])
            score = np.around(df_chunk_event[(df_chunk_event['Event']==event)]["Score"].sum(),4)

            meets.loc[meets["Meet ID"] == meet_id, event] = score
        for event in events: #For each event
            # Calculate team score for the meet
            team_score = team_score + meets.loc[meets['Meet ID'] == meet_id, event].iloc[0]
            meets.loc[meets["Meet ID"] == meet_id, "Team Score"] = team_score
        team_score = 0
    return meets

def calculate_athlete(df, athlete_name, event):
    # Make sure there are enough scores
    df_athlete = pd.DataFrame()
    df_athlete = df.loc[(df['Name'] == athlete_name) & (df['Event'] == event)]
    if (df_athlete.shape[0] < 6):
        logging.info("Not enough scores to calculate NQS for {} on {}".format(athlete_name, event))
        return 0

    df_athlete = df_athlete.sort_values(by=['Location', 'Score'], ascending=[True, False])
    # Make sure there are enough away scores
    if df_athlete.loc[(df_athlete['Location'] == 'Away')].shape[0] < 3:
        logging.info("Not enough away scores to calculate NQS for {} on {}".format(athlete_name, event))
        return 0

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
        nqs_average = nqs_average + float(row[5])/5

    return('{:.3f}'.format(nqs_average))


if __name__ == '__main__':
    main()
