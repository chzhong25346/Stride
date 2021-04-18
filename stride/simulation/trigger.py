import logging
logger = logging.getLogger('main.trigger')


def buy_strategy_a(df):
    # try:
    #     return df[(df['volume_price']>0) & (df['macd']=='buy')].index.tolist()
    # except Exception as e:
    #     logger.debug('bull_hivolume_uptrend: Missing Field in Report for Calculation!')
    #     pass
    pass

# new update strategy Oct 25 2019
def buy_strategy_b(df):
    try:
        return df[(df['yr_high'] == 1) & (df['downtrend'] == 0) & (df['uptrend'] == 1) &(df['macd'] == 'buy') &
                (df['high_volume'] == 1)].index.tolist()
    except Exception as e:
        logger.debug('bull_hivolume_uptrend: Missing Field in Report for Calculation!')
        pass



# def bull_oneyrlow_doji_hivolume(df):
#     '''
#     52week low and has any doji and high_volume
#     return tickers
#     '''
#     try:
#         return df[((df['high_volume']>0) | (df['support']>0)) & (df['uptrend']>0)].index.tolist()
#     except Exception as e:
#         logger.debug('bull_oneyrlow_doji_hivolume: Missing Field in Report for Calculation!')
#         pass

####################


def sell_strategy_a(df):
    try:
        return df[(df['yr_high'] == 0) & (df['yr_low'] == 0) & (df['downtrend'] == 1) &
                (df['high_volume'] == 1) & (df['uptrend'] == 0)].index.tolist()
    except Exception as e:
        logger.debug('bear_hivolume_downtrend: Missing Field in Report for Calculation!')
        pass


# def bear_oneyrhigh_doji_downtrend(df):
    #Retired
    # '''
    # 52week high and has any doji and down trend
    # return tickers
    # '''
    # try:
    #     return df[(df['yr_high']>0) & (df['pattern'].str.contains("doji")) ].index.tolist()
    # except Exception as e:
    #     logger.debug('bear_oneyrhigh_doji_downtrend: Missing Field in Report for Calculation!')
    #     pass
    # pass
