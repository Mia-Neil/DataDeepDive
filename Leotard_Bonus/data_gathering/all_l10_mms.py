import csv
import requests
from bs4 import BeautifulSoup

years = ['2019-09','2020','2021','2022']
# years = ['2019']

def clean_score(score):
    if not(score):
        score == '0.000'
    if not(isinstance(score,str)):
        score = str(score)
    if ' ' in score:
        score = score.split(' ')[0]
    if score == '':
        score = '0.000'
    return score

data = []
headers = ['Unique ID','MMS ID','MMS Name','MMS Club','Meet ID','Meet Date','Meet Name','Level','VT','UB','BB','FX','AA','Exclude?']
data.append(headers)

for year in years:
    if '-' in year:
        month = year.split('-')[1]
        year = year.split('-')[0]
    else:
        month = '01'
    url = 'http://www.mymeetscores.com/gym.pl?list=2&state=All&year='+year
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.findAll('table')[3]
    meets = table.findAll('tr')[3:]

    i = 0
    for meet in meets[:-1]:
        i = i + 1
        cols = meet.findAll('td')
        if len(cols[4].text) < 1:
            continue
        meet_date = cols[0].text
        meet_month = meet_date.split('-')[1]
        if int(meet_month) < int(month):
            continue
        print(year+': Meet '+str(i)+' of '+str(len(meets[:-1])))
        meet_name = cols[1].text
        meet_id = cols[1].find('a')['href'].split('=')[1]
        url = 'http://mymeetscores.com/meet.pl?meetid='+meet_id
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        trs = soup.findAll('tr')
        is_score = False
        try:
            for tr in trs:
                try:
                    if not is_score and tr.text.index('#Name') == 0:
                        is_score = True
                except:
                    continue
                if len(tr.text) > 1 and is_score:
                    tds = tr.findAll('td')
                    level = tds[4].text
                    if 'Nastia Liukin Cup' not in meet_name and '10' not in level and 'OP' not in level and 'Open' not in level:
                        continue
                    if 'Jr10' in level:
                        continue
                    mms_id = tds[1].find('a')['href'].split('=')[1]
                    mms_name = tds[1].text
                    mms_club = tds[2].text
                    vt = clean_score(tds[6].text)
                    ub = clean_score(tds[7].text)
                    bb = clean_score(tds[8].text)
                    fx = clean_score(tds[9].text)
                    aa = clean_score(tds[10].text)
                    exclude = ''
                    unique_id = mms_id+'_'+meet_date
                    row = [unique_id,mms_id,mms_name,mms_club,meet_id,meet_date,meet_name,level,vt,ub,bb,fx,aa,exclude]
                    data.append(row)
        except Exception as ex:
            print('Error: Meet '+meet_id+' - '+str(ex))

file = 'all_scores_since_'+years[0]+'.csv'

with open(file, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data)