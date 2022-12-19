#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


def main():
	school_data_path = '../data/output/school_rank_delta.csv'
	school_data = pd.read_csv(school_data_path)

	conferences = ['Big10', 'Big12', 'EAGL', 'GEC', 'MAC', 'MIC', 'MPSF', 'MRGC', 'PAC12', 'SEC', 'NaN']

	schools_a = []
	schools_b = []
	top_10 = get_range_schools(school_data, 1, 5)
	for index,row in top_10.iterrows():
		schools_a.append(row['school'])
	# next_10 = get_range_schools(school_data, 6, 10)
	# for index,row in next_10.iterrows():
	# 	schools_b.append(row['school'])

	# Graphs of top schools
	# graph_schools(school_data, schools_a, 'Top Schools')
	# graph_schools(school_data, schools_b, 'Next Top Schools')

	# # Generate conference graphs
	for conference in conferences:
		print("Conference: {}".format(conference))
		# graph_conference(school_data, conference)
		graph_conference_delta(school_data, conference)

def get_range_schools(data, high, low):
	print("Finding schools ranked {} to {}".format(high, low))
	rank_data_path = '../data/output/school_final_ranks.csv'
	rank_data = pd.read_csv(rank_data_path)
	years = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022]
	schools = rank_data.drop_duplicates(subset='Team', inplace=False, ignore_index=False)
	schools = schools[['Team']]
	lines = []

	for index,row in schools.iterrows():
		print(row['Team'])
		school_ranks = data.loc[data['School'] == row['Team']]
		school_ranks = school_ranks[['School', 'Year', 'Final Rank']]
		ave_rank = round(school_ranks["Final Rank"].mean(skipna=True))
		current_line = {
			'school':row['Team'],
			'ave_rank':ave_rank
		}
		lines.append(current_line)
	results = pd.DataFrame.from_records(lines)
	results = results.sort_values(by=['ave_rank']).reset_index(drop=True)
	return(results.iloc[high-1:low])

def graph_conference_delta(school_data, conference):
	display_years = [2013, 2015, 2017, 2019, 2021]
	aa_delta = select_for_chart(school_data, conference, 'AA Delta')
	vt_delta = select_for_chart(school_data, conference, 'VT Delta')
	ub_delta = select_for_chart(school_data, conference, 'UB Delta')
	bb_delta = select_for_chart(school_data, conference, 'BB Delta')
	fx_delta = select_for_chart(school_data, conference, 'FX Delta')
	rank_data = select_for_chart(school_data, conference, 'Final Rank')
	lowest_rank = rank_data.max().max()
	lowest_rank = 5 * round(rank_data.max().max()/5) + 5
	fig, axes = plt.subplots(nrows=2, ncols=3, constrained_layout=True)
	if conference == 'NaN':
		fig.suptitle('No Listed Conference', fontsize=27, fontweight='bold')
	else:
		fig.suptitle("Score Deltas: "+conference, fontsize=27, fontweight='bold')
	fig.set_figwidth(23)
	fig.set_figheight(13)

	aa_delta.plot(ax=axes[0,0], colormap='Set2', fontsize=10, xticks=display_years, lw=4, marker='.', markersize=7, legend=False)
	axes[0,0].set_title('AA Delta', y=1.05, pad=-14, size=17)

	vt_delta.plot(ax=axes[0,1], colormap='Set2', fontsize=10, xticks=display_years, lw=4, marker='.', markersize=7, legend=False)
	axes[0,1].set_title('VT Delta', y=1.05, pad=-14, size=17)

	ub_delta.plot(ax=axes[0,2], colormap='Set2', fontsize=10, xticks=display_years, lw=4, marker='.', markersize=7, legend=False)
	axes[0,2].set_title('UB Delta', y=1.05, pad=-14, size=17)

	bb_delta.plot(ax=axes[1,0], colormap='Set2', fontsize=10, xticks=display_years, lw=4, marker='.', markersize=7, legend=False)
	axes[1,0].set_title('BB Delta', y=1.05, pad=-14, size=17)

	fx_delta.plot(ax=axes[1,1], colormap='Set2', fontsize=10, xticks=display_years, lw=4, marker='.', markersize=7, legend=False)
	axes[1,1].set_title('FX Delta', y=1.05, pad=-14, size=17)

	yticks = np.arange(0, lowest_rank, 5)
	yticks = np.where(yticks==0, 1, yticks)
	rank_data.plot(ax=axes[1,2], colormap='Set2', fontsize=10, xticks=display_years, lw=4, marker='.', markersize=7, legend=False, yticks=yticks)
	axes[1,2].invert_yaxis()
	axes[1,2].set_title('Final Rank', y=1.05, pad=-14, size=17)

	# Figure Settings
	handles, labels = axes[0,0].get_legend_handles_labels()
	if conference == 'NaN':
		x = fig.legend(handles, labels, ncol=6, title='Schools', fancybox=True, shadow=True, loc='lower center', bbox_to_anchor=(0.5,-0.3), fontsize=15)
	else:
		x = fig.legend(handles, labels, ncol=5, title='Schools', fancybox=True, shadow=True, loc='lower center', bbox_to_anchor=(0.5,-0.2), fontsize=15)

	plt.setp(x.get_title(),fontsize=20)
	path_to_save = 'graph_output/deltas/'+conference+'.jpg'
	fig.savefig(path_to_save, bbox_extra_artists=(x,), bbox_inches='tight', pad_inches=1)
	plt.close('all')

