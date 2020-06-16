import robin_stocks as r
import matplotlib.pyplot as plt; plt.rcdefaults()
import datetime
import matplotlib
import matplotlib.ticker as tick
import matplotlib.dates as mdates
import numpy as np
import holidays
from tabulate import tabulate
import statistics
from scipy.stats.mstats import gmean
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import matplotlib.cbook as cbook
from matplotlib.dates import bytespdate2num, num2date
from matplotlib.ticker import Formatter

us_holidays = holidays.UnitedStates()
'''
Robinhood includes dividends as part of your net gain. This script removes
dividends from net gain to figure out how much your stocks/options have paid
off.
Note: load_portfolio_profile() contains some other useful breakdowns of equity.
Print profileData and see what other values you can play around with.
'''

#!!! Fill out username and password
username = 'kpreg'
password = 'Kevin71601'
#!!!

login = r.login(username,password)
hey = r.get_all_watchlists()
print()
print(hey)
stockList = r.build_holdings()
stocksArray = []
stocknumber = 0;

class trajectory:
    #print info to console
    debug = True

    #ideal slope for trajectory calculations

    #compositon of slope score (percentages)

    weekimportance = .1
    monthimportance = .1
    yearimportance = .1
    fiveyearimportance = .1

    #composition of error score importance (higher val = less important)

    weekerrorimportance = .1
    montherrorimportance = .1
    yearerrorimportance = .1
    fiveyearerrorimportance = .1

    #the maximum factor that the error adjusted score can deviate from the actual score by

    errordifference = .05

    #allowed error before confidence penalty (percentages)

    weekallowed = .02
    monthallowed = .05
    yearallowed = .02
    fiveyearallowed = .05

    #stock-specific confidence penalties for trajectory score (inited as zero)

    weekpenalty = 0
    monthpenalty = 0
    yearpenalty = 0
    fiveyearpenalty = 0

    #calculated scores for each slope (inited as zero)

    weekslopescore = 0
    monthslopescore = 0
    yearslopesocre = 0
    fiveyearslopescore = 0

    #error-adjusted scores for each span (inited as zero)

    weekscorefinal = 0
    monthscorefinal = 0
    yearscorefinal = 0
    fiveyearscorefinal = 0

    #the final score!

    finalscore = 0
    finalscoreerror = 0

    #determine if trajectory score is invalid due to excessive error

    invalid = False

    def __init__(self,stock):
        print(f'trajectory object created for {stock.getname()}')
        #grab error and slope trajectories for all possible spans
        self.stock = stock
        self.main = calculateall(stock)
        #check if errors are within threshholds and create penalties as needed
        self.checkerrors()
        #create slope scores
        self.createslopescores()

        self.createfinalscore()

    def createconfidencepenalty(self,input):

        #alter the coefficients of the error generation mechanism. [1,0,0] means x^2 + 0x +0

        coeffieicents = [.02,-3,0]
        confidenceout = float(np.polyval(coeffieicents,input))
        #make sure the value is greater than 1
        if confidenceout<1:
            confidenceout = 1
        if self.debug:
            print(f" error penalty created for {stock.getname()}. Input: {input} Output: {confidenceout}")
        # use the target span input to direct the recaulculated error into the proper error attribute
        return confidenceout

    def checkerrors(self):
        # make sure everything is constructed properly

        if self.debug:
            print(f"Trajectory object created for {self.stock.getname()}")


        #do initial checking to see if errors on all generated lined are within OK amounts specified

        #create some temp values to store error percentages for comparison

        x11 = self.main["weekconfidence"]
        x1 = x11/self.stock.getavgprice("week")
        x22 = self.main["monthconfidence"]
        x2 = x22/self.stock.getavgprice("month")
        x33= self.main["yearconfidence"]
        x3 = x33/self.stock.getavgprice("year")
        x44 = self.main["fiveyearconfidence"]
        x4 = x44/self.stock.getavgprice("fiveyear")
        if self.debug:
            print(f"Avg/max adjusted errors: \n week: {x1} \n month: {x2} \n year: {x3} \n fiveyear: {x4}\n"
                  f'Input errors : \n week: {x11} \n month: {x22} \n year: {x33} \n fiveyear: {x44}"')
        #check the values. b/c the error penalty generator is a squared function, values <1 must be normalized to 1.
        #for example, an 6% error above the a 4% threshhold would have an error penalty created on 2% of it.

        if x1 > self.weekallowed:
            assesspenaltyon = x1 - self.weekallowed
            if self.debug:
                print(f"pre-correction assesspenaltyon for week: {assesspenaltyon}")
            if assesspenaltyon < 1:
                assesspenaltyon = assesspenaltyon + (1.01-assesspenaltyon)
            self.weekpenalty = self.createconfidencepenalty(assesspenaltyon)
            if self.debug:
                print(f'Creating week penalty for {self.stock.getname()} with {assesspenaltyon} as input')
        else:
            self.weekpenalty = 1
        if x2 > self.monthallowed:
            assesspenaltyon = x2 - self.monthallowed
            if assesspenaltyon < 1:
                assesspenaltyon = assesspenaltyon + (1.01-assesspenaltyon)
            self.monthpenalty = self.createconfidencepenalty(assesspenaltyon)
            if self.debug:
                print(f'Creating month penalty for {self.stock.getname()} with {assesspenaltyon} as input')
        else:
            self.monthpenalty = 1
        if x3 > self.yearallowed:
            assesspenaltyon = x3 - self.yearallowed
            if self.debug:
                print("Pre-caulation year assesspenaltyon: " + str(assesspenaltyon))
            if assesspenaltyon < 1:
                assesspenaltyon = assesspenaltyon + (1.01-assesspenaltyon)
            self.yearpenalty = self.createconfidencepenalty(assesspenaltyon)
            if self.debug:
                print(f'Creating year penalty for {self.stock.getname()} with {assesspenaltyon} as input')
        else:
            self.yearpenalty = 1
        if x4 > self.fiveyearallowed:
            assesspenaltyon = x4 - self.fiveyearallowed
            if assesspenaltyon < 1:
                assesspenaltyon = assesspenaltyon + (1.01-assesspenaltyon)
            self.fiveyearpenalty = self.createconfidencepenalty(assesspenaltyon)
            if self.debug:
                print(f'Creating fiveyear penalty for {self.stock.getname()} with {assesspenaltyon} as input. \n Created'
                      f'fiveyear penalty: {self.fiveyearpenalty}')
        else:
            self.fiveyearpenalty = 1
        if self.debug:
            print(self.weekpenalty)
            print(self.monthpenalty)
            print(self.yearpenalty)
            print(self.fiveyearpenalty)

    def createslopescores(self):
        #apply the weightings of each error category and output,defined by a peicewise function.
        #level the playing field by dividing the slope by the maximum price of the stock for better comparison
        spans = ['week','month','year','fiveyear']
        out = []
        for span in spans:
            maxprice = float(self.stock.getavgprice(str(span)))
            keystr = span + "slope"
            slope = float(self.main[keystr])
            output = slope/maxprice
            out.append(output)
            if self.debug:
                print(f'Adjusting {self.stock.getname()}. Max {span} price: {maxprice}. Input slope: {slope}, output slope: {out}')

        self.weekscorefinal = out[0]
        self.monthscorefinal = out[1]
        self.yearscorefinal = out[2]
        self.fiveyearscorefinal = out[3]

    def createfinalscore(self):
        #enhanced local debugging
        localdebug = False

        if localdebug:
            print(type(self.weekscorefinal))
            print(type(self.weekpenalty))
            print(self.weekpenalty)
            print(self.weekpenalty)

        #divide the projections by the prices.
        weektemperror = ((self.weekscorefinal)/self.weekpenalty)*100
        monthtemperror = ((self.monthscorefinal)/self.monthpenalty)*100
        yeartemperror = (self.yearscorefinal/self.yearpenalty)*100
        fiveyeartemperror = (self.fiveyearscorefinal/self.fiveyearpenalty)*100
        self.finalscoreerror = ((weektemperror*self.weekerrorimportance + monthtemperror*self.montherrorimportance + yeartemperror*self.yearerrorimportance + fiveyeartemperror*self.fiveyearerrorimportance))


        weektemp = round((self.weekscorefinal)*100,3)
        monthtemp = round((self.monthscorefinal)*100,3)
        yeartemp = round(self.yearscorefinal*100,3)
        fiveyeartemp = round(self.fiveyearscorefinal*100,3)
        self.finalscore = (weektemp*self.weekimportance + monthtemp*self.monthimportance + yeartemp*self.yearimportance + fiveyeartemp*self.fiveyearimportance)

        #check if all span trajectories are in good parameters, if not, set equal to zero

        if weektemperror < self.errordifference*weektemp:
            #self.errordifference = True
            weektemp = "[Low Confidence]" + str(weektemp)
        if monthtemperror < self.errordifference*monthtemp:
            monthtemp = "[Low Confidence:]" + str(monthtemp)
        if yeartemperror < self.errordifference*yeartemp:
            yeartemp = "[Low Confidence]: " + str(yeartemp)
        if fiveyeartemp < self.errordifference*fiveyeartemp:
            fiveyeartemp = "[Low Confidence]: " + str(fiveyeartemp)

        #print(f'{stock.getname()} trajectory score was unable to be calculated due to extreme error. \n Final Error Adjusted Score: {finalscoreerror} \n Final Score:: {self.finalscore}')
        print(tabulate([["Final Score: ", str(self.finalscore)], ["Week Score:", str(weektemp)], ["Month Score: ", str(monthtemp)],["Year Score: ", str(yeartemp)],["Five Year Score: ", str(fiveyeartemp)],["Error Score: ",str(self.finalscoreerror)]], [self.stock.getname() + " Info", "Value"], tablefmt="grid"))
        #print(f"Final score for {stock.getname()}: {self.finalscore*100}. \n Week score: {weektemp*.3} \n Month score: {monthtemp*.2} \n Year score: {yeartemp*.1} \n Five year score: {fiveyeartemp*.1} \n Error score: {finalscoreerror}")

    def getfinalscore(self):
        return self.finalscore
    def getfinalerrorscore(self):
        return self.finalscoreerror
