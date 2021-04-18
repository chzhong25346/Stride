import logging
import pandas as pd
from stockstats import StockDataFrame


def adx(ticker, df):
    pd.set_option('mode.chained_assignment', None)
    stock = StockDataFrame.retype(df)
    # DMI
    # +DI, default to 14 days
    pdi = stock['pdi'][-1]
    # -DI, default to 14 days
    mdi = stock['mdi'][-1]
    # ADX, 6 days SMA of DX, same as stock['dx_6_ema']
    adx = stock['adx'][-1]

    if ( adx > 25 and pdi > mdi ):
        return {'symbol':ticker,'adx':'buy'}
    elif ( adx > 25 and pdi < mdi ):
        return {'symbol':ticker,'adx':'sell'}