def graph_conference(school_data, conference):
	display_years = [2013, 2015, 2017, 2019, 2021]
	nqs_data = select_for_chart(school_data, conference, 'NQS')
	rank_data = select_for_chart(school_data, conference, 'Final Rank')
	lowest_rank = rank_data.max().max()
	lowest_rank = 5 * round(rank_data.max().max()/5) + 5
	high_scores_data = select_for_chart(school_data, conference, 'Scores >= 9.9')
	location_data = select_for_chart(school_data, conference, 'Location Delta')
	fig, axes = plt.subplots(nrows=2, ncols=2, constrained_layout=True)
	if conference == 'NaN':
		fig.suptitle('No Listed Conference', fontsize=27, fontweight='bold')
	else:
		fig.suptitle(conference, fontsize=27, fontweight='bold')
	fig.set_figheight(7)
	fig.set_figwidth(15)

	# Add 4 plots
	nqs_data.plot(ax=axes[0,0], colormap='Set2', fontsize=10, xticks=display_years, lw=4, marker='.', markersize=7, legend=False)
	axes[0,0].set_title('NQS', y=1.1, pad=-14, size=17)

	yticks = np.arange(0, lowest_rank, 5)
	yticks = np.where(yticks==0, 1, yticks)
	rank_data.plot(ax=axes[0,1], colormap='Set2', fontsize=10, xticks=display_years, lw=4, marker='.', markersize=7, legend=False, yticks=yticks)
	axes[0,1].invert_yaxis()
	axes[0,1].set_title('Final Rank', y=1.1, pad=-14, size=17)

	high_scores_data.plot(ax=axes[1,0], colormap='Set2', fontsize=10, xticks=display_years, lw=4, marker='.', markersize=7, legend=False)
	axes[1,0].set_title('Percentage of Scores >= 9.9', y=1.1, pad=-14, size=17)

	location_data.plot(ax=axes[1,1], colormap='Set2', fontsize=10, xticks=display_years, lw=4, marker='.', markersize=7, legend=False)
	axes[1,1].set_title('Location Delta', y=1.1, pad=-14, size=17)

	# Figure Settings
	handles, labels = axes[0,0].get_legend_handles_labels()
	if conference == 'NaN':
		x = fig.legend(handles, labels, ncol=6, title='Schools', fancybox=True, shadow=True, loc='lower center', bbox_to_anchor=(0.5,-0.3), fontsize=15)
	else:
		x = fig.legend(handles, labels, ncol=5, title='Schools', fancybox=True, shadow=True, loc='lower center', bbox_to_anchor=(0.5,-0.2), fontsize=15)

	plt.setp(x.get_title(),fontsize=20)
	path_to_save = 'graph_output/conferences/'+conference+'.jpg'
	fig.savefig(path_to_save, bbox_extra_artists=(x,), bbox_inches='tight', pad_inches=1)
	plt.close('all')

def top_4_year(school, field):
	print("Current School: {}".format(school))
	x=[]
	y=[]
	data_path = '../data/output/school_rank_delta.csv'
	data = pd.read_csv(data_path)
	data = data[['Team', 'Year', field]]
	school_ranks = rank_data.loc[(rank_data['Team'] == school) & (rank_data['Year'] > 2011)].sort_values(by=['Year'])
	for index,row in school_ranks.iterrows():
		if row['Overall'] <= 4:
			x.append(row['Year'])
			y.append(row['Overall'])
			# or year,

	return x,y