class stockcontainer:
    stockdata = {}
    ticker = ""
    quantity = 0;
    graphit = True
    debug = True

    #some class attributes i didnt know what else to do with

    weekerrormax = 0
    montherrormax = 0
    yearerrormax = 0
    fiveyearerrormax = 0

    def __init__(self, stockname, stockDataDict, earnings, weekraw,monthraw,yearraw,fiveyearraw):

        # init data

        self.ticker = stockname
        self.stockdata = stockDataDict
        self.weekraw = weekraw
        self.monthraw = monthraw
        self.yearraw = yearraw
        self.fiveyearraw = fiveyearraw
        self.weekinterval = 0
        self.monthinterval = 0
        self.yearinterval = 0
        self.fiveyearinterval = 0

    def getprice(self):
        price = self.stockdata["price"]
        return price

    def getname(self):
        name = self.stockdata["name"]
        return name

    def getquantity(self):
        return(self.stockdata["quantity"])

    def getequity(self):
        return(self.stockdata["equity"])

    def calculatedates(self,span):
        timestamps = []
        dates = 0
        if span == "week":
            for data in self.weekraw:
                timestamps.append(data["begins_at"])
                dates = dates + 1
            zeroone = np.linspace(0,1, len(timestamps))
            self.weekinterval = (zeroone[1]-zeroone[0])
            return zeroone
        if span == "month":
            for data in self.monthraw:
                timestamps.append(data["begins_at"])
                dates = dates + 1
            zeroone = np.linspace(0, 1, len(timestamps))
            self.monthinterval = (zeroone[1] - zeroone[0])
            return zeroone
        if span == "year":
            for data in self.yearraw:
                timestamps.append(data["begins_at"])
                dates = dates + 1
            zeroone = np.linspace(0, 1, len(timestamps))
            self.yearinterval = (zeroone[1] - zeroone[0])
            return zeroone
        if span == "fiveyear":
            for data in self.fiveyearraw:
                timestamps.append(data["begins_at"])
                dates = dates + 1
            zeroone = np.linspace(0, 1, len(timestamps))
            self.fiveyearinterval = (zeroone[1] - zeroone[0])
            return zeroone

    def calculateprices(self,span):
        prices = []
        if span =="week":
            for data in self.weekraw:
                price = data["close_price"]
                prices.append(price)
        if span =="month":
            for data in self.monthraw:
                price = round(float(data["close_price"]), 3)
                prices.append(price)
        if span =="year":
            for data in self.yearraw:
                price = round(float(data["close_price"]), 3)
                prices.append(price)
        if span =="fiveyear":
            for data in self.fiveyearraw:
                price = round(float(data["close_price"]), 3)
                prices.append(price)
        return prices
    def generateline(self,x,y,precision,prediction,predictionunit,span):
        #figure out the interval, so we can predict future intervals

        interval = 0

        if span == "week":
            #for week span - intervals are in 10 minutes
            if predictionunit == "10min":
                interval = self.weekinterval
            if predictionunit == "hours":
                interval = (self.weekinterval)*6
            if predictionunit == "days":
                interval = (self.weekinterval)*42
        if span == "month":
            #for month span - intervals are in hours
            if predictionunit == "hours":
                interval = self.monthinterval
            if predictionunit == "days":
                interval = (self.monthinterval) * 7
            if predictionunit == "weeks":
                interval = (self.monthinterval) * 35
        if span == "year":
            #for year span - intervals are in days
            interval = self.yearinterval
        if span == "5year":
            interval = self.fiveyearinterval

        #convert given array of intervals to a numpi array, and add new intervals based on the relative number of the
        #prediction parameter.

        x = np.asarray(x, dtype='float64')
        if prediction != 0:
            i = 1
            while i > (prediction+2):
                temp = x[len(x)-1]+(interval*i)
                x.append(temp)
        y = np.asarray(y, dtype="float64")
        warn = False
        p, cov = np.polyfit(x,y,precision,cov = True)

        plt.plot(x, y)

        #start calculating error by evaluating the best fit line at every date and comparing w/ actual value
        index = 0
        errors = []
        for point in y:
            prediction = (np.polyval(p,x[index]))
            actual = (point)
            error = abs(actual-prediction)
            errors.append(error)
            index = index + 1
        maxerror = max(errors)
        medianerror = statistics.median(errors)
        gmeanerror = gmean(errors)
        errorsum = 0
        for error in errors:
            errorsum = errorsum + error
        avgerror = errorsum/len(errors)
        allowederror = .05
        calculatedxmaxerror = allowederror*avgerror
        #add a warning if the maximum error exceeds 4%
        if maxerror > calculatedxmaxerror:
            warn = True
        confidence = round((avgerror / calculatedxmaxerror),3)
        confidencepercent = avgerror
        if self.debug:
            print(f"Average error for {self.ticker} for span {span}: ${avgerror}")


        if warn:
            plt.title(f'-----Prediction for {self.ticker}----- \n Warning - average deviation of ${round(confidencepercent,3)}%')
        else:
            plt.title(f'Prediction for {self.ticker}')

        #construct the matplotlib graph
        plt.xlabel(f'Elapsed Time [{span}]')
        plt.ylabel('Price')
        plt.plot(x, np.polyval(p, x))
        plt.plot(x,(np.polyval(p,x)+ maxerror))
        plt.plot(x, (np.polyval(p, x) - maxerror))
        if self.graphit:
            plt.show()

        #put all important values in a dictionary

        #store maximum deviations as class atrributes
        if span == "week":
            self.weekerrormax = maxerror
        if span == "month":
            self.montherrormax = maxerror
        if span == "year":
            self.yearerrormax = maxerror
        if span == "fiveyear":
            self.fiveyearerrormax = maxerror


        toreturn = {}
        toreturn["slope"] = p[0]
        toreturn["confidence"] = gmeanerror
        return toreturn

    def getavgprice(self,span):
        x = self.calculateprices(span)
        new = []
        for y in x:
            new.append(float(y))
        return gmean(new)

    def getmaxprice(self,span):
        x = self.calculateprices(span)
        return max(x)
    def generatevol(self):
        return
    def addtrajectory(self,trajectoryin):
        self.trajectorymaster = trajectoryin
    def gettrajectoryfinalscore(self):
        return self.trajectorymaster.getfinalscore()
    def gettrajectoryerror(self):
        return self.trajectorymaster.getfinalerrorscore()
