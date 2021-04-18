import logging
from .fiftytwoWeek import if_fiftytwo_high,if_fiftytwo_low
logger = logging.getLogger('main.rules')


# UTILS
# open/close -1
def day_range(day):
    return (day['open']/day['close'])-1


# if it is a doji
def if_doji(day):
    '''
    util function, to decide if a day is a doji
    '''
    if (abs(day['open']/day['close'] -1) < 0.001):
        return True


# PATTERN RULES
def doji(df):
    today = df.iloc()[-1]
    if (abs(day_range(today)) < 0.001):
        return True


def dragonflyDoji(df):
    today = df.iloc()[-1]
    #  open and close price are at the high of the day
    high_of_day = (abs(today['open']/today['high'] -1) < 0.005 and abs(today['close']/today['high'] -1) < 0.005)
    long_lower_shadow = (today['low']/today['close'] - 1) < -0.02
    if (if_doji(today) and high_of_day and long_lower_shadow):
        return True


def gravestoneDoji(df):
    today = df.iloc()[-1]
    #   A doji line that develops when the Doji is at, or very near, the low of the day.
    low_of_day = (abs(today['open']/today['low'] -1) < 0.005 and abs(today['close']/today['low'] -1) < 0.005)
    long_higher_shadow = (today['high']/today['close'] - 1) > 0.02
    if (if_doji(today) and low_of_day and long_higher_shadow):
        return True


def longLeggedDoji(df):
    today = df.iloc()[-1]
    # This candlestick has long upper and lower shadows
    long_leg = (today['high']/today['low']-1) > 0.03
    # Doji in the middle of the day's trading range
    middle_of_day = (today['high'] + today['low'])/2
    if(if_doji(today) and long_leg and (today['close'] == middle_of_day or today['open'] == middle_of_day) ):
        return True


def engulfing(df):
     today = df.iloc()[-1]
     firstday = df.iloc()[-2]
     today_delta = today['close'] - today['open']
     firstday_delta = firstday['close'] - firstday['open']
     if ((abs(today_delta)-abs(firstday_delta)) >=0):
         # find day up or down
         if(firstday_delta>0 and today_delta<0):
             if((today['open']>firstday['close']) and (today['close']<firstday['open'])):
                return True
         elif(firstday_delta<0 and today_delta>0):
             if((today['open']<firstday['close']) and (today['close']>firstday['open'])):
                return True


def harami(df):
     today = df.iloc()[-1]
     firstday = df.iloc()[-2]
     today_delta = today['close'] - today['open']
     firstday_delta = firstday['close'] - firstday['open']
     # find day up or down
     if(firstday_delta>0 and today_delta<0):
         if((today['open']<firstday['close']) and (today['close']>firstday['open'])):
            return True
     elif(firstday_delta<0 and today_delta>0):
         if((today['open']>firstday['close']) and (today['close']<firstday['open'])):
            return True


def haramiCross(df):
     today = df.iloc()[-1]
     firstday = df.iloc()[-2]
     today_delta = today['close'] - today['open']
     firstday_delta = firstday['close'] - firstday['open']
     # find day up or down
     if(firstday_delta>0 and today_delta<0 and if_doji(today)):
         if((today['open']<firstday['close']) and (today['close']>firstday['open'])):
            return True
     elif(firstday_delta<0 and today_delta>0 and if_doji(today)):
         if((today['open']>firstday['close']) and (today['close']<firstday['open'])):
            return True


def hammer(df):
    today = df.iloc()[-1]
    # significantly lower after the open
    lower_after_open = (today['open']/today['low']-1) > 0.02
    # rallies to close well above the intraday low
    close_above_low = (today['close']/today['low']-1) > 0.02
    small_intraday = abs(day_range(today)) <= 0.008
    close_near_high = abs(today['close']/today['high']) <= 0.001
    open_near_high = abs(today['open']/today['high']) <= 0.001
    # this candlestick forms during a decline
    if(if_fiftytwo_low(df) and lower_after_open and close_above_low and close_near_high or open_near_high):
        return True


def invertedHammer(df):
    today = df.iloc()[-1]
    # significantly lower after the open
    higher_after_open = (today['open']/today['high']-1) < -0.02
    # rallies to close well above the intraday low
    close_above_high = (today['close']/today['high']-1) < -0.02
    small_intraday = abs(day_range(today)) <= 0.008
    close_near_low = abs(today['close']/today['low']) <= 0.001
    open_near_low = abs(today['open']/today['low']) <= 0.001
    # this candlestick forms during a decline
    if(if_fiftytwo_low(df) and higher_after_open and close_above_high and close_near_low or open_near_low):
        return True


def marubozu(df):
    # no shadow extending from the body
    today = df.iloc()[-1]
    no_shadow = abs(day_range(today)) == (today['high']/today['low']-1)
    if (no_shadow):
        return True


