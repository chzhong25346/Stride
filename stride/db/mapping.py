import pandas as pd
import datetime as dt
from ..utils.fetch import fetch_index, get_daily_adjusted
from ..utils.util import gen_id
from ..models import Index, Quote, Report, Transaction, Holding, St1, St49, St97, St100
import logging
logger = logging.getLogger('main.mapping')


def map_index(index_name):
    df = fetch_index(index_name)
    df_records = df.to_dict('records')
    model_instnaces = [Index(
        symbol = record['symbol'],
        company = record['company'],
        # sector = record['sector'],
        # industry = record['industry']
    ) for record in df_records]

    return model_instnaces


def map_quote(df, ticker):
    df_records = df.to_dict('records')
    model_instnaces = [Quote(
        id = gen_id(ticker+str(record['date'])),
        symbol = ticker,
        date = record['date'],
        open = record['open'],
        high = record['high'],
        low = record['low'],
        close = record['close'],
        adjusted = record['adjusted close'],
        volume = record['volume']
    ) for record in df_records]

    return model_instnaces


def map_fix_quote(sr, ticker):
    model_instance = Quote(
        id = gen_id(ticker+str(sr['date'])),
        symbol = ticker,
        date = sr['date'],
        open = sr['open'],
        high = sr['high'],
        low = sr['low'],
        close = sr['close'],
        adjusted = sr['adjusted close'],
        volume = sr['volume']
        )
    return model_instance


def map_report(config,df):
    date = dt.datetime.today().strftime("%Y-%m-%d")
    df_records = df.to_dict('records')
    model_instnaces = [Report(
        symbol = record['symbol'],
        date = date,
        id = gen_id(record['symbol']+str(date)),
        yr_high = record['yr_high'],
        yr_low = record['yr_low'],
        downtrend = record['downtrend'],
        uptrend = record['uptrend'],
        high_volume = record['high_volume'],
        rsi = record['rsi'],
        macd = record['macd'],
        bolling = record['bolling'],
        # adx = record['adx'],
        # low_volume = record['low_volume'],
        # pattern = record['pattern'],
        # support = record['support'],
        # volume_price = record['volume_price']
    ) for record in df_records]
    logger.info('Mapping completed.')

    return model_instnaces


def map_transaction(df):
    date = dt.datetime.today().strftime("%Y-%m-%d")
    df_records = df.to_dict('records')
    model_instnaces = [Transaction(
        id = gen_id(record['symbol'] + record['type'] + str(date)),
        date = date,
        symbol = record['symbol'],
        price = record['price'],
        quantity = record['quantity'],
        settlement = record['settlement'],
        type = record['type'],
    ) for record in df_records]
    logger.info('Mapping completed.')

    return model_instnaces


def map_holding(df):
    df_records = df.to_dict('records')
    model_instnaces = [Holding(
        symbol = record['symbol'],
        avg_cost  = record['avg_cost'],
        quantity = record['quantity'],
        book_value  = record['book_value'],
        change_dollar  = record['change_dollar'],
        change_percent  = record['change_percent'],
        mkt_price  = record['mkt_price'],
        mkt_value  = record['mkt_value'],
        note  = record['note'],
    ) for record in df_records]
    logger.info('Mapping completed.')

    return model_instnaces


def map_st1(df):
    df_records = df.to_dict('records')
    model_instnaces = [St1(
        date = record['date'],
        gas = record['gas'],
        oil = record['oil'],
        bitumen = record['bitumen'],
    ) for record in df_records]
    logger.info('Mapping completed.')

    return model_instnaces


def map_st49(df):
    df_records = df.to_dict('records')
    model_instnaces = [St49(
        date = record['date'],
        total  = record['total'],
        drill_to_ld = record['drill_to_ld'],
        re_entry = record['re_entry'],
        resumption = record['resumption'],
        set_surface = record['set_surface'],
    ) for record in df_records]
    logger.info('Mapping completed.')

    return model_instnaces


def map_st97(df):
    df_records = df.to_dict('records')
    model_instnaces = [St97(
        id = gen_id(str(record['application']) + record['licensee'] + str(record['date'])),
        date = record['date'],
        licensee  = record['licensee'],
        purpose = record['purpose'],
        type = record['type'],
    ) for record in df_records]
    logger.info('Mapping completed.')

    return model_instnaces


def map_st100(df):
    df_records = df.to_dict('records')
    model_instnaces = [St100(
        date = record['date'],
        total  = record['total'],
    ) for record in df_records]
    logger.info('Mapping completed.')

    return model_instnaces