def calculateall(stockobject):
    # return a dictionary with calculated trajectory and error data for all possible spans
    values = {}

    x1 = stockobject.calculatedates("week")
    y1 = stockobject.calculateprices("week")
    temp = stockobject.generateline(x1,y1,1,0,"none","week")
    weekslope = temp["slope"]
    weekconfidence = temp["confidence"]
    values["weekslope"] = weekslope
    values["weekconfidence"] = weekconfidence

    x2 = stockobject.calculatedates("month")
    y2 = stockobject.calculateprices("month")
    temp = stockobject.generateline(x2,y2,1,0,"none","month")
    monthslope = temp["slope"]
    monthconfidence = temp["confidence"]
    values["monthslope"] = monthslope
    values["monthconfidence"] = monthconfidence

    x3 = stockobject.calculatedates("year")
    y3 = stockobject.calculateprices("year")
    temp = stockobject.generateline(x3, y3, 1, 0, "none", "year")
    yearslope = temp["slope"]
    yearconfidence = temp["confidence"]
    values["yearslope"] = yearslope
    values["yearconfidence"] = yearconfidence

    x4 = stockobject.calculatedates("fiveyear")
    y4 = stockobject.calculateprices("fiveyear")
    temp = stockobject.generateline(x4, y4, 1, 0, "none", "fiveyear")
    fiveyearslope = temp["slope"]
    fiveyearconfidence = temp["confidence"]
    values["fiveyearslope"] = fiveyearslope
    values["fiveyearconfidence"] = fiveyearconfidence

    return values

