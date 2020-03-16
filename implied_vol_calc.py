#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Khalid Hassan
#
# Created:     16/03/2020
# Copyright:   (c) Khalid Hassan 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import csv

class Option:

    def __init__(self, underlying_type, underlying, risk_free_rate, days_to_expiry, strike, option_type, model_type, market_price):
        self.underlying_type = underlying_type # str -> 'Stock' or 'Future'
        self.underlying = underlying # float
        self.risk_free_rate = risk_free_rate # float
        self.days_to_expiry = days_to_expiry # float
        self.strike = strike # float
        self.option_type = option_type # str -> 'Call' or 'Put'
        self.model_type = model_type # str -> 'BlackScholes' or 'Bachelier'
        self.market_price = market_price # float

    def spot(self):
        'Calculates spot price and sets it as the spot property of the option'


    def calc_implied_vol(self):
        'Calculates implied vol and sets it as the implied_volatility property of the option'

class Trades:

    def __init__(self, path_to_input):
        options = []
        trades = open(path_to_input)
        read_trades = csv.reader(trades)
        next(read_trades) # skip first row of csv
        for row in read_trades:
            options.append(Option(row[1],float(row[2]),float(row[3]),float(row[4]),float(row[5]),row[6],row[7],float(row[8])))

        self.options = options

    def write_output(self, path_to_output):
        'Writes output csv to the given path'


