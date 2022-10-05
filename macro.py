from packages import *
from packages import *
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

# read the database and generate all portfolio at once
clients = pd.read_excel('new_clients.xlsx')
mercados = ['GSPC','FTSE','CEDEARS','NIKKEI','BOVESPA','CANADA','AUSTRALIA','SHANGHAI','CRYPTO','MERVAL']

path = []
for i in range(len(clients)):
    path.append(str(clients.Symbol.values[i]) + ' ' + clients['Names'].values[i] + ' ' + clients['Emails'].values[i] + ' ' + str(clients['Money'].values[i]) + ' ' + str(clients['Risk'].values[i]) + str(' ') + str(dt.date.today()) + '.xlsx')

clients['Path'] = path

dfs = []
for i in range(len(mercados)):
    dfs.append(clients[clients.Markets==i])
    dfs[i].index = range(len(dfs[i]))

markets = clients.Markets.to_list()
numbers = sorted(set(markets),key=markets.index)
numbers.sort()

""" Set markets numbers as parameters of megaManager to loop data of the excel  """
calls = [scrap.GSPC,scrap.FTSE,scrap.Cedears,scrap.NIKKEI,scrap.BOVESPA,\
        scrap.CANADA,scrap.AUSTRALIA,scrap.Shanghai,scrap.binance,\
            scrap.Merval]

def megaManager():
    for i in range(len(numbers)): # number identifies the market
        info = calls[numbers[i]]  # call the respective market data
        data = info()
        warning = numbers[i]      # to know which element we are iterating and align markets data variables
        if warning == 8:
            hedge = yahoo.download('BTCDOWN-USD',period='1d')['Adj Close']


        df, portfolioAdj, statistics_portfolios = optimizations(data)
        # Compensation is a bare metric return / volatility (sharpe ratio in a nutshell).
        # Choose the best return but also at the best risk available.

        winner = str(statistics_portfolios.index[0])

        # OVERWRITE NUMBERS TO STRINGS OF THE PROPER NAMES to be saved properly in the DB
        names = ['GSPC','FTSE','CEDEARS','NIKKEI','BOVESPA','CANADA','AUSTRALIA','SHANGHAI','CRYPTO','MERVAL']
        for j in range(len(dfs[warning]['Path'])):
            if warning == 8:
              folder = os.makedirs(f'./NewOnes/', exist_ok=True)
              path = f'./NewOnes/' + str(dfs[warning]['Path'].values[j])
              # Add a Hedge of BTCDOWNDUSDT 20%
              best = pd.DataFrame(index=df.columns.to_list()+['BTCDOWN-USD'])
              best['capital'] = float(dfs[warning]['Money'].values[j])
              best['price'] = df.iloc[-1].to_list() + [hedge.values[-1]]
              best['weights'] = optimizations.loc[:,dfs[warning]['Risk'].values[j]].to_list() + [0.2]
              best['weights'] =  best['weights'] / best['weights'].sum()
              best['cash'] = (best['capital'] * best['weights'])
              # ENDS HEDGING
              best['cash'] = round(best['cash'])
              best['nominal'] =  best['cash'] // best['price']
              best['invested'] = best['price'] * best['nominal']
              best['percentage'] = best['invested'] / sum(best['invested'])
              best['total'] = sum(best['invested'])
              best['liquid'] = best['capital'] - best['total']
              best = best[best.nominal!=0].dropna() # remove all stocks that you do not invest in
              ### to adjust weights in order to invest the maximum capital possible
              reinvest = (best['liquid'][0] / best['total'][0]) + 1 # ROUND DOWN DIFFERENCE
              best['weights'] = (best['weights'] * reinvest)
              best['weights'] = best['weights'] / best['weights'].sum()
              best['cash'] = (best['capital'] * best['weights'])
              best['nominal'] =  best['cash'] // best['price']
              best = best[best['invested']>10]
              best['invested'] = best['price'] * best['nominal']
              best['invested'] = round(best['invested'])
              best['percentage'] = best['invested'] / sum(best['invested'])
              best['total'] = sum(best['invested'])
              best['liquid'] = best['capital'] - best['total']
            else:
              folder = os.makedirs(f'./NewOnes/', exist_ok=True)
              path = f'./NewOnes/' + str(dfs[warning]['Path'].values[j])
              best = pd.DataFrame(index=df.columns.to_list())
              best['capital'] = float(dfs[warning]['Money'].values[j])
              best['price'] = df.iloc[-1].to_list()
              best['weights'] = optimizations.loc[:,dfs[warning]['Risk'].values[j]].to_list()
              best['weights'] =  best['weights'] / best['weights'].sum()
              best['cash'] = (best['capital'] * best['weights'])
              best['cash'] = round(best['cash'])
              best['nominal'] =  best['cash'] / best['price']
              best['invested'] = best['price'] * best['nominal']
              best['percentage'] = best['invested'] / sum(best['invested'])
              best['total'] = sum(best['invested'])
              best['liquid'] = best['capital'] - best['total']
              best = best[best.nominal!=0].dropna() # remove all stocks that you do not invest in
              ### to adjust weights in order to invest the maximum capital possible
              reinvest = (best['liquid'][0] / best['total'][0]) + 1 # ROUND DOWN DIFFERENCES
              best['weights'] = (best['weights'] * reinvest)
              best['weights'] = best['weights'] / best['weights'].sum()
              best['cash'] = (best['capital'] * best['weights'])
              best['nominal'] =  best['cash'] // best['price']
              best['invested'] = best['price'] * best['nominal']
              best['percentage'] = best['invested'] / sum(best['invested'])
              best['total'] = sum(best['invested'])
              best['liquid'] = best['capital'] - best['total']
              best = best[best.nominal!=0].dropna() # remove all stocks that you do not invest in

            writer = pd.ExcelWriter(path, engine='xlsxwriter')
            best.to_excel(writer,sheet_name=f'{dfs[warning]["Names"].values[j]}')
            portfolioAdj.to_excel(writer, sheet_name='portfolioWeights')
            statistics_portfolios.to_excel(writer, sheet_name='descriptiveStatistics')
            writer.save()

handle = megaManager()