def comparetrajectories(stockArray):
    debug = True
    scores = []
    stocks = []
    errors = []
    for stock in stockArray:
        y = round(stock.gettrajectoryfinalscore(),2)
        scores.append(y)
        z = round(stock.gettrajectoryerror(),2)
        errors.append(z)
        za = stock.ticker
        stocks.append(za)
        if debug:
            print(f'Stock Name: {za} \n trajectory score: {y} error score: {z} \n ------')
    #create the bar graph
    shift = 0
    width = .1
    if debug:
        print("creating plot")
    index = stocks
    if debug:
        print("index has arranged the stocks")
    if debug:
        print("score array: " + str(scores))

    plt.clf()
    labels = stocks
    men_means = scores
    women_means = errors

    x = np.arange(len(labels))  # the label locations
    width = 0.4  # the width of the bars
    fig, ax = plt.subplots(figsize=(15,10))
    rects1 = ax.bar(x - width / 2, men_means, width, label='Trajectory Score (Higher is better)')
    rects2 = ax.bar(x + width / 2, women_means, width, label='Confidence Score (Higher is better)')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Scores')
    ax.set_title(f'---Trajectory and Error Score Comparisons----- \n \n Score Weights - Week: {stock.trajectorymaster.weekimportance*100}%  | '
                 f'Month: {stock.trajectorymaster.monthimportance*100}% | Year: {stock.trajectorymaster.yearimportance*100}% | '
                 f'Fiveyear: {stock.trajectorymaster.fiveyearimportance*100}% \n  Error weights - Week: {stock.trajectorymaster.weekerrorimportance*100}% | '
                 f' Month: {stock.trajectorymaster.montherrorimportance*100}% | Year: {stock.trajectorymaster.yearerrorimportance*100}% |'
                 f' Fiveyear: {stock.trajectorymaster.fiveyearerrorimportance*100}')


    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    for rect in rects1:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
    for rect in rects2:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
    fig.tight_layout()
    plt.show()

