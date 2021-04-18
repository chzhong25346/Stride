import hashlib
import logging
import re
logger = logging.getLogger('main.util')


def gen_id(string):
    return int(hashlib.md5(str.encode(string)).hexdigest(), 16)


def normalize_Todash(data):
    data['symbol'] = data['symbol'].str.replace(".","-")
    return data


def groupby_na_to_zero(df, ticker):
    df = df.groupby(ticker).first()
    df.fillna(0, inplace=True)
    return df


def missing_ticker(index):
    tickers = set()
    rx = re.compile("\((.+)\)")
    fh = open('log.log', 'r')
    for line in fh:
        if 'Found duplicate' not in line:
            strings = re.findall(rx, line)
            if strings and index in strings[0]:
                    tickers.add(strings[0].split(',')[1])
    logger.info('Found %d missing quotes in %s' % (len(tickers), index))
    fh.close()
    return list(tickers)
