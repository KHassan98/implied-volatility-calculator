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
import math

def phi(x):
    # Cumulative normal distribution function
    return (1 + math.erf(x/math.sqrt(2)))/2

assert(phi(0) == 0.5 and 0.84 < phi(1) < 0.85)

def norm(x):
    return math.exp(-(x**2)/2)/math.sqrt(2*math.pi)

assert(0.39 < norm(0) < 0.40)

def BlackScholes(t,S_t,K,r,sigma):
    # Black Scholes for a Call Option, variable names as in formula (t is time to expiry in years)
    d_1 = (t*(r + (sigma**2)/2) + math.log(S_t/K))/(sigma*math.sqrt(t))
    d_2 = d_1 - sigma*math.sqrt(t)
    P_v = K*math.exp(-r*t)

    return phi(d_1)*S_t - phi(d_2)*P_v

assert(0.99 < BlackScholes(0.0822,100,100,0.05,0.0681) < 1.01)

def vega(t,S_t,K,r,sigma):
    d_1 = (t*(r + (sigma**2)/2) + math.log(S_t/K))/(sigma*math.sqrt(t))

    return S_t*math.sqrt(t)*norm(d_1)

assert(11.1 < vega(0.0822,100,100,0.05,0.0681) < 11.2)

def newtonraphson(t,S_t,K,r,m,tol,max_iters):
    # iteratively solve for sigma
    # m is call price, tol is tolerance for difference between iterations
    # max_iters is maximum number of iterations
    sigma = 0
    sigma_ = 0.1 # initial guess
    c = 0
    while abs(sigma_ - sigma) > tol:
        c += 1
        sigma = sigma_
        sigma_ = sigma_ - (BlackScholes(t,S_t,K,r,sigma_) - m)/vega(t,S_t,K,r,sigma_)
        if c > max_iters:
            return float('nan')

    return sigma_

assert(0.0681 < newtonraphson(0.0822,100,100,0.05,1,10**(-8),100) < 0.0682)

def gamma(x):
    return phi(x) + norm(x)/x

def Bachelier(t,S_t,K,r,m, option_type):
    # Calculate Bachelier volatility from market price
    # Calculations from https://jaeckel.000webhostapp.com/ImpliedNormalVolatility.pdf

    D = math.exp(r*t)
    F = S_t/D
    if option_type == 'Call':
        theta = 1
    elif option_type == 'Put':
        theta = -1

    if F >= K:
        gamma_star = -abs(m - (theta*(F-K)))/abs(K-F)
    else:
        gamma_star = -abs(m)/abs(K-F)
    if gamma_star < gamma(-9/4):
        g = 1/(gamma_star - 1/2)
        e_ = (0.032114372355 - (g**2)*(0.016969777977 - (g**2)*(2.6207332461*10**(-3) - (g**2)*(9.606695286*10**(-5)))))
        e_ = e_/(1 - (g**2)*(0.6635646938 - (g**2)*(0.14528712196 - (g**2)*(0.010472855461))))
        x_ = g*(norm(0) + e_*(g**2))
    else:
        h = math.sqrt(-math.log(-gamma_star))
        x_ = 9.4883409779 - h*(9.6320903635 - h*(0.58556997323 + 2.1464093351*h))
        x_ = x_/(1- h*(0.65174820867 + h*(1.5120247828 + h*6.6437847132*10**(-5))))

    q = (gamma(x_) - gamma_star)/norm(x_)

    x_star = x_ + ((3*q*(x_**2))*(2 - q*x_*(2 + (x_)**2)))/(6 + q*x_*(-12 + x_*(6*q + x_*(-6 + q*x_*(3 + (x_)**2)))))

    return abs(K-F)/abs(x_star*math.sqrt(t))


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
        self.years_to_expiry = days_to_expiry/365 # float ACT/365 convention

    def spot(self):
        'Calculates spot price and sets it as the spot property of the option'
        if self.underlying_type == 'Future':
            r = self.risk_free_rate
            t = self.days_to_expiry/365
            self.spot = (self.underlying)*math.exp(-r*t)
        elif self.underlying_type == 'Stock':
            self.spot = self.underlying


    def implied_volatility(self):
        'Calculates implied volatility and sets it as the implied_volatility property of the option'
        self.spot()
        if self.model_type == 'BlackScholes':
            if self.option_type == 'Call':
                self.implied_volatility = newtonraphson(self.years_to_expiry,self.spot,self.strike,self.risk_free_rate,self.market_price,10**(-8),100)
            elif self.option_type == 'Put':
                discount = math.exp(self.risk_free_rate*self.years_to_expiry)
                c = self.market_price + self.spot - discount*self.strike # put-call parity
                self.implied_volatility = newtonraphson(self.years_to_expiry,self.spot,self.strike,self.risk_free_rate,c,10**(-8),100)

        if self.model_type == 'Bachelier':
            self.implied_volatility = Bachelier(self.years_to_expiry,self.spot,self.strike,self.risk_free_rate,self.market_price,self.option_type)

        return self.implied_volatility




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
        vols = open(path_to_output,'w',newline='')
        write_vols = csv.writer(vols)
        write_vols.writerow(['ID','Spot','Strike','Risk-Free Rate','Years To Expiry','Option Type','Model Type','Implied Volatility','Market Price'])
        for i in range(len(self.options)):
            option = self.options[i]
            try:
                option.implied_volatility()
            except:
                continue
            write_vols.writerow([i,option.spot,option.strike,option.risk_free_rate,option.years_to_expiry,option.option_type,option.model_type,option.implied_volatility,option.market_price])


# Replace with own input/output csvs as necessary
trades = Trades("C:\\Users\\Khalid Hassan\\Downloads\\MakoInterviewPackIV\\input.csv")
trades.write_output("C:\\Users\\Khalid Hassan\\Downloads\\MakoInterviewPackIV\\output.csv")