print("constructing stock objects")
stocknumber = 0

watchlist = ["VOO", "MSFT","XOP", "INTC","QQQ","RMD"]
def getstockinfo(watchlistname):
    # fetch data from robinhood and parse data into a dictionary structure that stockcontainer can accept
    for stock in watchlist:
        week = r.get_historicals(stock, span ='week',bounds = "regular")
        month = r.get_historicals(stock, span = 'month', bounds = "regular")
        year = r.get_historicals(stock, span = 'year', bounds = "regular")
        fiveyear = r.get_historicals(stock, span = '5year', bounds = "regular")
        data = {}
        data['name'] = str(stock)
        data['price'] = "Stock created using secondary method - price not supported"
        data['earnings'] = r.get_earnings(stock)
        data['events'] = r.get_events(stock)
        data['fundamentals'] = r.get_fundamentals(stock)
        x = stockcontainer(stock,data,"fuck off",week,month,year,fiveyear)
        traj = trajectory(x)
        x.addtrajectory(traj)
        stocksArray.append(x)
addmystocks = True
blacklist = []
for key,value in stockList.items():
    if addmystocks:
        if key not in blacklist:
            earnings = r.get_earnings(key)
            weekraw = r.get_historicals(key,span='week',bounds="regular")
            monthraw = r.get_historicals(key, span='month',bounds="regular")
            yearraw = r.get_historicals(key,span="year",bounds="regular")
            fiveyearraw = r.get_historicals(key,span="5year",bounds="regular")
            stocksArray.append((stockcontainer(key,value,earnings,weekraw,monthraw,yearraw,fiveyearraw)))
            stocknumber = stocknumber + 1;
        else:
            print(f'{key} excluded from calculations')

if addmystocks:
    for stock in stocksArray:
        trajectoryinfo = trajectory(stock)
        stock.addtrajectory(trajectoryinfo)
getstockinfo(watchlist)
comparetrajectories(stocksArray)








