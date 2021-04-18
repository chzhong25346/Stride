import logging
import pandas as pd
from stockstats import StockDataFrame


def bolling(ticker, df):
    pd.set_option('mode.chained_assignment', None)
    stock = StockDataFrame.retype(df)

    # All BB
    boll = stock['boll']
    upper = stock['boll_ub']
    lower = stock['boll_lb']

    # Today's Bolling
    today_boll = boll[-1]
    today_upper = upper[-1]
    today_lower = lower[-1]

    # All Price
    close = stock['close']
    open = stock['open']
    high = stock['high']
    low = stock['low']

    # Today's Price
    today_close = close[-1]
    today_open = open[-1]
    today_high = high[-1]
    today_low = low[-1]

    # Last five days OHLC
    last5 = stock[['close','open','high','low','boll','boll_ub','boll_lb']][-6:-1]

    # If Last five days touched bound
    last5['break'] = (last5['high'] >= last5['boll_ub']) | (last5['low'] <= last5['boll_lb'])
    Is_Last5_break = last5['break'].any()


    # EMA5; EMA5 MUST within BB; Bollinger Band Squeeze
    ema5 = ema(df,5)
    today_ema5 = ema5.loc[df.index.max()]
    df_cross = pd.concat([ema5, boll], axis=1).dropna().rename(columns={"adjusted": "ema5"})
    if today_ema5 > today_boll:
        df_cross['is_crossed'] = df_cross['ema5'] < df_cross['boll']
    elif today_ema5 < today_boll:
        df_cross['is_crossed'] = df_cross['ema5'] > df_cross['boll']

    # If Cross up or down really happened
    if df_cross['is_crossed'].any():
        crossed_date = df_cross[df_cross['is_crossed'] == True].index[-1]
        # Maximum of Upper to Lower band spread after Crossing
        max_BandWidth  = (upper[crossed_date:] - lower[crossed_date:]).max()
        # Today's bandwidth halfed maximum bandwidth
        today_BandWidth = today_upper - today_lower
        is_Squeezed = today_BandWidth <= max_BandWidth/2
        # Is price overlap Boll?
        is_Overlaped = today_high >= today_boll and today_low <= today_boll

        # Upside Break
        if ( Is_Last5_break == False and today_close >= today_upper ):
            return {'symbol':ticker,'bolling':'buy'}
        # Downside Break
        elif ( Is_Last5_break == False and today_close <= today_lower ):
            return {'symbol':ticker,'bolling':'sell'}
        # Bolling Band Narrowing and Price is overlaped with middle
        elif ( is_Squeezed and is_Overlaped ):
            return {'symbol':ticker,'bolling':'narrow'}


def ema(df, span):
    '''
    pick 3M data for analysis and calculate ewm
    return today's ema
    '''
    df = df.sort_index(ascending=True).last("3M")
    df = df['adjusted'].ewm(span=span, adjust=False).mean()

    return df