def graph_schools(data, schools, title):
	display_years = [2013, 2015, 2017, 2019, 2021]

	fig, axes = plt.subplots(nrows=2, ncols=2, constrained_layout=True)
	fig.suptitle(title, fontsize=27, fontweight='bold')
	fig.set_figwidth(23)
	fig.set_figheight(13)

	rank_data = select_school_for_chart(data, schools, 'Final Rank')
	lowest_rank = rank_data.max().max()
	lowest_rank = 5 * round(rank_data.max().max()/5) + 5
	yticks = np.arange(0, lowest_rank, 5)
	yticks = np.where(yticks==0, 1, yticks)
	rank_data.plot(ax=axes[0,0], colormap='Set2', fontsize=10, xticks=display_years, lw=4, marker='.', markersize=7, legend=False, yticks=yticks, zorder=1)
	axes[0,0].invert_yaxis()
	axes[0,0].set_title('Final Rank', y=1.05, pad=-14, size=17)

	for school in schools:
		color = axes[0,0].get_lines()[schools.index(school)].get_color()
		x,y = top_4_year(school, 'Final Rank')
		x = np.array(x)
		y = np.array(y)
		axes[0,0].scatter(x, y, color=color, s=253, marker='D', zorder=2)

	percentage = select_school_for_chart(data, schools, 'Scores >= 9.9')
	percentage.plot(ax=axes[0,1], colormap='Set2', fontsize=10, xticks=display_years, lw=4, legend=False)
	axes[0,1].set_title('Percentage of Scores >= 9.9', y=1.05, pad=-14, size=17)
	for school in schools:
		color = axes[0,1].get_lines()[schools.index(school)].get_color()
		x,y = top_4_year(school, 'Scores >= 9.9')
		x = np.array(x)
		y = np.array(y)
		axes[0,1].scatter(x, y, color=color, s=253, marker='D', zorder=2)


	delta = select_school_for_chart(data, schools, 'VT Delta')
	delta.plot(ax=axes[1,0], colormap='Set2', fontsize=10, xticks=display_years, lw=4, marker='.', markersize=7, legend=False)
	axes[1,0].set_title('Vault Delta', y=1.05, pad=-14, size=17)

	aa_delta = select_school_for_chart(data, schools, 'AA Delta')
	aa_delta.plot(ax=axes[1,1], colormap='Set2', fontsize=10, xticks=display_years, lw=4, marker='.', markersize=7, legend=False)
	axes[1,1].set_title('AA Delta', y=1.05, pad=-14, size=17)

	# Figure Settings
	handles, labels = axes[0,0].get_legend_handles_labels()

	x = fig.legend(handles, labels, ncol=7, title='Schools', fancybox=True, shadow=True, loc='lower center', bbox_to_anchor=(0.5,-0.2), fontsize=15)

	plt.setp(x.get_title(),fontsize=20)
	path_to_save = 'graph_output/schools/'+title+'.jpg'
	fig.savefig(path_to_save, bbox_extra_artists=(x,), bbox_inches='tight', pad_inches=1)
	plt.close('all')
	return(True)

def select_school_for_chart(data, schools, value):
	years = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022]
	data = data[["Year", "School", value]]
	result = pd.DataFrame(columns=schools)

	for year in years:
		for school in schools:
			x = data.loc[(data['School'] == school) & (data['Year'] == int(year))]
			x = x.reset_index(drop=True)
			if not x.empty:
				if x.at[0,value] != 0.0: #don't plot if no NQS
					if not x.at[0,value] == 1000:
						result.at[int(year),school] = x.at[0,value]
	return(result)

def select_for_chart(data, conference, value):
	# Select conference and value to visualize
	if conference == 'NaN':
		select = data[data['Conference'].isnull()]
	else:
		select = data.loc[data['Conference'] == conference]
	select = select[["Year", "School", value]]
	years = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022]

	# Transpose
	schools = select.drop_duplicates(subset='School', inplace=False, ignore_index=False)
	schools = schools[['School']]
	school_list = []

	for index, row in schools.iterrows():
		school_list.append(row['School'])

	result = pd.DataFrame(columns=school_list)

	for year in years:
		for school in school_list:
			x = select.loc[(select['School'] == school) & (select['Year'] == int(year))]
			x = x.reset_index(drop=True)
			if not x.empty:
				if x.at[0,value] != 0.0: #don't plot if no NQS
					if not x.at[0,value] == 1000:
						result.at[int(year),school] = x.at[0,value]

	return(result)

if __name__ == '__main__':
	main()
