from bs4 import BeautifulSoup
#https request engine
from urllib.request import urlopen, Request
from datetime import datetime
from alpha_vantage.timeseries import TimeSeries

import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import time

finwiz_url = 'https://finviz.com/quote.ashx?t='
alphakey = "PUEYGLK953RE2EB1"
def getnews(ticker):
    debug = True
    if "." in ticker:
        print("not gathing news, found bad char")
        return
    news_tables = {}
    url = finwiz_url + ticker
    req = Request(url=url, headers={'user-agent': 'my-app/0.0.1'})
    response = urlopen(req)
    html = BeautifulSoup(response)
    news_table = html.find(id='news-table')
    news_tables[ticker] = news_table

    parsed_news = []
    for file_name, news_table in news_tables.items():
        # Iterate through all tr tags in 'news_table'
        for x in news_table.findAll('tr'):
            # read the text from each tr tag into text
            # get text from a only
            text = x.a.get_text()
            # splite text in the td tag into a list
            date_scrape = x.td.text.split()
            # if the length of 'date_scrape' is 1, load 'time' as the only element
            if len(date_scrape) == 1:
                time = date_scrape[0]
            # else load 'date' as the 1st element and 'time' as the second
            else:
                date = date_scrape[0]
                time = date_scrape[1]
            # Extract the ticker from the file name, get the string up to the 1st '_'
            ticker = file_name.split('_')[0]

            parsed_news.append([ticker, date, time, text])
    if debug:
        print(f'Pulldata output for {ticker}: {parsed_news}')

    return parsed_news

def getoverallnews(day,month,year):
    debug = True
    print("overallnews init")
    news_tables = {}
    url = "https://seekingalpha.com/market-news"
    pages = []
    keepgoing = True
    maxpages = 1
    currentpage = 0
    while currentpage<maxpages:
        urltemp = f'{url}/{currentpage}'
        print(f'connecting to url {urltemp}')
        req = Request(url=url, headers={'user-agent': 'my-app/0.0.1'})
        response = urlopen(req)
        html = BeautifulSoup(response)
        pages.append(html)
        currentpage = currentpage+1
        print(html)

    parsed_news = []
    print("processing raw HTMLs")
    for page in pages:
        items = page.findAll("li", {"class": "item"})
        items2 = {}
        for item in items:
            temp = item.findAll("a",{"class":"add-source-assigned"})
            headlines = []
            print(f"temp: {temp} type: {temp.type()}")
            temp2 = item.findAll("span",{"class":"item-date"})
            print(f"temp2: {temp2}")
            entry = {temp:temp2}
            items2.update(entry)
        print(items2)
        date = page.findAll("li", {"class": "date-changed"})
        print(date)


    return parsed_news


def gethighest(analyis):
    highestpop = 0
    highestpopt = ""
    highestrep = 0
    highestrept = ""
    returnval = {}
    for key,value in analyis:
        if value["reputation"] > highestrep:
            highestrep = value[0]
            highestrept = key
        if value["popularity"] > highestpop:
            highestpop = value[1]
            highestpopt = key
    returnval["highestpop"] = highestpopt
    returnval['highestrep'] = highestrept
    return returnval

def getpriceondate(pddatetime,ticker):
    debug = True

