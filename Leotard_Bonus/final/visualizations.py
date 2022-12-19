#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import random
from helper import *
import itertools
from itertools import product
from IPython.display import display


def main():

	# Open Files
	school_data = pd.read_csv('../data/output/school_rank_delta.csv')
	athlete_vt = pd.read_csv('../data/output/athlete_data_VT_2.csv')
	athlete_ub = pd.read_csv('../data/output/athlete_data_UB_2.csv')
	athlete_bb = pd.read_csv('../data/output/athlete_data_BB_2.csv')
	athlete_fx = pd.read_csv('../data/output/athlete_data_FX_2.csv')
	athlete_aa = pd.read_csv('../data/output/athlete_data_AA_2.csv')
	athlete_all_events = {
		'VT' : athlete_vt,
		'UB' : athlete_ub,
		'BB' : athlete_bb,
		'FX' : athlete_fx,
		'AA' : athlete_aa
	}

	years = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022]
	school_data = school_data.loc[(school_data['Year'] > 2011) & (school_data['School'] != 'Wilson College')]
	schools = school_data[['School']].drop_duplicates(subset='School', inplace=False).reset_index(drop=True)
	schools_arr = schools["School"].to_numpy()

	# Build required DataFrames

	school_data = school_data[['Year', 'School', 'Final Rank', 'Scores >= 9.9', 'Location Delta']]

	school_data['Ave Athlete Delta'] = np.nan
	school_data['Ave Roster Rating'] = np.nan

	use_saved_data = True
	if use_saved_data:
		school_data = pd.read_csv('intermediate_data/school_data.csv')
	else:
		for index,row in school_data.iterrows():
			year = row['Year']
			school = row['School']
			roster = get_recruits(athlete_all_events, school, year)
			ave_athlete_delta = get_ave_delta_team(athlete_all_events, school, year, roster)
			ave_roster_rating = get_ave_rating(athlete_all_events, school, year, roster)
			school_data.at[index, 'Ave Athlete Delta'] = ave_athlete_delta
			school_data.at[index, 'Ave Roster Rating'] = ave_roster_rating
			school_data.to_csv('intermediate_data/school_data.csv')

	values = ['Final Rank','Scores >= 9.9','Location Delta','Ave Athlete Delta','Ave Roster Rating']
	school_dfs = []

	for value in values:
		school_graph = pd.DataFrame(columns=schools_arr)
		for year, school in itertools.product(years,schools_arr):
			df = school_data.loc[(school_data['Year'] == year) & (school_data['School'] == school)].reset_index(drop=True)
			if not df.empty:
				datapoint = df.at[0,value]
				school_graph.at[year,school] = datapoint
		school_graph.dropna(axis=1, how='all')
		school_dfs.append(school_graph)

	# Create graphs
	top_schools = ['Oklahoma','Florida','Michigan','LSU','UCLA','Utah','Alabama']
	interesting_schools = ['California', 'Michigan State', 'Stanford']
	mid_schools = get_range_schools(school_data, 40, 43, 'Final Rank')
	mid_plus = mid_schools + interesting_schools
	# combination = top_schools + mid_plus

	highest_deltas = get_range_schools(school_data, 1, 4, 'Ave Athlete Delta')
	med_deltas = get_range_schools(school_data, 40, 43, 'Ave Athlete Delta')
	mid_plus = med_deltas + interesting_schools
	combination = highest_deltas + med_deltas + interesting_schools

	# highest_roster_rating = get_range_schools(school_data, 1, 4, 'Ave Roster Rating')
	# mid_roster_rating = get_range_schools(school_data, 40, 43, 'Ave Roster Rating') + interesting_schools
	# combination = highest_roster_rating + mid_roster_rating

	graph_to_use = combination
	graph_to_use = sorted(graph_to_use)
	data_filtered = filter_graph_table(school_dfs[3], graph_to_use)
	create_single_graph(data_filtered, "Ave Athlete Delta", graph_to_use, 'Athlete Score Delta')


if __name__ == '__main__':
	main()
