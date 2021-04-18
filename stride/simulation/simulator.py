import datetime as dt
import pandas as pd
import logging
import datetime as dt
from ..db.read import *
from ..db.write import *
from .trigger import buy_strategy_a, buy_strategy_b, sell_strategy_a
from .quote import get_quote
from .trade import execute_order
# from .rbreaker import rbreaker
from ..models import Index, Quote, Report, Holding, Transaction
from ..report.support import support_price, ema
logger = logging.getLogger('main.simulator')


def simulator(s):
    # today's date
    date = dt.datetime.today().strftime("%Y-%m-%d")
    # read report
    df_report = pd.read_sql(s.query(Report).filter(Report.date == date).statement, s.bind, index_col='symbol')
    # BUY list
    all_in, half_in = buy_list(df_report)
    # SELL list
    all_out = sell_list(df_report)
    # BUY Order
    if all_in:
        quote_list = get_quote(all_in,s)
        # execute buy order - trade.py
        execute_order(quote_list,10000,"buy",s)
    if half_in:
        quote_list = get_quote(half_in,s)
        # execute buy order $5000 - trade.py
        execute_order(quote_list,5000,"buy",s)
    # SELL Order
    if all_out:
        quote_list = get_quote(all_out,s)
        # execute sell order - all holding quantity - trade.py
        execute_order(quote_list,10000,"sell",s)
    # if half_out:
    #     quote_list = get_quote(half_out,s)
    #     # execute sell order - half holding quntity - trade.py
    #     execute_order(quote_list,5000,"sell",s)
    # refreshing holding table
    refresh_holding(s)
    # rbreaker(engine_simulation, engine_dailydb)


def buy_list(df):
    '''
    return lists of tickers based on Buy triggers
    '''
    #  trigger.py
    all_in = buy_strategy_a(df)
    # logger.debug('Buy All: %s', ','.join(all_in))
    half_in = buy_strategy_b(df)
    logger.debug('Buy Half: %s', ','.join(half_in))
    return all_in, half_in


def sell_list(df):
    '''
    return lists of tickers based on Sell triggers
    '''
    # trigger.py
    all_out = sell_strategy_a(df)
    logger.debug('Sell All: %s', ','.join(all_out))
    # half_out = None
    # half_out = bear_oneyrhigh_doji_downtrend(df)
    # logger.debug('Sell Half: %s', ','.join(half_out) )
    return all_out


def refresh_holding(s):
    '''
    read existing holding table, get quote for every ticker
    execute sql to update needed fields.
    '''
    df_holding = pd.read_sql(s.query(Holding).statement, s.bind, index_col='symbol')
    # index is ticker, make it a list
    tickerL = df_holding.index.tolist()
    # [{ticker:price},..] get quote of each ticker - quote.py
    quote_list = get_quote(tickerL,s)
    # each quote in quote list
    for dict in quote_list:
        # ticker,price in list format retrieved from dict
        ticker,price = zip(*dict.items())
        # ticker value
        ticker = ticker[0]
        # the df only includes the ticker
        df_ticker = df_holding[(df_holding.index==ticker)]
        # price value is float
        mkt_price = float(price[0])
        # quntity of the security on holding
        qty = df_ticker.quantity.sum()
        # calculate mkt_value
        mkt_value = qty*mkt_price
        # change in dollar of the security on holding, sum() makes it in int
        change_dollar = round(mkt_value - df_ticker.book_value.sum(),2)
        # change in dollar of the security on holding, sum() makes it in int
        change_percent = round((mkt_value / df_ticker.book_value.sum()-1)*100,2)
        # Check if rsi & macd happened
        trxn = pd.read_sql(s.query(Transaction).filter(Transaction.symbol == ticker).statement, s.bind, index_col='date').sort_index()
        # Latest date of buying order
        latest_trxn_date = trxn.index[-1]
        rep = pd.read_sql(s.query(Report).filter(Report.symbol == ticker).statement, s.bind, index_col='date').sort_index()
        # Ends with latest date and count back 21 days (includes latest day, 20 days)
        rep = rep[rep.index <= latest_trxn_date].iloc[-21:]
        # RSI and MACD both happened in these days
        if ((rep['rsi'] == 'buy').any() and (rep['macd'] == 'buy').any()):
            note = 'ris_macd'
        else:
            note = None
        # if change percentage lower than 2%
        # if (change_percent<=-2):
        #     note = 'Stop Loss'
        # # else to use 'Support price' - report.support.py
        # else:
        #     # read daily db return df in random order
        #     df = pd.read_sql(s.query(Quote).filter(Quote.symbol == ticker).statement, s.bind, index_col='date')
        #     # sort by old to new
        #     df.sort_index(inplace=True)
        #     # drop rows have 0
        #     df = df[(df != 0).all(1)]
        #     price = support_price(df)
        #     if(price != None):
        #         note = round(price,2)
        #     else:
        #         note = None

        # update table
        s.query(Holding).filter(Holding.symbol == ticker).update(
                                                {'mkt_price': mkt_price,
                                                'mkt_value': mkt_value,
                                                'change_dollar': change_dollar,
                                                'change_percent': change_percent,
                                                'note': note})
        s.commit()


        logger.debug('Refreshing holding: %s at $%s/share, change: $%s(%s percent) ' % (ticker,mkt_price,change_dollar,change_percent))
