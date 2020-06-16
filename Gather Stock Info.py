import robin_stocks as r
from sentiment import analyze
from pulldata import gethighest
from pulldata import getoverallnews
from harvest import harvest
debug = True

#connect to robinhood, access tickers
username = 'kpreg'
password = 'Kevin71601'
login = r.login(username,password)
temp = r.build_holdings()
tickersHeld = []
for key in temp:
    tickersHeld.append(key)
    if debug:
        print(f'Appending {key} to tickers held')
print("starting overallnews")
#hey = getoverallnews(5,10,10)
#week = analyze(tickersHeld,2020,5,1)
print("finished")
#print(week["highestpop"])
harvest()


