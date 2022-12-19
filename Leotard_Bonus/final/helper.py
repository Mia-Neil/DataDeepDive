#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import random
from IPython.display import display
import matplotlib as mpl
from matplotlib import colors
from matplotlib.ticker import PercentFormatter


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
		return(np.NaN)
	total = 0
	num_zeros = 0
	for athlete in roster:
		curr_rating = get_l10_rating(data, athlete)
		if curr_rating == 0:
			num_zeros = num_zeros+1
		else:
			total = total + curr_rating
	if num_zeros != 0:
		if len(roster) == 1:
			return np.NaN
		else:
			total = round(total/(len(roster)-num_zeros), 3)
	else:
		total = round(total/len(roster), 3)
	return(total)

def get_ave_delta_team(data, school, year, roster):
	if roster == []:
		return(np.NaN)
	total = 0
	num_zeros = 0
	for athlete in roster:
		# if school == 'UCLA' and year == 2014:
		# 	print("Delta: {}\n".format(get_ave_delta_individual(data, athlete)))
		curr_delta = get_ave_delta_individual(data, athlete)
		if curr_delta == 0:
			num_zeros = num_zeros + 1
		else:
			total = total + curr_delta
	if num_zeros !=0:
		if len(roster) == 1:
			return np.NaN
		else:
			total = round(total/len(roster)-num_zeros,3)
	else:
		total = round(total/len(roster), 3)
	return(total)

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

def get_markers(school, field, cutoff):
	x=[]
	y=[]
	data_path = 'intermediate_data/school_data.csv'
	data = pd.read_csv(data_path)
	if field == 'Final Rank':
		data = data[['School', 'Year', field]]
	else:
		data = data[['School', 'Year', 'Final Rank', field]]
	school_ranks = data.loc[(data['School'] == school) & (data['Year'] > 2011)].sort_values(by=['Year'])
	for index,row in school_ranks.iterrows():
		if row['Final Rank'] <= cutoff:
			x.append(row['Year'])
			y.append(row[field])

	return x,y

def create_graph(rows, cols, data_arr, title_arr, schools, output):
	num_plots = len(data_arr)
	assert(len(title_arr) == num_plots)
	assert(rows*cols >= num_plots)
	display_years = [2013, 2015, 2017, 2019, 2021]

	fig, axes = plt.subplots(nrows=rows, ncols=cols, constrained_layout=True)
	fig.suptitle(output, fontsize=27, fontweight='bold')
	fig.set_figwidth(27)
	fig.set_figheight(13)

	i=0
	for x in range(0, rows):
		for y in range(0, cols):
			rank_data = data_arr[i]
			if title_arr[i] == 'Final Rank':
				lowest_rank = rank_data.max().max()
				lowest_rank = 5 * round(rank_data.max().max()/5) + 5
				yticks = np.arange(0, lowest_rank, 5)
				yticks = np.where(yticks==0, 1, yticks)
				rank_data.plot(ax=axes[x,y], colormap='tab10', fontsize=10, xticks=display_years, lw=4, legend=False, marker='.', markersize=7, yticks=yticks, zorder=1)
				axes[x,y].invert_yaxis()
			else:
				rank_data.plot(ax=axes[x,y], colormap='tab10', fontsize=10, xticks=display_years, lw=4, legend=False, marker='.', markersize=7, zorder=1)

			for school in schools:
				color = axes[x,y].get_lines()[schools.index(school)].get_color()
				a,b = get_markers(school,title_arr[i],3)
				a = np.array(a)
				b = np.array(b)
				axes[x,y].scatter(a, b, color=color, s=235, marker='D', zorder=2)
			# print(title_arr[i])
			axes[x,y].set_title(title_arr[i], y=1.05, pad=-14, size=17)
			i = i+1
			# if i == len(data_arr) - 1:
			# 	fig.delaxes(axes[x,y+1])
			# 	break
			# else:
			# 	i = i + 1

	# Figure Settings
	handles, labels = axes[0,0].get_legend_handles_labels()

	legend = fig.legend(handles, labels, ncol=2, title='Schools', fancybox=True, shadow=True, loc='lower center', bbox_to_anchor=(0.5,-0.2), fontsize=15)

	plt.setp(legend.get_title(),fontsize=20)
	fig.savefig(output+'.jpg', bbox_extra_artists=(legend,), bbox_inches='tight', pad_inches=1)
	plt.close('all')

