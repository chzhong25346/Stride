import pandas as pd
import logging
logger = logging.getLogger('main.volume')


def unusual_volume(ticker,df):
    '''
    require df
    high volume = over 90% growth of average volume
    ,low = over 75% loss of average volume
    return dic
    '''
    av90 = average_volume(df,90)
    av90 = av90.loc[av90.index.max()]
    volume = df['volume'].loc[df.index.max()]
    if ((volume/av90)-1 >= 0.9):
        return {'symbol':ticker,'high_volume':True}
    # elif ((volume/av90)-1 <-0.75):
    #     return {'symbol':ticker,'low_volume':True}


def average_volume(df, span):
    '''
    pick 3M data for analysis and calculate ewm
    return today's ema
    '''
    df = df.sort_index(ascending=True).last("6M")
    df = df['volume'].rolling(window=90).mean()

    return df
