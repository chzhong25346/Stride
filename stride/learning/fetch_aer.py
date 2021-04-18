import pandas as pd
import requests
import re, os, logging
import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
from dateutil import parser
from ..db.mapping import map_st1, map_st49, map_st97, map_st100
from ..db.write import bulk_save
logger = logging.getLogger('main.learning')


def fetch_aer(mode, rtype, s):
    if mode == 'full':
        # Define report path here
        path = "C:\\Users\\Administrator\\Downloads\\st97\\update"
        data = read_local(rtype, path)
        if rtype == 'st97':
            bulksave_report(rtype, s, data)
        else:
            df = pd.DataFrame(data)
            df = df.drop_duplicates(subset='date', keep="last")
            bulksave_report(rtype, s, df)
    elif mode == 'daily':
        file = get_report_online(rtype)
        if rtype == 'st97':
            df = read_report(rtype, file)
            bulksave_report(rtype, s, df)
        else:
            data = read_report(rtype, file)
            df = pd.DataFrame(data, index=[0])
            bulksave_report(rtype, s, df)


# Bulk Read local report files
def read_local(rtype, path):
    files = os.listdir(path)
    data = []
    for file in files:
        file_path = os.path.join(path,file)
        file = open(file_path, 'r')
        data.append(read_report(rtype, file)) # Read data and append as a list
        file.close() # Close file in Loop
    if rtype == 'st97':
        return pd.concat(data)
    return data


# Retrive report from AER
def get_report_online(rtype):
    dow = (datetime.date.today() - timedelta(days=1)).strftime("%a") # Yesterday, format MON, TUE, WED...
    if rtype == 'st1':
        url = "https://www.aer.ca/providing-information/data-and-reports/statistical-reports/st1"
    elif rtype == 'st49':
        url = "https://www.aer.ca/providing-information/data-and-reports/statistical-reports/st49"
    elif rtype == 'st97':
        url = "https://www.aer.ca/providing-information/data-and-reports/statistical-reports/st97"
    elif rtype == 'st100':
        url = "https://www.aer.ca/providing-information/data-and-reports/statistical-reports/st100"
    headers={
    'Referer': 'https://itunes.apple.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }
    data = requests.get(url, headers=headers).text
    soup = BeautifulSoup(data, "lxml")
    report_url = None
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if dow.casefold() in href.casefold():
            report_url = href
    if report_url != None:
        response = requests.get(report_url, headers=headers)
        if rtype == 'st97':
            return response
        file = response.text.splitlines()
        return file


# return Data map
def read_report(rtype, file):
    date = datetime.date.today()
    if rtype == 'st1':
        gas = 0
        oil = 0
        bitumen = 0
        for line in file:#.readlines():
            mdate = re.search('(?<=DATE: )(.*)', line)
            if mdate:
                date = parser.parse(mdate.group(0))
            for result in re.finditer(r'\bGAS\b', line):
                gas += 1
            for result in re.finditer(r'\bCRUDE OIL\b', line):
                oil += 1
            for result in re.finditer(r'\bCRUDE BITUMEN\b', line):
                bitumen += 1
        data = {'date': date, 'gas': gas, 'oil': oil, 'bitumen': bitumen}
        return data
    if rtype == 'st49':
        dtl = 0
        ree = 0
        resu = 0
        ss = 0
        total = 0
        for line in file:
            mdate = re.search('(?<=Run Date: )(.*)', line)
            mdtl =  re.search('(?<=Drilling to Licensed Depth)(.*)', line)
            mree =  re.search('(?<=Re-entry of an Abandoned Well)(.*)', line)
            mresu =  re.search('(?<=Resumption of Drilling of a Non-abandoned Well)(.*)', line)
            mss =  re.search('(?<=Drilling to Set Surface Casing Only)(.*)', line)
            mtotal = re.search('(?<=TOTAL NUMBER OF WELLS LISTED)(.*)', line)
            if mdate:
                date = parser.parse(mdate.group(0)[:14])
            if mdtl:
                dtl = re.findall(r'\b\d+\b', mdtl.group(0))[0]
            if mree:
                ree = re.findall(r'\b\d+\b', mree.group(0))[0]
            if mresu:
                resu = re.findall(r'\b\d+\b', mresu.group(0))[0]
            if mss:
                ss = re.findall(r'\b\d+\b', mss.group(0))[0]
            if mtotal:
                total = re.findall(r'\b\d+\b', mtotal.group(0))[0]
        data = {'date': date, 'drill_to_ld': dtl, 're_entry': ree, 'resumption': resu, 'set_surface': ss, 'total': total}
        return data
    if rtype == 'st97':
        # for line in file.text.splitlines():
        for line in file.readlines():
            mdate = re.search('(?<=Date:)(.*)', line)
            if mdate:
                date = parser.parse(re.sub("<.*?>", "", mdate.group(0), flags = re.IGNORECASE))
        try:
            df = pd.read_html(file.name, header=0, attrs={"align":"center"})[0]
            df.rename(columns={"Licensee Name": "licensee", "Application Purpose": "purpose", "Category Type Description": "type", "Application Number": "application"}, inplace=True)
            df = df[['licensee', 'purpose', 'type', 'application']]
            df['type'] = df['type'].str.split(' - | < |>', expand = True)
            df['date'] = date
            return df
        except:
            # print(e)
            pass
    if rtype == 'st100':
        total = 0
        for line in file:
            mdate = re.search('(?<=Run Date: )(.*)', line)
            mtotal =  re.search('(?<=TOTAL PIPELINE CONSTRUCTION NOTIFICATIONS =)(.*)', line)
            if mdate:
                date = parser.parse(mdate.group(0)[:14])
            if mtotal:
                total = re.findall(r'\b\d+\b', mtotal.group(0))[0]
        data = {'date': date,'total': total}
        return data


# Bulk Save
def bulksave_report(rtype, s, df):
    if rtype == 'st1':
        bulk_save(s, map_st1(df))
    elif rtype == 'st49':
        bulk_save(s, map_st49(df))
    elif rtype == 'st97':
        bulk_save(s, map_st97(df))
    elif rtype == 'st100':
        bulk_save(s, map_st100(df))
    logger.debug('(AER %s) %s entires written' % ( rtype, len(df.index) ))
