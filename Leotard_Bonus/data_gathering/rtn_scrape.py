import csv
import requests
from datetime import datetime

years = ['2022', '2021', '2019', '2018', '2017', '2016',
'2015', '2014', '2013', '2012', '2011', '2010', '2009',
'2008', '2007', '2006', '2005', '2004', '2003', '2002',
'2001', '2000', '1999', '1998']

years = ['2022']
list_of_rows = []
headers = ['Season','Meet ID','Meet Date','Host','Opponents','Meet Name','Gymnast ID','Name','Team','Event','RQS','Score']
list_of_rows.append(headers)

list_of_meets = []
completed_meets = []
gymnast_data = {}
meet_data = {}
i = 1

for year in years:
    list_of_meets = []
    completed_meets = []
    gymnast_data = {}
    meet_data = {}
    i = 1
    url = 'https://www.roadtonationals.com/api/women/gymnasts2/'+year+'/1'
    allTeamsData = requests.get(url)
    teams = allTeamsData.json()['teams']
    for team in teams:
        teamID = team['id']
        teamName = team['team_name']
        print(year+': '+teamName)
        url = 'https://www.roadtonationals.com/api/women/rostermain/'+year+'/'+teamID+'/1'
        rosterData = requests.get(url).json()
        url = 'https://www.roadtonationals.com/api/women/rostermain/'+year+'/'+teamID+'/4'
        rqsData = requests.get(url).json()['ind']
        url = 'https://www.roadtonationals.com/api/women/dashboard/'+year+'/'+teamID
        meets = requests.get(url).json()['meets']
        for gymnast in rosterData:
            gymnastID = gymnast['id']
            gymnastName = gymnast['fname']+' '+gymnast['lname']
            vt_rqs = ''
            ub_rqs = ''
            bb_rqs = ''
            fx_rqs = ''
            for rqs in rqsData:
                if rqs['gid'] == gymnastID:
                    vt_rqs = rqs['maxv']
                    ub_rqs = rqs['maxub']
                    bb_rqs = rqs['maxbb']
                    fx_rqs = rqs['maxfx']
            gymnast_data[gymnastID] = {'name': gymnastName, 'team': teamName, 'vt': vt_rqs, 'ub': ub_rqs, 'bb': bb_rqs, 'fx': fx_rqs}
        for meet in meets:
            meetID = meet['meet_id']
            if meetID == 0:
                continue
            if meetID in list_of_meets:
                continue
            list_of_meets.append(meetID)
            meetDate = meet['meet_date']
            meetName = meet['meet_desc']
            meet_data[meetID] = {'date': meetDate, 'name': meetName, 'team': teamName}
        j = len(list_of_meets)
    for meet in list_of_meets:
        print(year+': meet '+str(i)+' of '+str(j))
        i = i + 1
        url = 'https://www.roadtonationals.com/api/women/meetresults/'+meet
        try:
            meet_teams = requests.get(url).json()['teams']
        except:
            print('meet '+meet+' not found')
            continue
        home_team = 'Neutral'
        away_teams_list = []
        meetDate = meet_data[meet]['date']
        meetName = meet_data[meet]['name']
        teamName = meet_data[meet]['team']
        for meet_team in meet_teams:
            if meet_team['home'] == 'H':
                home_team = meet_team['tname']
            else:
                away_teams_list.append(meet_team['tname'])
        away_teams = ', '.join(away_teams_list)
        scores = requests.get(url).json()['scores']
        for team_scores in scores:
            for gymnast_scores in team_scores:
                gymnastID = gymnast_scores['gid']
                if gymnastID not in gymnast_data.keys():
                    gymnast_data[gymnastID] = {}
                    gymnast_data[gymnastID]['name'] = gymnast_scores['first_name']+' '+gymnast_scores['last_name']
                    gymnast_data[gymnastID]['team'] = gymnast_scores['team_name']
                    gymnast_data[gymnastID]['vt'] = ''
                    gymnast_data[gymnastID]['ub'] = ''
                    gymnast_data[gymnastID]['bb'] = ''
                    gymnast_data[gymnastID]['fx'] = ''
                    print('gymnast '+gymnastID+' from meet '+meet+' added to data')
                    continue
                if gymnast_data[gymnastID]['team'] != teamName:
                    continue
                gymnastName = gymnast_data[gymnastID]['name']
                vt_rqs = gymnast_data[gymnastID]['vt']
                ub_rqs = gymnast_data[gymnastID]['ub']
                bb_rqs = gymnast_data[gymnastID]['bb']
                fx_rqs = gymnast_data[gymnastID]['fx']
                if gymnast_scores['vault']:
                    row = [year,meet,meetDate,home_team,away_teams,meetName,gymnastID,gymnastName,teamName,'VT',vt_rqs,gymnast_scores['vault']]
                    list_of_rows.append(row)
                if gymnast_scores['bars']:
                    row = [year,meet,meetDate,home_team,away_teams,meetName,gymnastID,gymnastName,teamName,'UB',ub_rqs,gymnast_scores['bars']]
                    list_of_rows.append(row)
                if gymnast_scores['beam']:
                    row = [year,meet,meetDate,home_team,away_teams,meetName,gymnastID,gymnastName,teamName,'BB',bb_rqs,gymnast_scores['beam']]
                    list_of_rows.append(row)
                if gymnast_scores['floor']:
                    row = [year,meet,meetDate,home_team,away_teams,meetName,gymnastID,gymnastName,teamName,'FX',fx_rqs,gymnast_scores['floor']]
                    list_of_rows.append(row)

years_text='-'.join(years)
csv_file = "../data/rtn_2022.csv"
with open(csv_file, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(list_of_rows)
