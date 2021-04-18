import logging
logger = logging.getLogger('main.52week')


def fiftytwo_week(ticker, df):
    '''
    52 weeks high is in -0.1
    52 weeks low is in 0.1
    52weeks trending: highest, lowest is 0
    '''
    price = df['adjusted'][-1]
    high,low = high_low(df,'52w')
    high_range = (price/high)-1
    low_range = (price/low)-1
    if (-0.1 <= high_range <= 0 ):
        return {'symbol':ticker,'yr_high':True}
    elif (0 <= low_range <= 0.1):
        return {'symbol':ticker,'yr_low':True}


def high_low(df,span):
    '''
    return max and min in time span
    on 'adjusted close'
    '''
    df = df.sort_index(ascending=True).last(span)['adjusted']

    return df.max(),df.min()


def if_fiftytwo_high(df):
    '''
    util function, to decide if is in 52week high trend(within 10%)
    '''
    price = df['adjusted'][-1]
    high,low = high_low(df,'52w')
    high_range = (price/high)-1
    low_range = (price/low)-1
    if (-0.1 <= high_range <= 0 ):
        return True


def if_fiftytwo_low(df):
    '''
    util function, to decide if is in 52week low trend(within -10%)
    '''
    price = df['adjusted'][-1]
    high,low = high_low(df,'52w')
    high_range = (price/high)-1
    low_range = (price/low)-1
    if (0 <= low_range <= 0.1 ):
        return True
