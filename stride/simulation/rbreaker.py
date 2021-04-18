import sys
import logging
import yaml,os
logger = logging.getLogger('main.rbreaker')
import pandas as pd
from db.remove import *
from db.write import *
from .trade import *
from db.read import read_table_df_Engine,read_table_df_nodrop_Engine

os.path.dirname(os.path.realpath(__file__))


def rbreaker(engine_simulation, engine_dailydb):
    try:
        with open("config.yaml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
    except Exception as e:
        logger.error('config.yaml not found or no subscriber entry!')
        logger.error(e)
        sys.exit(1)

    # reads subscribe -  config.yaml
    subscribes = cfg['Rbreaker']['sub']
    # if there are subscribers
    if subscribes:
        # ticker is in xx.to format
        for ticker in subscribes:
            day = read_table_df_Engine(ticker,engine_dailydb).iloc()[-1]
            date = day.name
            high = day.high
            close = day.close
            low = day.low
            foreseen_sell = high + 0.35 * (close - low)
            foreseen_buy = low - 0.35 * (high - close)
            reverse_sell = 1.07 / 2 * (high + low) - 0.07 * low
            reverse_buy = 1.07 / 2 * (high + low) - 0.07 * high
            breakout_buy = foreseen_sell + 0.25 * (foreseen_sell - foreseen_buy)
            breakout_sell = foreseen_buy - 0.25 * (foreseen_sell - foreseen_buy)
            # R-Breaker dict
            dict_rbreaker = {'date':date, 'ticker':ticker, 'foreseen_sell':round(foreseen_sell,2),'foreseen_buy':round(foreseen_buy,2),'reverse_sell':round(reverse_sell,2),'reverse_buy':round(reverse_buy,2),'breakout_buy':round(breakout_buy,2),'breakout_sell':round(breakout_sell,2)}
            # R-Breaker dataframe
            df_rbreaker = pd.DataFrame.from_records([dict_rbreaker],index='date')
            df_rbreaker.index = pd.to_datetime(df_rbreaker.index)
            # delete rows that have specific ticker name in 'ticker' filed - remove.py
            delete_by_fieldValue_Engine('rbreaker','ticker',ticker,engine_simulation)
            # write df to sql - write.py
            df_to_sql_prikey('rbreaker',df_rbreaker,engine_simulation,'date')
            logger.debug('updating %s for %s' % (date,ticker))
            ################ R-Breaker TRADING #############
            # the previous day df
            preday = read_table_df_Engine(ticker,engine_dailydb).iloc()[-2]
            preday_high = preday.high
            preday_close = preday.close
            preday_low = preday.low
            preday_foreseen_buy = preday_low - 0.35 * (preday_high - preday_close)
            buy_quote = [{ticker:preday_foreseen_buy}]
            sell_quote = [{ticker:close}]
            # if buy is possible, foreseen more 2 cents to buy
            if (low <= preday_foreseen_buy+0.02 <= high):
                # excute buy order at foreseen buy price
                execute_order(buy_quote,10000,"buy",engine_simulation)
                # excute sell order at close price
                execute_order(sell_quote,10000,"sell",engine_simulation)
                logger.debug('[%s] - Buy @ %s - Sell @ %s' % (ticker,preday_foreseen_buy,preday_close))
            else:
                logger.debug('No opportunity to trade - [%s]', ticker)
