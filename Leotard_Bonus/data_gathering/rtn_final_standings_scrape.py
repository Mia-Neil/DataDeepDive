import csv
import requests
from datetime import datetime

years = ['2022', '2021', '2019', '2018', '2017', '2016',
'2015', '2014', '2013', '2012', '2011', '2010', '2009']

# years = ['2022']
list_of_rows = []
headers = ['Team','Year','VT','UB','BB','FX','Overall']
list_of_rows.append(headers)

for year in years:
	url = 'https://www.roadtonationals.com/api/women/gymnasts2/'+year+'/1'
	allTeamsData = requests.get(url)
	teams = allTeamsData.json()['teams']
	for team in teams:
		teamID = team['id']
		teamName = team['team_name']
		print(year+': '+teamName)

		url = 'https://www.roadtonationals.com/api/women/dashboard/'+year+'/'+teamID
		ranks = requests.get(url).json()['ranks']
		row = [teamName, year, ranks['vault'], ranks['bars'], ranks['beam'], ranks['floor'], ranks['team']]
		list_of_rows.append(row)

csv_file = "../data/rtn_final_standings.csv"
with open(csv_file, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(list_of_rows)
