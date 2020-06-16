import requests
from bs4 import BeautifulSoup
#https request engine
from urllib.request import urlopen, Request
from datetime import datetime
from alpha_vantage.timeseries import TimeSeries
import random

import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import time
def harvest():
    debug = True
    print("overallnews init")
    news_tables = {}
    url = "https://seekingalpha.com/market-news"
    pages = []
    keepgoing = True
    file = open("../from laptop/scrape.txt", "a")
    maxpages = 5
    currentpage = 0
    while currentpage < maxpages:
        urltemp = f'{url}/{currentpage}'
        print(f'connecting to url {urltemp}')
        hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
        req = (requests.get(url=url, proxies = {'http':'50.207.31.221:80'})).text
        html = BeautifulSoup(req, 'html.parser')
        pages.append(html)
        currentpage = currentpage + 1
        file.write(f'[[START]]{html}[[END]] \n \n \n \n')
        print(file)
        delay = random.randint(0,100)/125
        print(f"waiting {delay} seconds before next connection")
        time.sleep(delay)

        for newspiece in html.find_all('li', class_ = "item"):
            


        for item in refine2:
            date = 0
            temp = item.find("h4")
            temp2 = temp.find("a")
            headline = temp2.contents[0]
            print(f'headline: {headline}')

            #file.write(f'[[START]]{entry}[[END]] \n \n \n \n')
