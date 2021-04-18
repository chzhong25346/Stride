import smtplib
import logging
import yaml,os
import sys
import pandas as pd
import datetime as dt
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dateutil import parser
from ..models import Holding, Report
logger = logging.getLogger('main.email')

def sendMail(object, s_nasdaq, s_tsxci, s_sp100, s_csi300):
    # today's datetime
    day = dt.datetime.today().strftime("%Y-%m-%d")
    dow = parser.parse(day).strftime("%a")
    today = day + ' ' + dow
    # start talking to the SMTP server for Gmail
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.ehlo()
    # now login as my gmail user
    user = object.EMAIL_USER
    pwd = object.EMAIL_PASS
    # rcpt = object.EMAIL_TO
    rcpt = [i for i in object.EMAIL_TO.split(',')]
    try:
        s.login(user,pwd)
    except Exception as e:
        logger.error(e)

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = today
    msg['From'] = user
    msg['To'] = ", ".join(rcpt)

    html = generate_html(s_nasdaq, s_tsxci, s_sp100, s_csi300)
    attachment = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(attachment)

    # send the email
    s.sendmail(user, rcpt, msg.as_string())
    # we're done
    s.quit()


def generate_html(s_nasdaq, s_tsxci, s_sp100, s_csi300):
    # Nasdaq100
    nasdaq_holding = pd.read_sql(s_nasdaq.query(Holding).statement, s_nasdaq.bind, index_col='symbol').sort_values(by=['change_percent'],ascending=0)
    # nasdaq_uptrend = [Report.symbol for Report in s_nasdaq.query(Report).filter(Report.uptrend == 1)]
    # nasdaq_downtrend = [Report.symbol for Report in s_nasdaq.query(Report).filter(Report.downtrend == 1)]
    # nasdaq_high_volume = [Report.symbol for Report in s_nasdaq.query(Report).filter(Report.high_volume == 1)]
    # nasdaq_support = [Report.symbol for Report in s_nasdaq.query(Report).filter(Report.support == 1)]
    # TSXCI
    tsxci_holding = pd.read_sql(s_tsxci.query(Holding).statement, s_tsxci.bind, index_col='symbol').sort_values(by=['change_percent'],ascending=0)
    # tsxci_uptrend = [Report.symbol for Report in s_tsxci.query(Report).filter(Report.uptrend == 1)]
    # tsxci_downtrend = [Report.symbol for Report in s_tsxci.query(Report).filter(Report.downtrend == 1)]
    # tsxci_high_volume = [Report.symbol for Report in s_tsxci.query(Report).filter(Report.high_volume == 1)]
    # tsxci_support = [Report.symbol for Report in s_tsxci.query(Report).filter(Report.support == 1)]
    sp100_holding = pd.read_sql(s_sp100.query(Holding).statement, s_sp100.bind, index_col='symbol').sort_values(by=['change_percent'],ascending=0)
    csi300_holding = pd.read_sql(s_csi300.query(Holding).statement, s_csi300.bind, index_col='symbol').sort_values(by=['change_percent'],ascending=0)

    buy,sell = read_log()

    html = """\
    <html>
    <head></head>
    <body>
        <h3>NASDAQ 100</h3>
        {nasdaq_holding}<br>

        <h3>TSXCI</h3>
        {tsxci_holding}<br>

        <h3>SP100</h3>
        {sp100_holding}<br>

        <h3>CSI300</h3>
        {csi300_holding}<br>

        <h4> <font color="green">Long </font></h4>
        <p>{buy}</p>

        <h4> <font color="red">Short </font></h4>
        <p>{sell}</p>


    </body>
    </html>
    """

    html = html.format(nasdaq_holding=nasdaq_holding.to_html(),
                      tsxci_holding=tsxci_holding.to_html(),
                      sp100_holding=sp100_holding.to_html(),
                      csi300_holding=csi300_holding.to_html(),
                      buy = buy,
                      sell = sell)

    return html


def read_log():
    s = 'DEBUG - '
    s2 = 'INFO - '
    buy = ''
    sell = ''
    # portfolio = ''
    day = dt.datetime.today().strftime("%Y-%m-%d")
    fh = open('log.log', 'r')
    with fh as file:
        for line in file:
            if((day in line) and ('Buy All' in line)):
                buy += "<li>" + line[line.index(s) + len(s):] + "</li>"
            elif((day in line) and ('Buy Half' in line)):
                buy += "<li>" + line[line.index(s) + len(s):] + "</li>"
            elif((day in line) and ('Sell All' in line)):
                sell += "<li>" + line[line.index(s) + len(s):] + "</li>"
            # elif((day in line) and (('optimize' in line)) ):
            #     portfolio += "<li>" + line[line.index(s2) + len(s2):] + "</li>"
    fh.close()

    return buy, sell#, portfolio