def create_single_graph(data, field, schools, output, highlight=None):
	color_mapping = {
		"Oklahoma":"springgreen",
		"Florida":"darkviolet",
		"Michigan":"royalblue",
		"LSU":"cyan",
		"UCLA":"orangered",
		"Utah":"red",
		"Alabama":"gold",
		"California":"violet",
		"Pittsburgh":"lightskyblue",
		"Western Michigan":"pink",
		"UC Davis":"orange",
		"Eastern Michigan":"coral",
		"Michigan State":"olivedrab",
		"Stanford":"darkblue"
	}

	colors = ['yellowgreen', 'rosybrown', 'forestgreen', 'plum', 'chocolate', 'darkseagreen', 'mediumvioletred']

	display_years = [2013, 2015, 2017, 2019, 2021]

	if len(data.columns) > 14:
		print("Too many schools to map")

	fig = plt.figure(figsize=(7,5))

	if field == 'Final Rank':
		lowest_rank = data.max().max()
		lowest_rank = 5 * round(lowest_rank/5) + 5
		yticks = np.arange(0, lowest_rank, 5)
		yticks = np.where(yticks==0, 1, yticks)

	for idx, col in enumerate(data.columns):
		if highlight: #highlight one school
			if schools[idx] == highlight:
				ax = data[col].squeeze().plot.line(color='dodgerblue', label=data.columns[idx], xticks=display_years, lw=4, zorder=3)
				highlight_index = idx
			else:
				ax = data[col].squeeze().plot.line(color='slategray', label=data.columns[idx], xticks=display_years, zorder=1)
		else:
			if schools[idx] in color_mapping:
				ax = data[col].squeeze().plot.line(color=color_mapping[schools[idx]], label=data.columns[idx], xticks=display_years, zorder=1)
			else:
				color_index = random.randint(0,6)
				ax = data[col].squeeze().plot.line(color=colors[color_index], label=data.columns[idx], xticks=display_years, zorder=1)

	for school in schools:
		color = ax.get_lines()[schools.index(school)].get_color()
		a,b = get_markers(school,field,3)
		ax.scatter(np.array(a), np.array(b), color=color, s=43, marker='D', zorder=2)

	if field == 'Final Rank':
		ax.invert_yaxis()
		ax.set_yticks(yticks, minor=False)
	if field == 'Scores >= 9.9':
		ax.yaxis.set_major_formatter(PercentFormatter(xmax = 100))
		ax.set_ylabel("Percentage of Scores")

	ax.set_title(output, fontsize=20, fontweight='bold')

	if highlight:
		handles, labels = ax.get_legend_handles_labels()
		legend = ax.legend([handles[highlight_index]], [highlight], ncol=2, title='Highlighted School', fancybox=True, shadow=True, loc='lower center', bbox_to_anchor=(0.5,-0.3), fontsize=9)
	else:
		handles, labels = ax.get_legend_handles_labels()
		legend_cols = round(len(data.columns)/4)
		legend = ax.legend(handles, labels, ncol=legend_cols, title='Schools', fancybox=True, shadow=True, loc='lower center', bbox_to_anchor=(0.5,-0.4), fontsize=7)

	plt.setp(legend.get_title(),fontsize=13)

	ax.figure.savefig('article_figures/'+output+'.jpg', bbox_extra_artists=(legend,), bbox_inches='tight', pad_inches=1)
	plt.close('all')

def get_range_schools(data, high, low, field):
	years = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022]
	schools = data.drop_duplicates(subset='School', inplace=False, ignore_index=False)
	schools = schools[['School']]
	lines = []
	for index,row in schools.iterrows():
		ranking = data.loc[data['School'] == row['School']]
		ranking = ranking[['School', 'Year', field]]
		ave_value = round(ranking[field].mean(skipna=True),3)
		current_line = {
			'school':row['School'],
			'ave_value':ave_value
		}
		lines.append(current_line)

	results = pd.DataFrame.from_records(lines)
	if field == 'Final Rank':
		results = results.sort_values(by=['ave_value']).reset_index(drop=True).iloc[high-1:low]
	else:
		results = results.sort_values(by=['ave_value'],ascending=[False]).reset_index(drop=True).iloc[high-1:low]
	results_arr = []
	for index,row in results.iterrows():
		results_arr.append(row['school'])

	return(results_arr)

def create_graph_1d(cols, data, title_arr, schools, output):
	# num_plots = len(data_arr)
	display_years = [2013, 2015, 2017, 2019, 2021]

	fig, axes = plt.subplots(nrows=1, ncols=cols, constrained_layout=True, sharex=True)
	fig.suptitle(output, fontsize=27, fontweight='bold')
	fig.set_figwidth(27)
	fig.set_figheight(13)
	# schools = schools_arr[0] + schools_arr[1]

	lowest_rank = 5 * round(data.max().max()/5) + 5
	yticks = np.arange(0, lowest_rank, 5)
	yticks = np.where(yticks==0, 1, yticks)

	# Rank
	# data = data_arr[0]
	axes[0].set_yticks(yticks)
	data.plot(ax=axes[0], colormap='Set3', fontsize=10, xticks=display_years, lw=4, legend=False, marker='.', markersize=7, zorder=1)
	axes[0].invert_yaxis()
	axes[0].set_navigate(False)

	for school in schools:
		color = axes[0].get_lines()#[schools.index(school)].get_color()
		# a,b = get_markers(school,'Final Rank',3)
		# a = np.array(a)
		# b = np.array(b)
		# axes[0].scatter(a, b, color=color, s=235, marker='D', zorder=2)

	# Percentage
	# data = data_arr[1]
	data.plot(ax=axes[1], colormap='Set3', fontsize=10, xticks=display_years, lw=4, legend=False, marker='.', markersize=7,yticks=yticks, zorder=1)
	# for school in schools:
	# 	color = axes[1].get_lines()[schools.index(school)].get_color()
	# 	a,b = get_markers(school,'Scores >= 9.9',3)
	# 	a = np.array(a)
	# 	b = np.array(b)
	# 	axes[1].scatter(a, b, color=color, s=235, marker='D', zorder=2)
	# 	axes[1].invert_yaxis()

	axes[0].set_title("End of Season Rank", y=1.05, pad=-14, size=17)
	axes[1].set_title("Percentage of Scores >= 9.9", y=1.05, pad=-14, size=17)


	# Figure Settings
	handles, labels = axes[0].get_legend_handles_labels()

	legend = fig.legend(handles, labels, ncol=3, title='Schools', fancybox=True, shadow=True, loc='lower center', bbox_to_anchor=(0.5,-0.2), fontsize=15)

	plt.setp(legend.get_title(),fontsize=20)
	fig.savefig(output+'.jpg', bbox_extra_artists=(legend,), bbox_inches='tight', pad_inches=1)
	plt.close('all')
