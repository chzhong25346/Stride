import logging
import pandas as pd
from stockstats import StockDataFrame
logger = logging.getLogger('main.macd')


def macd(ticker, df):
    df = df.drop('adjusted', axis=1)
    pd.set_option('mode.chained_assignment', None)
    stock = StockDataFrame.retype(df)
    # MACD TODAY
    tmacd = stock['macd'][-1]
    tmacds = stock['macds'][-1]
    tmacdh = stock['macdh'][-1]
    tatt = macd_attribute(tmacd, tmacds, tmacdh)
    #MACD TODAY -1
    ymacd = stock['macd'][-2]
    ymacds = stock['macds'][-2]
    ymacdh = stock['macdh'][-2]
    yatt = macd_attribute(ymacd, ymacds, ymacdh)
    if (yatt=='neg' and tatt=='pos-buy'):
        return {'symbol':ticker,'macd':'buy'}
    elif (yatt=='neg' and tatt=='pos-sell'):
        return {'symbol':ticker,'macd':'sell'}
    # print(ymacd, ymacds, ymacdh, yatt)
    # print(tmacd, tmacds, tmacdh, tatt)


def macd_attribute(macd, macds, macdh):
    if (macd < 0 and macds < 0 and macdh > 0):
        return 'pos-buy'
    elif (macd > 0 and macds > 0 and macdh < 0):
        return 'pos-sell'
    elif (macd > 0 and macds > 0 and macdh > 0):
        return 'neg'
    elif (macd < 0 and macds < 0 and macdh < 0):
        return 'neg'
