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

	nqs_data = select_for_chart(school_data, 'Big10', 'NQS')
	rank_data = select_for_chart(school_data, 'Big10', 'Final Rank')
	high_scores_data = select_for_chart(school_data, 'Big10', 'Scores >= 9.9')
	location_data = select_for_chart(school_data, 'Big10', 'Location Delta')
	x_values = [2013, 2015, 2017, 2019, 2021]

	fig, axes = plt.subplots(nrows=2, ncols=2, constrained_layout=True)
	fig.suptitle('Big 10', fontsize=27)
	fig.set_figheight(7)
	fig.set_figwidth(15)

	# Add 4 plots
	nqs_data.plot(ax=axes[0,0], colormap='jet', fontsize=10, xticks=x_values, lw=2, marker='.', markersize=7, legend=False)
	axes[0,0].set_title('NQS', y=1.1, pad=-14, size=17)

	rank_data.plot(ax=axes[0,1], colormap='jet', fontsize=10, xticks=x_values, lw=2, marker='.', markersize=7, legend=False)
	axes[0,1].set_title('Final Rank', y=1.1, pad=-14, size=17)

	high_scores_data.plot(ax=axes[1,0], colormap='jet', fontsize=10, xticks=x_values, lw=2, marker='.', markersize=7, legend=False)
	axes[1,0].set_title('Percentage of Scores >= 9.9', y=1.1, pad=-14, size=17)

	location_data.plot(ax=axes[1,1], colormap='jet', fontsize=10, xticks=x_values, lw=2, marker='.', markersize=7, legend=False)
	axes[1,1].set_title('Location Delta', y=1.1, pad=-14, size=17)

	# Figure Settings
	handles, labels = axes[0,0].get_legend_handles_labels()
	x = fig.legend(handles, labels, ncol=5, title='Schools', fancybox=True, shadow=True, loc='lower center', bbox_to_anchor=(0.5,-0.2), fontsize=15)
	plt.setp(x.get_title(),fontsize=20)

	fig.savefig('samplefigure', bbox_extra_artists=(x,), bbox_inches='tight', pad_inches=1)


def select_for_chart(data, conference, value):
	# Select conference and value to visualize
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
				if x.at[0,value] != 0.0:
					result.at[int(year),school] = x.at[0,value]

	return(result)

if __name__ == '__main__':
	main()
