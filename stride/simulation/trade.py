import datetime as dt
import pandas as pd
import logging
from ..db.mapping import map_transaction, map_holding
from ..db.write import bulk_save
from ..models import Transaction, Holding
from ..utils.fetch import get_yahoo_finance_price, get_yahoo_bvps, get_yahoo_cr
logger = logging.getLogger('main.trade')


def execute_order(list, type, s):
    # Get Db Name
    db_name = s.bind.url.database
    # for each quote as dict in buy list
    for dict in list:
        # ticker,price in list format retrieved from dict
        ticker, price = zip(*dict.items())
        # ticker value
        ticker = ticker[0]
        # Current Close
        cp = float(price[0])
        try:
            # BUY
            if type == 'buy':
                # Fetch and Calculate Capital
                if db_name == 'tsxci':
                    bvps = get_yahoo_bvps(ticker+'.TO')
                    cr = get_yahoo_cr(ticker+'.TO')
                elif db_name == 'csi300' and 'SH' in ticker:
                    bvps = get_yahoo_bvps(ticker.replace('SH','SS'))
                    cr = get_yahoo_cr(ticker.replace('SH','SS'))
                else:
                    bvps = get_yahoo_bvps(ticker)
                    cr = get_yahoo_cr(ticker)
                if cp > 0 and bvps is not None and cr is not None:
                    adjusted_cap = _get_adjusted_cap(cp, bvps, cr)
                    if adjusted_cap >= cp:
                        # execute buy function
                        buy(dict, adjusted_cap, s)
            # SELL
            elif cp > 0 and type == 'sell':
                # print(db_name, dict, adjusted_cap)
                # execute buy function
                sell(dict, None, s)
        except:
            logger.debug('Failed to buy %s-%s ', db_name, ticker)


def buy(dict,cap,s):
    build_transaction(dict,cap,'buy',s)
    build_holding(dict,s)


def sell(dict,cap,engine):
    # if there is already a holding table and found ticker in holding table
    if build_transaction(dict,cap,'sell',engine) is not False:
        # then transaction is completed and holding table is able to build and reflush
        build_holding(dict,engine)


def build_transaction(dict,cap,type,s):
    # current date
    date = dt.datetime.today().strftime("%Y-%m-%d")
    # ticker,price in list format retrieved from dict
    ticker,price = zip(*dict.items())
    # ticker value
    ticker = ticker[0]
    # price value is float
    price = float(price[0])
    # if type is buy qty is potitive and settlement is negative(sepnding)
    if(type == 'buy'):
        qty = int(cap/price)
        settlement = (price*qty)*-1
    # if type is sell, qty is negative and settlement is potitive(income)
    elif(type == 'sell'):
        # read holding table, if False, table not exits
        df_existing_holding = pd.read_sql(s.query(Holding).statement, s.bind, index_col='symbol')
        # if there is holding table and ticker is found in holding df
        if (ticker in df_existing_holding.index.unique()):
            # # if sell off all
            # if cap == 10000:
            # retrieve quntity which is negative
            qty = (df_existing_holding[(df_existing_holding.index==ticker)].quantity.tolist()[0])*-1
            # # if sell off a half
            # elif cap == 5000:
            #     # retrieve quntity which is negative
            #     qty = ((df_existing_holding[(df_existing_holding.index==ticker)].quantity.tolist()[0])*-1)/2
            # settlement amount is positive(income)
            settlement = abs(price*qty)
        # if no table or no ticker in holding
        else:
            logger.debug('No table or not holding: %s, cannot %s' % (ticker,type))
            return False
    # TRANSACTION dict
    dict_transaction = {'date':date, 'symbol':ticker, 'type':type,'quantity':qty,'price':price,'settlement':settlement}
    # TRANSACTION dataframe
    df_transaction = pd.DataFrame.from_records([dict_transaction],index='date')
    df_transaction.index = pd.to_datetime(df_transaction.index)
    # mappiong df to sql - db.mapping, and save to db - db.write
    bulk_save(s, map_transaction(df_transaction))
    logger.debug('(ORDER) %s %s %s shares at %s/share' % (type,ticker,qty,price))


def build_holding(dict,s):
    # ticker,price in list format retrieved from dict
    ticker,price = zip(*dict.items())
    # ticker value
    ticker = ticker[0]
    # price value is float
    price = float(price[0])
    # get transaction
    transaction = pd.read_sql(s.query(Transaction).statement, s.bind, index_col='id')
    # all rows in specified ticker
    df_ticker = transaction[(transaction['symbol']==ticker)]
    # all rows in specified ticker and type = buy
    df_ticker_buy = transaction[(transaction['symbol']==ticker) & (transaction['type']=='buy')]
    # sum up quantity of this ticker all of buy and sell records
    qty = df_ticker['quantity'].sum()
    # if there is nothing holding on
    if (qty != 0):
        # average cost each row: sum of (price*qty) / sum of 'qty'
        avg_cost = sum(df_ticker_buy.price*df_ticker_buy.quantity)/sum(df_ticker_buy.quantity)
        # market price is the price from quote that is contained in the dict
        mkt_price = price
        # book value is average cost times quantity
        book_value = avg_cost*qty
        # market value is market price times quantity
        mkt_value = mkt_price*qty
        # changes
        change_dollar = mkt_value - book_value
        change_percent = (mkt_value/book_value-1)*100
        # construct holding dictionary
        dict_holding = {'symbol':ticker,'quantity':qty,'avg_cost':avg_cost,'mkt_price':mkt_price,'book_value':book_value,'mkt_value':mkt_value,'change_dollar':round(change_dollar,2),'change_percent':round(change_percent,2),'note':None}
        # constract holding dataframe from the dictionary
        df_holding = pd.DataFrame.from_records([dict_holding])
        # delete ticker in holding table
        s.query(Holding).filter(Holding.symbol == ticker).delete(synchronize_session=False)
        s.commit()
        # update new rows of this ticker - db.mapping and save to db db.write
        bulk_save(s, map_holding(df_holding))
    # if quantity is zero
    else:
        # delete ticker in holding table - remove.py
        s.query(Holding).filter(Holding.symbol == ticker).delete(synchronize_session=False)
        s.commit()


def _get_adjusted_cap(cp, bvps, cr):
    shares = 1000 / cp
    delta_ps = cp - bvps
    delta_cash = shares * delta_ps
    adjusted_cap = 1000 - delta_cash
    if cr < 1 and cr > 0:
        return int(adjusted_cap * cr)
    elif cr > 1:
        return int(adjusted_cap)
