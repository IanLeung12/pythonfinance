import bs4 as bs
import pickle
import requests
import os
import pandas as pd
import yfinance as web
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import mplfinance as mpf
import matplotlib

style.use("ggplot")

def save_sp500_tickers():
    #beatufiul sup
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text,'html.parser')
    table = soup.find('table', {'class':'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:  # Skip the header row
        # Find all <td> elements (table columns)
        columns = row.findAll('td')


        # Check if the row has at least one <td> element
        if len(columns) > 0:
            ticker = columns[1].text.strip() # Get the ticker symbol, remove extra spaces
            tickers.append(ticker)

    with open("sp500tickers.pickle", "wb") as file:
        pickle.dump(tickers, file)

    print(tickers)

    return tickers

def get_data_from_yahoo(reload_sp500=False):
    if reload_sp500:
        tickers = save_sp500_tickers()
    else:
        with open("sp500tickers.pickle", "rb") as file:
            tickers = pickle.load(file)

    tickers = [ticker for ticker in tickers if ticker.strip()]

    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')

    start = dt.datetime(2000,1,1)
    end = dt.datetime(2024,12,31)

    for ticker in tickers:
        if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
            df = web.download(ticker,start,end)
            df.to_csv('stock_dfs/{}.csv'.format(ticker))
        else:
            print('Already have {}'.format(ticker))

def compile_data():
    with open('sp500tickers.pickle', 'rb') as file:
        tickers = pickle.load(file)

    tickers = [ticker for ticker in tickers if ticker.strip()]
    main_df = pd.DataFrame()

    for count,ticker in enumerate(tickers):
        df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
        df.drop(index={0,1}, inplace=True)
        df.rename(columns={"Price":"Date"}, inplace=True)
        df.set_index('Date', inplace=True, drop=False)
        df = df[['Adj Close']].copy()
        df.rename(columns = {'Adj Close': ticker}, inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df = pd.merge(main_df, df, on='Date', how='outer')

        if count % 10 == 0:
            print(count , '/' , str(len(tickers)))

    main_df.to_csv('sp500_joined_closes.csv')

def graph_data():
    df = pd.read_csv('sp500_joined_closes.csv')
    print(df.tail())
    for ticker in df.columns:
        if ticker != 'Date':
            df[ticker].plot(x='Date', y=ticker, label=ticker, title='Adjusted Closes of the S&P 500')

    plt.show()

def graph_corr():
    df = pd.read_csv('sp500_joined_closes.csv')
    df = df.iloc[:, 1:]
    df_corr = df.corr()
    df_corr = df.dropna(axis=1, how='all').corr()
    data = df_corr.values
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn)
    fig.colorbar(heatmap)
    ax.set_xticks(np.arange(data.shape[0]) + 0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[1]) + 0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    column_labels = df_corr.columns
    row_labels = df_corr.index
    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap.set_clim(-1,1)
    plt.tight_layout()
    plt.show()


#graph_data()
graph_corr()
#compile_data()
print("Done")
#get_data_from_yahoo()
#save_sp500_tickers()