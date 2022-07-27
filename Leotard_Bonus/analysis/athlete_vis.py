#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import random


def main():
	events = ['aa', 'vt', 'ub', 'bb', 'fx']
	aa_data = pd.read_csv('../data/output/athlete_data_AA_2.csv')

	vt_data = pd.read_csv('../data/output/athlete_data_VT_2.csv')
	ub_data = pd.read_csv('../data/output/athlete_data_UB_2.csv')
	bb_data = pd.read_csv('../data/output/athlete_data_BB_2.csv')
	fx_data = pd.read_csv('../data/output/athlete_data_FX_2.csv')

	aa_segment = get_segment(aa_data, 15, 85, 'AA') #[top,bottom]

	aa_top = get_num_recruits(aa_segment[0], 'AA')
	# aa_bottom = get_num_recruits(aa_segment[1], 'AA')

	# vt_top = get_num_recruits(aa_segment[0], 'VT')
	# vt_bottom = get_num_recruits(aa_segment[1], 'VT')
	# ub_top = get_num_recruits(aa_segment[0], 'UB')
	# ub_bottom = get_num_recruits(aa_segment[1], 'UB')
	# bb_top = get_num_recruits(aa_segment[0], 'BB')
	# bb_bottom = get_num_recruits(aa_segment[1], 'BB')
	# fx_top = get_num_recruits(aa_segment[0], 'FX')
	# fx_bottom = get_num_recruits(aa_segment[1], 'FX')
	# #
	data = [aa_top, aa_top, \
		aa_top, aa_top, \
		aa_top, aa_top, \
		aa_top, aa_top, \
		aa_top, aa_top]

	create_graph(data)

def create_graph(data):
	print(data[0])
	display_years = [2013, 2015, 2017, 2019, 2021]
	events = ['AA', 'VT', 'UB', 'BB', 'FX']
	fig, axes = plt.subplots(nrows=5, ncols=2, constrained_layout=True)
	fig.suptitle('Number of Recruits by Segment', fontsize=27, fontweight='bold')
	fig.set_figheight(7)
	fig.set_figwidth(15)

	# Add 10 plots
	for event in events:
		index = events.index(event)

		data[0].plot(ax=axes[index,0], colormap='Set2', fontsize=10, xticks=display_years, lw=4, legend=False)
		axes[index,0].set_title(event+' Top', y=1.2, pad=-14, size=17)

		data[0].plot(ax=axes[index,1], colormap='Set2', fontsize=10, xticks=display_years, lw=4, legend=False)
		axes[index,1].set_title(event+' Bottom', y=1.2, pad=-14, size=17)

	# Legend
	handles, labels = axes[0,0].get_legend_handles_labels()
	x = fig.legend(handles, labels, ncol=5, title='Schools', fancybox=True, shadow=True, loc='lower center', bbox_to_anchor=(0.5,-0.2), fontsize=15)
	plt.setp(x.get_title(),fontsize=20)

	path_to_save = 'athlete_vis.jpg'
	fig.savefig(path_to_save, bbox_extra_artists=(x,), bbox_inches='tight', pad_inches=1)
	plt.close('all')

def get_num_recruits(event_segment, event):
	schools_df = event_segment[['School']].drop_duplicates(ignore_index=True)
	print(event_segment)
	years = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022]
	schools = schools_df['School'].to_numpy()

	result = pd.DataFrame(columns=schools)
	for school in schools:
		for year in years:
			# value = event_segment.loc[(event_segment['School'] == school) & (event_segment['Year'] == year)]
			# print(value)
			num_recruits = random.randint(0, 1000)
			result.at[year, school] = num_recruits

	# result['Event'] = event
	return(result)

def get_segment(data, top, bottom, event):
	# Return an array with the top percentage and bottom percentage
	data = drop_zeros(data, event)
	data = data[['Name', 'School', event+'_delta', 'Freshman']]
	data = data.sort_values(by=[event+'_delta'], ascending=False).reset_index(drop=True)
	data = data.drop_duplicates(ignore_index=True, subset=['Name'])
	num_rows = data.shape[0]
	num_top = round(num_rows*top*0.01)
	num_bottom = round(num_rows*bottom*0.01)

	return([data.head(num_top),data.tail(num_top)])

def drop_zeros(event_data, event):
	col = 'NCAA_High_'+event
	event_data = event_data.loc[event_data[col] != 0]
	col = 'L10_High_'+event
	event_data = event_data.loc[event_data[col] != 0]
	return(event_data)

if __name__ == '__main__':
	main()
