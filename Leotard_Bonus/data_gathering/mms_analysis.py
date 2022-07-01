#!/usr/bin/env python3
import pandas as pd
import numpy as np
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def main():
	url = 'https://www.mymeetscores.com/gymnast.pl?gymnastid=15482'
	resp = requests.get(url).text

	soup = BeautifulSoup(resp, features="lxml")
	tables = soup.find_all('table')

	# Personal Bests from final year
	personal_bests = tables[4]
	rows = personal_bests.find_all('tr')
	last_year = rows[-2]
	cells = last_year.find_all('td')
	for cell in cells:
		x = 1 + 1
		# print(cell.text)

	# Top 100 scores from final year
	hot_100 = tables[5]
	rows = hot_100.find('table').find_all('tr')
	final_year = rows[-2]

	cells = final_year.find_all('td')
	for cell in cells:
		x = 1 + 1
		# print(cell.text)

	# Meet data from final year
	meet_data = tables[7]
	rows = meet_data.find('table').find_all('tr')
	year = datetime.strptime(rows[2].find('td').text, '%Y-%M-%d').year

	aa_scores = []
	for row in rows[2:len(rows)-2]:
		row_arr = []
		date = row.find('td')
		meet_year = datetime.strptime(date.text, '%Y-%M-%d').year
		if meet_year == year:
			cells = row.find_all('td')
			for cell in cells:
				row_arr.append(cell.text)
		aa_scores.append(row_arr)
	print(aa_scores)

if __name__ == '__main__':
	main()