def longBody(df):
    today = df.iloc()[-1]
    long_body = abs(day_range(today)) >= 0.03


def abandonedBaby(df):
    firstday = df.iloc()[-3]
    secondday = df.iloc()[-2]
    today = df.iloc()[-1]
    firstday_delta = firstday['close'] - firstday['open']
    today_delta = today['close'] - today['open']
    gap_up = (secondday['low'] > firstday['high']) and (secondday['low'] > today['high'])
    gap_down = (secondday['high'] < firstday['low']) and (secondday['high'] < today['low'])
    # first day up and today down, and there is a gap
    if (firstday_delta>0 and today_delta<0 and gap_up or gap_down ):
        # if second day is a doji
        if(if_doji(secondday)):
            return True
    # first day down and today up, and there is a gap
    elif (firstday_delta<0 and firstday_delta>0 and gap_up or gap_down):
        # if second day is a doji
        if(if_doji(secondday)):
            return True


def darkCloudCover(df):
    firstday = df.iloc()[-2]
    today = df.iloc()[-1]
    firstday_range = day_range(firstday)
    today_range = day_range(today)
    open_new_high = today['open'] > firstday['high']
    close_low_midpoint = firstday['open'] < today['close'] < (firstday['high'] + firstday['low'])/2
    # a long white body / A bearish reversal pattern / next day opens at a new high/
    # closes below the midpoint of the body of the first day.
    if(if_fiftytwo_high(df) and firstday_range > 0.2 and today_range < 0 and open_new_high and close_low_midpoint):
        return True


def downsideTasukiGap(df):
    firstday = df.iloc()[-3]
    secondday = df.iloc()[-2]
    today = df.iloc()[-1]
    firstday_range = day_range(firstday)
    secondday_range = day_range(secondday)
    today_range = day_range(today)
    #  mid-day has gapped below the first one
    gap = firstday['low'] > secondday['high']
    #  third day is white and opens within the body of the second day
    opens_within = secondday ['open'] <= today['open'] <= secondday ['close']
    # closes in the gap between the first two days but does not close the gap
    close_in_gap = secondday['high'] <= today['close']  < firstday['low']
    # A continuation pattern with a long, black body followed by another black body that has gapped below the first one.
    if(firstday_range<0 and firstday_range<=-0.02 and secondday_range<0 and today_range>0):
        if(opens_within and close_in_gap):
            return True


def eveningDojiStar(df):
    firstday = df.iloc()[-3]
    secondday = df.iloc()[-2]
    today = df.iloc()[-1]
    firstday_range = day_range(firstday)
    secondday_range = day_range(secondday)
    today_range = day_range(today)
    #  The uptrend continues with a large white body.
    large_white_body = firstday_range > 0.02
    # The next day opens higher
    open_higher = secondday['open'] > firstday['high']
    # The next day closes below the midpoint of the body of the first day.
    close_low_midpoint = firstday['open'] < today['close'] < (firstday['high'] + firstday['low'])/2
    # uppper trending / first day large white / second day higher and doji / today close midpoint of first day
    if(if_fiftytwo_high(df) and large_white_body and open_higher and if_doji(secondday) and close_low_midpoint):
        return True


def eveningStar(df):
    firstday = df.iloc()[-3]
    secondday = df.iloc()[-2]
    today = df.iloc()[-1]
    firstday_range = day_range(firstday)
    secondday_range = day_range(secondday)
    today_range = day_range(today)
    #  The uptrend continues with a large white body.
    large_white_body = firstday_range > 0.02
    # The next day opens higher
    open_higher = secondday['open'] > firstday['high']
    # The next day closes below the midpoint of the body of the first day.
    close_low_midpoint = firstday['open'] < today['close'] < (firstday['high'] + firstday['low'])/2
    # uppper trending / first day large white / second day higher and doji / today close midpoint of first day
    if(if_fiftytwo_high(df) and large_white_body and open_higher and close_low_midpoint):
        return True


def fallingThreeMethods(df):
    firstday = df.iloc()[-5]
    today = df.iloc()[-1]
    next3 = df.iloc()[-2]
    next2 = df.iloc()[-3]
    next1 = df.iloc()[-4]
    # A long black body
    long_black_body = day_range(firstday) > 0.02
    # following three days ranges, followed by three small body days
    small_bodys = False
    for body in (day_range(next1),day_range(next2),day_range(next3)):
        if (body < 0.02):
            small_bodys = True
        else:
            small_bodys = False
            break
     # each fully contained within the range of the high and low of the first day
    inrange = False
    for day in (next1,next2,next3):
        if(firstday['high']>= day['open'] >= firstday['low'] and firstday['high']>= day['close'] >= firstday['low']):
         inrange = True
        else:
         inrange = False
         break
    # The fifth day closes at a new low.
    new_low = today['close'] < firstday['low']
    if (if_fiftytwo_low(df) and long_black_body and small_bodys and inrange and new_low and day_range(today)<0):
        return True
