from packages import *
from optimizations import optimizations
import scrap

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

def megaManager():
  print("Type the market to operate:\n(1) SP500,\n(2) FTSE,\n(3) CEDEARS,\n(4) Nikkei225,\n(5) BOVESPA,\n(6) CANADA,\n(7) AUSTRALIA,\n(8) SHANGHAI,\n(9) CRYPTO\n(10) Merval")
  market = str(input("Which market do you wish to operate?... "))
  if market == '1':
      data = scrap.GSPC()
      symbol = 'GSPC'
  elif market == '2':
      data = scrap.FTSE()
      symbol = 'FTSE'
  elif market == '3':
      data = scrap.Cedears()
      symbol = 'CEDEARS'
  elif market == '4':
      data = scrap.NIKKEI()
      symbol = 'NIKKEI'
  elif market =='5':
      data = scrap.BOVESPA()
      symbol = 'BOVESPA'
  elif market == '6':
      data = scrap.CANADA()
      symbol = 'CANADA'
  elif market == '7':
      data = scrap.AUSTRALIA()
      symbol = 'AUSTRALIA'
  elif market == '8':
      data = scrap.Shanghai()
      symbol = 'SHANGHAI'
  elif market == '9':
      data = scrap.binance()
      symbol = 'CRYPTO'
      hedge = yahoo.download('PAXG-USD',period='1d')['Adj Close']
  elif market == '10':
      data = scrap.Merval()
      symbol = 'MERVAL'


  df, portfolioAdj, statistics_portfolios = optimizations(data)
  winner = str(statistics_portfolios.index[0])

 # Once all calculus is done. Pass to generate specific portfolios
  if ("" == str(input("CALCULATIONS DONE SUCCESSFULLY. Press [Enter] to build portfolios."))):
    for i in range(int(input("how many portfolios you want? "))):
      client = input(f"enter the name of your client {i}: ")
      profile = str(input("Choose Optimization\n1 SharpeRatio\n2 MonteVaR\n3 MonteSharpe\n4 MinVaR\nOther option is the winner\nMake your choice: "))
      if profile == '1':
          profile = 'SharpeRatio'
      elif profile == '2':
          profile = 'MonteVaR'
      elif profile == '3':
          profile = 'MonteSharpe'
      elif profile == '4':
          profile = 'MinVaR'
      else:
          profile = winner
      name = str(client) + str(' ') + str(profile) + str(' ') + str(dt.date.today()) + '.xlsx'
      folder = os.makedirs('./NewOnes/', exist_ok=True)
      capital = int(input(f"How much {client} will invest? "))
      path = f'./NewOnes/{symbol} ' + client + ' ' + str(input("Email address? "))\
              + ' ' + str(capital) + ' ' + profile + ' ' + str(dt.date.today()) + '.xlsx'
      if market == '9':
          # Add a Hedge of PAXGUSDT 20%
          best = pd.DataFrame(index=df.columns.to_list()+['PAXG-USD'])
          best['capital'] = capital
          best['price'] = df.iloc[-1].to_list() + [hedge.values[-1]]
          # ENDS HEDGING
          best['weights'] = portfolioAdj[f'{profile}'].to_list() + [0.24]
          best['weights'] =  best['weights'] / best['weights'].sum()
          best['cash'] = (best['capital'] * best['weights'])
          best['cash'] = round(best['cash'])
          best['nominal'] =  best['cash'] // best['price']
          best['invested'] = best['price'] * best['nominal']
          best['percentage'] = best['invested'] / sum(best['invested'])
          best['total'] = sum(best['invested'])
          best['liquid'] = best['capital'] - best['total']
          best = best[best.weights!=0].dropna() # remove all stocks that you do not invest in
          ### to adjust weights in order to invest the maximum capital possible
          reinvest = (best['liquid'][0] / best['total'][0]) + 1 # ROUND DOWN DIFFERENCE
          best['weights'] = (best['weights'] * reinvest)
          best['weights'] = best['weights'] / best['weights'].sum()
          best['cash'] = (best['capital'] * best['weights']) 
          # crypto remember fractional investing
          best['nominal'] =  best['cash'] / best['price']
          best['invested'] = best['price'] * best['nominal']
          best['percentage'] = best['invested'] / sum(best['invested'])
          # minimum keep 3% in order to invest in an asset
          best = best[best['percentage']>0.03]
          best['invested'] = round(best['invested'])
          best['total'] = sum(best['invested'])
          best['liquid'] = best['capital'] - best['total']
      else:
          best = pd.DataFrame(index=df.columns)
          best['capital'] = capital
          best['price'] = df.tail(1).T.values
          best['weights'] = portfolioAdj[f'{profile}'].values
          best['weights'] =  best['weights'] / best['weights'].sum()
          best['cash'] = (best['capital'] * best['weights'])
          best['cash'] = round(best['cash'])
          best['nominal'] =  best['cash'] // best['price']
          best['invested'] = best['price'] * best['nominal']
          best['percentage'] = best['invested'] / sum(best['invested'])
          # minimum keep 3% in order to invest in an asset
          best = best[best['percentage']>0.03]
          best['total'] = sum(best['invested'])
          best['liquid'] = best['capital'] - best['total']
          reinvest = (best['liquid'][0] / best['total'][0]) + 1 # ROUND DOWN DIFFERENCE
          best['weights'] = (best['weights'] * reinvest)
          best['weights'] = best['weights'] / best['weights'].sum()
          best['cash'] = (best['capital'] * best['weights']) 
          # crypto remember fractional investing
          best['nominal'] =  best['cash'] // best['price']
          best['invested'] = best['price'] * best['nominal']
          best['percentage'] = best['invested'] / sum(best['invested'])
          best['invested'] = round(best['invested'])
          best['total'] = sum(best['invested'])
          best['liquid'] = best['capital'] - best['total']

    
      best = best.sort_index(ascending=True)
      writer = pd.ExcelWriter(path, engine='xlsxwriter')
      best.to_excel(writer,sheet_name=f'{profile}')
      portfolioAdj.to_excel(writer, sheet_name='portfolioWeights')
      statistics_portfolios.to_excel(writer, sheet_name='descriptiveStatistics')
      writer.close()

handle = megaManager()
