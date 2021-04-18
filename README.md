# Stride

Stride is a python script to fetch quotes (TSXCI, NASDAQ100 and SP100) from ALPHA VANTAGE (https://www.alphavantage.co/) and to write quotes to local database. Also it makes analysis reports that mark down important market signals and saves into tables. Lastly it simulates trading based on these signals.

## Getting Started

Python3.5 or higher version and Pandas, Numpy, SQLAlchemy and ect.
A loca/remote Mysql is required and db "tsxci", "nasdaq100" and "sp100" are created.
Environment varibles to enter in OS:
```
DB_USER="DB_USER"
DB_PASS="DB_PASSWORD"
DB_HOST="localhost"
DB_PORT="3306"
EMAIL_USER="SENDER_GMAIL"
EMAIL_PASS="SENDER_GMAIL_PWD"
EMAIL_TO="MYDOG@GMAIL.COM,MYCAT@GMAIL.COM"
AV_KEY="ALPHAVANTAGE_KEY"
```

### Prerequisites

What things you need to install the software and how to install them

```
python3.5+
pandas
urllib3==1.22
alpha_vantage==2.3.1
certifi==2020.4.5.1
stockstats==0.3.0
numpy==1.16.0
requests==2.18.4
SQLAlchemy==1.2.7
beautifulsoup4==4.9.1
python_dateutil==2.8.1
PyYAML==5.3.1
lxml==4.5.2
mysqlclient==2.0.1
asyncio==3.4.3


```


### Usage

Update quotes

```
Update: run.py -u <full|compact|fastfix|slowfix> <nasdaq100|tsxci|sp100> (ticker)
Report: run.py -r <nasdaq100|tsxci|sp100>
Simulate: run.py -s <nasdaq100|tsxci|sp100>
```



Reporting
```
run.py -r <nasdaq100|tsxci|sp100>
```

Simulate Trading
```
run.py -s <nasdaq100|tsxci|sp100>
```


## Authors

* **Colin Zhong** - *Initial work* - [Git Page](https://github.com/chzhong25346)
