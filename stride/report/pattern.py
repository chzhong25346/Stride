import logging
from .rules import *
logger = logging.getLogger('main.pattern')


def find_pattern(ticker, df):
    '''
    find pattern according pattern rules
    and return dict to report.py
    '''
    if (fallingThreeMethods(df)):
        return {'symbol':ticker,'pattern':'Falling Three Methods'}
    elif (eveningDojiStar(df)):
        return {'symbol':ticker,'pattern':'evening doji star'}
    elif (eveningStar(df)):
        return {'symbol':ticker,'pattern':'evening star'}
    elif (abandonedBaby(df)):
        return {'symbol':ticker,'pattern':'abandoned baby'}
    elif (darkCloudCover(df)):
        return {'symbol':ticker,'pattern':'dark cloud cover'}
    elif (downsideTasukiGap(df)):
        return {'symbol':ticker,'pattern':'downside tasuki gap'}
    elif(longLeggedDoji(df)):
        return {'symbol':ticker,'pattern':'long legged doji'}
    elif(gravestoneDoji(df)):
        return {'symbol':ticker,'pattern':'gravestone doji'}
    elif(dragonflyDoji(df)):
        return {'symbol':ticker,'pattern':'dragonfly doji'}
    elif (doji(df)):
        return {'symbol':ticker,'pattern':'doji'}
    elif (engulfing(df)):
        return {'symbol':ticker,'pattern':'engulfing'}
    elif (hammer(df)):
        return {'symbol':ticker,'pattern':'hammer'}
    elif (invertedHammer(df)):
        return {'symbol':ticker,'pattern':'inverted hammer'}
    elif (haramiCross(df)):
        return {'symbol':ticker,'pattern':'harami cross'}
    elif (harami(df)):
        return {'symbol':ticker,'pattern':'harami'}
    elif (longBody(df)):
        return {'symbol':ticker,'pattern':'long body'}
    elif (marubozu(df)):
        return {'symbol':ticker,'pattern':'marubozu'}
