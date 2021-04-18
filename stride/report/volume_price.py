import logging
import datetime as dt
logger = logging.getLogger('main.volume_price')


def volume_price(ticker, df):
    today = dt.datetime.today().strftime("%Y-%m-%d")
    df = df.copy()
    # df.set_index('date', inplace=True)
    ema21 = ema(df,21)
    ema5 = ema(df,5)
    av90 = average_volume(df)
    df['ema_delta'] = round(((ema5/ema21)-1)*100,2)
    df['volume_delta'] = round((df.volume/av90)-1,2)
    df = df[df['volume_delta']>=0.9]
    df = df[['ema_delta','volume_delta']]
    try:
        date = df.index[-1].strftime("%Y-%m-%d")
        if (df.ema_delta.count() >= 2) and (today == date):
            df = df.tail(2)
            previous = df.iloc()[-2]
            now = df.iloc()[-1]
            if (now.ema_delta > 0) and(previous.ema_delta < 0):
                return {'symbol':ticker,'volume_price':True}
            else:
                return {'symbol':ticker,'volume_price':False}
    except:
        pass


def ema(df, span):
    df = df.sort_index(ascending=True).last("18M")
    df = df['adjusted'].ewm(span=span, adjust=False).mean()
    return df


def average_volume(df):
    df = df.sort_index(ascending=True).last("18M")
    df = df['volume'].rolling(window=90).mean()
    return df
