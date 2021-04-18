import datetime as dt
import pandas as pd
import logging
from ..models import Quote
logger = logging.getLogger('main.quote')


def get_quote(list,s):
    '''
    get today close price from a ticker
    return list = [dic{ticker:price},{}...]
    '''
    order_list = []
    for ticker in list:
        # today's date
        date = dt.datetime.today().strftime("%Y-%m-%d")
        df = pd.read_sql(s.query(Quote).filter(Quote.symbol == ticker).statement, s.bind, index_col='date')
        df.sort_index(inplace=True)
        # today's df - close price
        price = df.iloc()[-1]['close']
        order_list.append({ticker:price})

    return order_list
