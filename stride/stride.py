from .utils.config import Config
from .utils.fetch import get_daily_adjusted, get_da_req, fetchError, get_quote_endpoint, get_yahoo_finance_price,\
get_yahoo_finance_price_all
from .utils.util import missing_ticker
from .db.db import Db
from .db.mapping import map_index, map_quote, map_fix_quote, map_report
from .db.write import bulk_save, insert_onebyone, writeError, foundDup
from .db.read import read_ticker, has_index, read_exist
from .email.email import sendMail
from .report.report import report
from .simulation.simulator import simulator
from .learning.fetch_aer import fetch_aer
import logging
import logging.config
import getopt
import time
import math
import os, sys
logging.config.fileConfig('stride/log/logging.conf')
logger = logging.getLogger('main')

# If fist time create a new function
# Please use Create_all() tables
def main(argv):
    time_start = time.time()

    try:
        opts, args = getopt.getopt(argv,"u:rsh",["update=", "report=", "simulate="])

    except getopt.GetoptError:
        print('Update: run.py -u <full|compact|fastfix|slowfix> <nasdaq100|tsxci|sp100> (ticker)')
        print('Report: run.py -r <nasdaq100|tsxci|sp100>')
        print('Simulate: run.py -s <nasdaq100|tsxci|sp100>')
        sys.exit(2)

    for opt, arg in opts:

        if opt == '-h':
            print('Update: run.py -u <full|compact|fastfix|slowfix> <nasdaq100|tsxci|sp100> (ticker)')
            print('Report: run.py -r <nasdaq100|tsxci|sp100>')
            print('Simulate: run.py -s <nasdaq100|tsxci|sp100>')
            sys.exit()

        elif (opt == '-u' and len(argv) < 3):
            print('run.py -u <full|compact|fastfix|slowfix> <nasdaq100|tsxci|sp100> (ticker)')
            sys.exit()

        elif opt in ("-u", "--update"):
            if(arg == 'full'):
                index_name = argv[2]
                type = arg
                today_only = False
                update(type, today_only, index_name)  # Full update

            elif(arg == 'compact'):
                index_name = argv[2]
                type = arg
                today_only = True
                update(type, today_only, index_name)  # Compact update for today

            elif(arg == 'slowfix'):
                index_name = argv[2]
                type = 'full' # fixing requires full data
                today_only = False
                update(type, today_only, index_name, fix='slowfix')  # Compact update for today

            elif(arg == 'fastfix'):
                index_name = argv[2]
                type = 'full' # fixing requires full data
                today_only = False
                update(type, today_only, index_name, fix='fastfix', ticker=argv[3])  # Compact update for today

        elif opt in ("-r", "--report"):  # Report
            index_name = argv[1]
            analyze(index_name)

        elif opt in ("-s", "--simulate"): # Simulate
            index_name = argv[1]
            simulate(index_name)

    elapsed = math.ceil((time.time() - time_start)/60)
    logger.info("%s took %d minutes to run" % ( (',').join(argv), elapsed ) )


def update(type, today_only, index_name, fix=False, ticker=None):
    logger.info('Run Task:[%s %s UPDATE]' % (index_name, type))
    Config.DB_NAME=index_name
    db = Db(Config)
    s = db.session()
    e = db.get_engine()
    # Create table based on Models
    # db.create_all()
    if has_index(s) == None:
        # Fetch/Mapping/Write Index
        bulk_save(s, map_index(index_name))
    tickerL = read_ticker(s)

    if (fix == 'slowfix'):
        # tickerL = read_ticker(s)
        tickerL = missing_ticker(index_name)

    elif (fix == 'fastfix'):
        tickerL = [ticker]

    for ticker in tickerL:
    # for ticker in tickerL[tickerL.index('EFN'):]: # Fast fix a ticker
        try:
            if (fix == 'fastfix'): # Fast Update, bulk
                if index_name == 'tsxci':
                    df = get_yahoo_finance_price_all(ticker+'.TO')
                else:
                    df = get_yahoo_finance_price_all(ticker)
                # df = get_daily_adjusted(Config, ticker, type, today_only, index_name)
                model_list = []
                for index, row in df.iterrows():
                    model = map_fix_quote(row, ticker)
                    model_list.append(model)
                logger.info("--> %s" % ticker)
                bulk_save(s, model_list)

            elif (fix == 'slowfix'): # Slow Update, one by one based on log.log
                # df = get_daily_adjusted(Config, ticker, type, today_only, index_name)
                if index_name == 'tsxci':
                    df = get_yahoo_finance_price_all(ticker+'.TO')
                else:
                    df = get_yahoo_finance_price_all(ticker)
                # df = get_daily_adjusted(Config, ticker, type, today_only, index_name)
                model_list = []
                if not df.empty:
                    for index, row in df.iterrows():
                        model = map_fix_quote(row, ticker)
                        model_list.append(model)
                    logger.info("--> %s" % ticker)
                    insert_onebyone(s, model_list)
                else:
                    logger.info("--> (%s, not exist)" % ticker)

            else: # Compact Update
                # 1st fetch by Alphavantage
                df = get_quote_endpoint(Config, ticker, index_name)
                try:
                    model_list = map_quote(df, ticker)
                    bulk_save(s, model_list)
                    logger.info("--> %s" % ticker)
                except:
                    # 2nd try by Yahoo Finance if duplicate
                    if index_name == 'tsxci':
                        df = get_yahoo_finance_price(ticker+'.TO')
                    else:
                        df = get_yahoo_finance_price(ticker)
                    model_list = map_quote(df, ticker)
                    bulk_save(s, model_list)
                    logger.info("2--> %s" % ticker)
        except writeError as e:
            logger.error("%s - (%s,%s)" % (e.value, index_name, ticker))
        except fetchError as e:
            logger.error("%s - (%s,%s)" % (e.value, index_name, ticker))
        except foundDup as e:
            logger.error("%s - (%s,%s)" % (e.value, index_name, ticker))
        except:
            logger.error("Updating failed - (%s,%s)" % (index_name,ticker))

    s.close()


def analyze(index_name):
    logger.info('Run Task: [Reporting]')
    Config.DB_NAME=index_name
    db = Db(Config)
    s = db.session()
    e = db.get_engine()
    # Create table based on Models
    # db.create_all()
    df = report(s)
    model_list = map_report(Config,df)  ####CHECKPOINT
    bulk_save(s, model_list)  ####CHECKPOINT

    s.close()


def simulate(index_name):
    logger.info('Run Task: [Simulation]')
    Config.DB_NAME=index_name
    db = Db(Config)
    s = db.session()
    e = db.get_engine()
    # Create table based on Models
    # db.create_all()
    simulator(s)
    s.close()


# class foundDup(Exception):
#     def __init__(self, value):
#         self.value = value
#     def __str__(self):
#         return repr(self.value)
