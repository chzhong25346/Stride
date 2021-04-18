import logging
import pandas as pd
from stockstats import StockDataFrame
logger = logging.getLogger('main.rsi')


def rsi(ticker, df):
    pd.set_option('mode.chained_assignment', None)
    stock = StockDataFrame.retype(df)
    # RSI Today
    trsi = stock['rsi_14'][-1]
    # RSI Today - 1
    yrsi = stock['rsi_14'][-2]

    # print(yrsi, trsi)

    if (yrsi <= 30 and trsi > 30):
        return {'symbol':ticker,'rsi':'buy'}
    elif (yrsi >= 70 and trsi < 70):
        return {'symbol':ticker,'rsi':'sell'}
