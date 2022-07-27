#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import random
from IPython.display import display

def get_top_markers(data, schools, years, cutoff):
	# Return dataframe with 'School' and 'Years', years is an array of years in top {cutoff}

	results = pd.DataFrame(columns=['School', 'Years'])
	data = data[['School', 'Year', 'Final Rank']]
	for school in schools:
		school_years = []
		school_ranks = data.loc[(data['School'] == school) & (data['Year'] > 2011)].sort_values(by=['Year'])
		for index,row in school_ranks.iterrows():
			if row['Final Rank'] <= cutoff:
				school_years.append(row['Year'])
		if school_years != []:
			results.loc[len(results.index)] = [school, school_years]

	return(results)

def get_recruits(all_data, school, year):
	# Return a list of athletes that competed for {school} in {year}
	athletes = []

	for key in all_data:
		data = all_data[key]
		data = data.loc[(data['School'] == school) & (data['Freshman'] == year)]
		data = data[['Name', 'School']]
		for index,row in data.iterrows():
			athletes.append(row['Name'])
	athletes = [*set(athletes)]
	return(athletes)

def get_ave_rating(data, school, year, roster):
	# Return a float value for the average recruit rating for {school} in {year}
	if roster == []:
		return(13)
	total = 0
	for athlete in roster:
		total = total + get_l10_rating(data, athlete)
	total = round(total/len(roster), 3)
	return(total)

def get_ave_delta_team(data, school, year, roster):
	if roster == []:
		return(13)
	total = 0
	for athlete in roster:
		total = total + get_ave_delta_individual(data, athlete)
	return(round(total/len(roster), 3))

def get_l10_rating(data, name):
	# Return a float value with the ave event score
	# Used high score and excluded values below 8

	VT = data['VT'].loc[data['VT']['Name'] == name].reset_index(drop=True).at[0,'L10_High_VT']
	UB = data['UB'].loc[data['UB']['Name'] == name].reset_index(drop=True).at[0,'L10_High_UB']
	BB = data['BB'].loc[data['BB']['Name'] == name].reset_index(drop=True).at[0,'L10_High_BB']
	FX = data['FX'].loc[data['FX']['Name'] == name].reset_index(drop=True).at[0,'L10_High_FX']
	scores = [VT, UB, BB, FX]

	total = 0
	count = 0
	for score in scores:
		if score > 8:
			total = total + score
			count = count + 1
	if count == 0:
		return(0)

	total = round(total / count, 3)
	return(total)

def get_ave_delta_individual(data, name):
	# Return a float value with the total event delta

	VT = data['VT'].loc[data['VT']['Name'] == name].reset_index(drop=True).at[0,'VT_delta']
	UB = data['UB'].loc[data['UB']['Name'] == name].reset_index(drop=True).at[0,'UB_delta']
	BB = data['BB'].loc[data['BB']['Name'] == name].reset_index(drop=True).at[0,'BB_delta']
	FX = data['FX'].loc[data['FX']['Name'] == name].reset_index(drop=True).at[0,'FX_delta']
	deltas = [VT, UB, BB, FX]

	total = 0
	for delta in deltas:
		if delta < 5 and delta > -5:
			total = total + delta
	return(round(total,3))

def filter_graph_table(table, schools):
	result = pd.DataFrame(index=table.index)
	for school in schools:
		result = result.join(table[school])

	return(result)

def create_graph(rows, cols, data_arr, title_arr, schools, output_path='graph.jpg'):
	# Print graph as specified
	num_plots = len(data_arr)
	assert(len(title_arr) == len(data_arr))
	assert(rows*cols >= len(title_arr))

	# If delta or ranking == 13, skip graphing this row, no recruits
	# for athlete_id in athletes_no_nqs:
    	# athlete_results = athlete_results.drop(athlete_results[athlete_results['Gymnast ID'] == athlete_id].index)

	display_years = [2013, 2015, 2017, 2019, 2021]

	fig, axes = plt.subplots(nrows=1, ncols=len(data_arr), constrained_layout=True)
	fig.suptitle('Temp Title', fontsize=27, fontweight='bold')
	fig.set_figwidth(23)#23
	fig.set_figheight(7)#13

	for i in range(0,num_plots):
		rank_data = data_arr[i]
		lowest_rank = rank_data.max().max()
		lowest_rank = 5 * round(rank_data.max().max()/5) + 5
		yticks = np.arange(0, lowest_rank, 5)
		yticks = np.where(yticks==0, 1, yticks)
		rank_data.plot(ax=axes[i], colormap='Set2', fontsize=10, xticks=display_years, lw=4, legend=False, yticks=yticks, zorder=1)
		if title_arr[i] == 'Final Rank':
			axes[i].invert_yaxis()
		axes[i].set_title(title_arr[i], y=1.05, pad=-14, size=17)

	# for school in schools:
	# 	color = axes[0,0].get_lines()[schools.index(school)].get_color()
	# 	# x,y = top_4_year(school, 'Final Rank')
	# 	x = ['2021', '2022', '2018']
	# 	y = ['Michigan', 'Oklahoma', 'UCLA']
	# 	x = np.array(x)
	# 	y = np.array(y)
	# 	axes[0,0].scatter(x, y, color=color, s=253, marker='D', zorder=2)

	# Figure Settings
	handles, labels = axes[0].get_legend_handles_labels()

	x = fig.legend(handles, labels, ncol=2, title='Schools', fancybox=True, shadow=True, loc='lower center', bbox_to_anchor=(0.5,-0.2), fontsize=15)

	plt.setp(x.get_title(),fontsize=20)
	fig.savefig(output_path, bbox_extra_artists=(x,), bbox_inches='tight', pad_inches=1)
	plt.close('all')
	return(True)
