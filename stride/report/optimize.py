import os
import pandas as pd
import numpy as np
import numpy.random as npr
import logging
import scipy.optimize as sco
from ..models import Quote
logger = logging.getLogger('main.optimize')


def optimize(s):
    path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(path, '../utils/tsxci_industry.csv')
    df = pd.read_csv(filename, na_filter = False)
    df.columns = ['symbol','company', 'sector', 'industry']
    df.set_index('symbol', inplace=True)
    ind_list = ['Metals & Mining','Exploration & Production','Banks','Integrated Oil & Gas','Application Software','Independent Power Producers','Autos']
    type = 'min_sharpe'

    for ind in ind_list:
        list = df[df.industry==ind].index.tolist()
        data = contact_df(s, list)
        portfolio, ratios = get_portfolio_ratios(data, list, type)

        logger.info('%s Portfolio at %s: %s' % (ind, type, portfolio))
        logger.info('%s Ratio: P-Return: %s,  P-Volatility: %s, Sharpe: %s ' % (ind,
                                                                                round(ratios[0]*100,2),
                                                                                round(ratios[1]*100,2),
                                                                                round(ratios[2],2) ))


def contact_df(s, list):
    '''
    return df contacted with adjusted columns each for symbol
    '''
    df_list = []
    for ticker in list:
        df = pd.read_sql(s.query(Quote).filter(Quote.symbol == ticker).statement, s.bind, index_col='date')
        df.sort_index(inplace=True)
        df = df[(df != 0).all(1)]
        df.rename(columns={'adjusted':ticker}, inplace=True)
        df = df[ticker]
        df_list.append(df)
    return pd.concat(df_list, axis=1).dropna()


def get_portfolio_ratios(data, list, type):
    log_returns = np.log(data.pct_change() + 1).dropna()
    portfolio, ratios = convex_optimization(log_returns,type)
    pf_dic = dict(zip(list, portfolio))
    pf_dic = {x:y for x,y in pf_dic.items() if y!=0}
    portfolio = str(pf_dic).replace("{","").replace("}", "")
    return portfolio, ratios


def convex_optimization(log_returns, type):
    number = 1000
    stock_num = len(log_returns.columns)
    weights = npr.rand(number, stock_num)
    weights/= np.sum(weights, axis=1).reshape(number, 1)
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bnds = tuple((0, 1) for x in range(stock_num))


    def statistics(weights):
        weights = np.array(weights)
        pret = np.sum(log_returns.mean() * weights * 252)
        pvols = np.sqrt(np.dot(weights.T, np.dot(log_returns.cov() * 252, weights)))
        return np.array([pret, pvols, pret / pvols])


    def min_sharpe(weights):
        return -statistics(weights)[2]


    def min_volatility(weights):
        return statistics(weights)[1]


    def max_return(weights):
        return -statistics(weights)[0]


    if(type == 'min_sharpe'):
        opts = sco.minimize(min_sharpe, stock_num * [1 / stock_num],
                        method='SLSQP', bounds=bnds, constraints=cons)
        return opts['x'].round(1)*100, statistics(opts['x'].round(1))
    elif(type == 'min_vol'):
        opts1 = sco.minimize(min_volatility, stock_num * [1 / stock_num],
                        method='SLSQP', bounds=bnds, constraints=cons)
        return opts1['x'].round(1)*100, statistics(opts1['x'].round(1))
    elif(type == 'max_return'):
        opts2 = sco.minimize(max_return, stock_num * [1 / stock_num],
                        method='SLSQP', bounds=bnds, constraints=cons)
        return opts2['x'].round(1)*100, statistics(opts2['x'].round(1))
