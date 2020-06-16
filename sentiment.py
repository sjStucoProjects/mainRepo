from bs4 import BeautifulSoup
#https request engine
from urllib.request import urlopen, Request
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pulldata import getnews
import datetime

finwiz_url = 'https://finviz.com/quote.ashx?t='

def analyze(tickers,yearlimit,monthlimit,daylimit):
    print("starting analysis method")
    debug = True
    all_news = []
    tickerst = []
    pops = []
    reps = []
    scoresdict = {}
    grouped_news = {}
    for ticker in tickers:
        #check to see if any special chars are in the ticker
        if "." in ticker:
            print("Error, found . in ticker name")
        else:
            news = getnews(ticker)
            all_news.append(news)
            if debug:
                print(f"{ticker} news appended to all news \n         Raw headlines: {news}")

        vader = SentimentIntensityAnalyzer()

        # Set column names
        columns = ['ticker', 'date', 'time', 'headline']

        # Convert the parsed_news list into a DataFrame called 'parsed_and_scored_news'
        parsed_and_scored_news = pd.DataFrame(news, columns=columns)

    # Iterate through the headlines and get the polarity scores using vader
        scores = parsed_and_scored_news['headline'].apply(vader.polarity_scores).tolist()
        if debug:
            print(scores)
    # Convert the 'scores' list of dicts into a DataFrame
        scores_df = pd.DataFrame(scores)

    # Join the DataFrames of the news and the list of dicts
        parsed_and_scored_news = parsed_and_scored_news.join(scores_df, rsuffix='_right')

    # Convert the date column from string to datetime
        parsed_and_scored_news['date'] = pd.to_datetime(parsed_and_scored_news.date).dt.date
        parsed_and_scored_news.head()

        #scrub out not-reveant dates
        start_date = pd.to_datetime(f'{monthlimit}/{daylimit}/{yearlimit}')
        filterednews = parsed_and_scored_news.loc[(parsed_and_scored_news['date'] > start_date)]


    return filterednews


