import logging
import pandas as pd
import numpy as np
from .ema import trend_potential
from .volume import unusual_volume
from .fiftytwoWeek import fiftytwo_week
# from .pattern import find_pattern
# from .support import support
from .rsi import rsi
from .macd import macd
from .bolling import bolling
# from .adx import adx
# from .volume_price import volume_price
from ..utils.util import groupby_na_to_zero
from ..db.read import read_ticker
from ..models import Index, Quote, Report
import logging
logger = logging.getLogger('main.report')


def report(s):
    tickerL = read_ticker(s)
    # tickerL = ['PG']  #### CHECKPOINT
    # temp df for report with predefined columns
    columns=['symbol','yr_high','yr_low','downtrend','uptrend','high_volume','rsi','macd','bolling']
    dtypes =['str','int','int','int','int','int','str','str','str']
    report_df = df_empty(columns, dtypes)
    for symbol in tickerL:
        # print(symbol)
        # read daily db return df in random order
        df = pd.read_sql(s.query(Quote).filter(Quote.symbol == symbol).statement, s.bind, index_col='date')
        # sort by old to new
        df.sort_index(inplace=True)
        # drop rows have 0
        df = df[(df != 0).all(1)]
        # unusual volume stickers append to df
        report_df = report_df.append(unusual_volume(symbol,df),ignore_index=True)
        # unusual trend stickers append to df
        report_df = report_df.append(trend_potential(symbol,df),ignore_index=True)
        # 52w high/low/trending append to df
        report_df = report_df.append(fiftytwo_week(symbol,df),ignore_index=True)
        # decide if known pattern append to df
        # report_df = report_df.append(find_pattern(symbol,df),ignore_index=True)
        # decide if close to support line append to df
        # report_df = report_df.append(support(symbol,df),ignore_index=True)
        # decide if colume price turnning positive append to df
        # report_df = report_df.append(volume_price(symbol,df),ignore_index=True)
        # RSI
        report_df = report_df.append(rsi(symbol,df),ignore_index=True)
        # MACD
        report_df = report_df.append(macd(symbol,df),ignore_index=True)
        # BOLLING
        report_df = report_df.append(bolling(symbol,df),ignore_index=True)
        # ADX
        # report_df = report_df.append(adx(symbol,df),ignore_index=True)
    # if 'volume_price' not in df.columns:
    #     report_df['volume_price'] = np.nan
    # # grouby using first() and NaN to Zero and Date is a column
    report_df = groupby_na_to_zero(report_df, 'symbol')
    report_df = report_df.reset_index()
    logger.info('Report Completed, total: %s equities.' % (len(report_df.index)))
    return report_df


def df_empty(columns, dtypes, index=None):
    assert len(columns)==len(dtypes)
    df = pd.DataFrame(index=index)
    for c,d in zip(columns, dtypes):
        df[c] = pd.Series(dtype=d)

    return df
