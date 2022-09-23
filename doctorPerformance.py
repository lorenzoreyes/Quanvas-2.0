# We want to iterate excels, perform a task and save changes
# designed in TrackUpdate.py Grab an input int 
# of excel to perform task (monitor, update, withdraw, etc)
# from the command line.

import pandas as pd, numpy as np, glob
import yfinance as yahoo, datetime as dt
import trackCLI as tracker
import os, shutil
import matplotlib.pyplot as plt

pd.options.display.float_format = '{:,.2f}'.format

# 1. Want to generate a dictionary key:val ID:name to pick file
# As this every time re run the code the list is updated
def print_database():
    file = []
    clientDict = {}

    for filename in glob.iglob('./DATABASE/*'):
      file.append(filename)
      clientDict = dict(map(reversed, enumerate(file)))  
      clientDict = dict((v,k) for k,v in clientDict.items())

    clientDict = pd.DataFrame(clientDict.items(), columns=['IDs','Path'])
    clientDict = clientDict.sort_values('Path',axis=0,ascending=True)
    clientDict['IDs'] = range(len(clientDict))
    clientDict.index = range(len(clientDict))
    return clientDict


# 2. Choose excel to work with and operation what operation to do
def portfolio_name():
    database = (print_database())
    database = database.Path.to_list()
    name = input("\nWhat client Name do you want? ")
    client = (list(filter(lambda x: (name in x),database)))
    client = pd.DataFrame(client, columns=[f'{name} Portfolios'],index=range(len(client)))
    print(client)
    order = input("\nType [N]umber for a portfolio, else to do something else \n\n")
    try:
        order = int(order)
        data = pd.read_excel(client[f'{name} Portfolios'][order])
        path = str(client[f'{name} Portfolios'][order])
    except:
        print(f"input {order} is not valid. Type an integer")
        portfolio_operation()
    
    return path
    
def to_plot():
    df = portfolio_name()
    name = str(df)
    df = pd.read_excel(df,sheet_name='portfolioWeights')
    stocks = df.iloc[:,0].to_list()
    date = name.split(' ')[-1].split('.')[0]
    print(date)
    info = yahoo.download(stocks,date,interval="60m")['Adj Close'].fillna(method='ffill')
    performance = pd.DataFrame((info * df['SharpeRatio'].values).T.sum(),columns=['SharpeRatio'],index=info.index)
    performance['MinVaR'] = (info * df['MinVaR'].values).T.sum()
    performance['SharpeUnbound'] = (info * df['SharpeUnbound'].values).T.sum()
    performance['SortinoRatio'] = (info * df['SortinoRatio'].values).T.sum()
    performance['Benchmark'] = (info * (1/len(df.columns))).T.sum()
    performance = performance.rename(columns={'MinVaR':f'MinVaR {round(performance.MinVaR.pct_change().sum() * 100,2)}%'})
    performance = performance.rename(columns={'SharpeRatio':f'SharpeRatio {round(performance.SharpeRatio.pct_change().sum() * 100,2)}%'})
    performance = performance.rename(columns={'SharpeUnbound':f'SharpeUnbound {round(performance.SharpeUnbound.pct_change().sum() * 100,2)}%'})
    performance = performance.rename(columns={'SortinoRatio':f'SortinoRatio {round(performance.SortinoRatio.pct_change().sum() * 100,2)}%'})
    performance = performance.rename(columns={'Benchmark':f'Benchmark {round(performance.Benchmark.pct_change().sum() * 100,2)}%'})
    fig = plt.figure(figsize=(30, 20), dpi=400)
    fig.set_size_inches(18.5, 10.5, forward=True)
    ax1 = fig.add_subplot(111)
    performance.pct_change().cumsum().fillna(value=0.0).plot(ax=ax1,lw=2.,legend=True)
    ax1.set_title('Optimizations Performance Check',fontsize=60,fontweight='bold')
    ax1.grid(True,color='k',linestyle='-.',linewidth=2)
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=30)
    plt.xticks(size=20)
    plt.yticks(size=20)
    plt.show()
    #print(performance.pct_change().sum())
    to_plot()



# final iterator of eternal loop. Save recommendation, do another operation or leave.
if __name__ =='__main__':
    if 'Y' == input('want to analyze another portfolio?\n[Y]es or [N]o\n\n\t\t').upper():
        to_plot()    
