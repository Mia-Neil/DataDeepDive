import csv
import requests
from bs4 import BeautifulSoup

def main():
	for year in range(2011, 2022):
		print("Getting top 100 scores for {}".format(year))
		get_scores(year)

def get_scores(year):
	url = 'https://www.mymeetscores.com/at40.pl?event=AA&level=10&year={}'.format(year)
	aa_scores = []

	resp = requests.get(url).text
	soup = BeautifulSoup(resp, features="lxml")
	table_set = soup.find_all('table')
	gymnast_table = table_set[2]
	rows = iter(gymnast_table.find('table').find_all('tr'))

	next(rows)
	next(rows)
	next(rows)

	for row in rows:
		row_data = []
		cells = row.find_all('td')
		for cell in cells:
			row_data.append(cell.text)
		if row_data != []:
			row_data = row_data[0:3]
			row_data.append(year)
			aa_scores.append(row_data)

	filename = 'mms_top_100.csv'
	with open(filename, "a+") as f:
		writer = csv.writer(f)
		writer.writerows(aa_scores)


if __name__ == '__main__':
	    main()
