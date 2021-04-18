import logging
logger = logging.getLogger('main.support')


def support(ticker, df):
    today = df.iloc()[-1]
    supp = support_price(df)
    if(supp is not None):
        range = (today.close/supp)-1
        if (-0.02<=range<=0.02):
            return {'symbol':ticker,'support':True}


def ema(df, span):
    # pull up one and half year df
    df = df.sort_index(ascending=True).last("78w")
    df = df['adjusted'].ewm(span=span, adjust=False).mean()

    return df


def support_price(df):
    ema21 = ema(df,21)
    ema5 = ema(df,5)
    delta = ema5 - ema21
    df['delta'] = delta < 0
    df.reset_index(inplace=True)
    temp = df.iloc[0:0]
    final = df.iloc[0:0]
    for index, row in df.iterrows():
        if(row.delta == False):
            temp = temp[temp.low == temp.low.min()]
            final = final.append(temp)
            temp = temp.iloc[0:0]
        elif(row.delta == True):
            temp = temp.append(row)
            if(row.date == df.iloc[-1].date):
                temp = temp[temp.low == temp.low.min()]
                final = final.append(temp)
    final.sort_values('low', ascending=True, inplace=True)
    if(final.symbol.count() > 1):
        final = final.drop(final[final.date < final.iloc[0].date].index)
    if(final.symbol.count() > 1):
        x1 = df[(df.date == final.iloc[0].date)].index.values[0]+1
        y1 = df[(df.date == final.iloc[0].date)].low.values[0]
        x2 = df[(df.date == final.iloc[1].date)].index.values[0]+1 -x1
        y2 = df[(df.date == final.iloc[1].date)].low.values[0]
        b = y1
        m = (y2-y1)/(x2)
        today_x = df[(df.date == df.iloc[-1].date)].index.values[0]+1 -x1
        today_y = b+m*today_x

        return today_y
