# -*- coding: utf-8 -*-

from .db.db import Db as db


class Index(db.Model):
    __tablename__ = 'index'
    symbol = db.Column(db.String(6), unique=True, nullable=False, primary_key=True)
    company = db.Column(db.String(60),nullable=False)
    # sector = db.Column(db.String(80),nullable=False)
    # industry = db.Column(db.String(60),nullable=False)
    quote = db.relationship('Quote', backref='quote', lazy=True)
    report = db.relationship('Report', backref='report', lazy=True)


class Quote(db.Model):
    __tablename__ = 'quote'
    id = db.Column(db.String(40), unique=True, nullable=False, primary_key=True)
    symbol = db.Column(db.String(6), db.ForeignKey("index.symbol"), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    open = db.Column(db.Float, nullable=True)
    high = db.Column(db.Float, nullable=True)
    low = db.Column(db.Float, nullable=True)
    close = db.Column(db.Float, nullable=True)
    adjusted = db.Column(db.Float, nullable=True)
    volume = db.Column(db.BIGINT, nullable=True)


class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.String(40), unique=True, nullable=False, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    symbol = db.Column(db.String(6), db.ForeignKey("index.symbol"), nullable=False)
    yr_high = db.Column(db.Boolean, nullable=True)
    yr_low = db.Column(db.Boolean, nullable=True)
    downtrend = db.Column(db.Boolean, nullable=True)
    uptrend = db.Column(db.Boolean, nullable=True)
    high_volume = db.Column(db.Boolean, nullable=True)
    # low_volume = db.Column(db.Boolean, nullable=True)
    # support = db.Column(db.Boolean, nullable=True)
    # pattern = db.Column(db.String(20), nullable=True)
    # volume_price = db.Column(db.Boolean, nullable=True)
    rsi = db.Column(db.String(4), nullable=True)
    macd = db.Column(db.String(4), nullable=True)
    bolling = db.Column(db.String(10), nullable=True)
    # adx = db.Column(db.String(4), nullable=True)


class Holding(db.Model):
    __tablename__ = 'holding'
    symbol = db.Column(db.String(6), db.ForeignKey("index.symbol"), primary_key=True, nullable=False)
    avg_cost = db.Column(db.Float, nullable=True)
    book_value = db.Column(db.Float, nullable=True)
    change_dollar = db.Column(db.Float, nullable=True)
    change_percent = db.Column(db.Float, nullable=True)
    mkt_price = db.Column(db.Float, nullable=True)
    mkt_value = db.Column(db.Float, nullable=True)
    quantity = db.Column(db.BIGINT, nullable=True)
    note = db.Column(db.String(20), nullable=True)


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.String(40), unique=True, nullable=False, primary_key=True)
    symbol = db.Column(db.String(6), db.ForeignKey("index.symbol"), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=True)
    quantity = db.Column(db.BIGINT, nullable=True)
    settlement = db.Column(db.Float, nullable=True)
    type = db.Column(db.String(6), nullable=False)

# Well Licences Issued
class St1(db.Model):
    __tablename__ = 'st1'
    date = db.Column(db.DateTime, unique=True, nullable=False, primary_key=True)
    gas = db.Column(db.Integer, nullable=True)
    oil = db.Column(db.Integer, nullable=True)
    bitumen = db.Column(db.Integer, nullable=True)


# DAILY DRILLING ACTIVITY LIST
class St49(db.Model):
    __tablename__ = 'st49'
    date = db.Column(db.DateTime, unique=True, nullable=False, primary_key=True)
    total = db.Column(db.Integer, nullable=True)
    drill_to_ld = db.Column(db.Integer, nullable=True)
    re_entry = db.Column(db.Integer, nullable=True)
    resumption = db.Column(db.Integer, nullable=True)
    set_surface = db.Column(db.Integer, nullable=True)


# Facility Approval Disposition Daily Report
class St97(db.Model):
    __tablename__ = 'st97'
    id = db.Column(db.String(40), unique=True, nullable=False, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    licensee = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(30), nullable=False)


# Pipeline Construction Notification List
class St100(db.Model):
    __tablename__ = 'st100'
    date = db.Column(db.DateTime, unique=True, nullable=False, primary_key=True)
    total = db.Column(db.Integer, nullable=True)
