from packages import *
# This file covers the cycle of portolio management tasks
# with the purpose of being executed in the Console
"""4 main functions to handle the cycle of portfolio management from the clients.xlsx inputs
  0 Do nothing.
  1 portfolioMonitor to update and suggets rebalance allocaiton
  2 DepositOrWithdraw suggest new composition based on a capital change given in Status = 2 & ammount to change.
  3 portfolioRiskUpdated rebalance allocation according to CVaR analysis
  4 BacktoBasics reverse previous functions format to original format
"""

def PortfolioMonitor(data):
  """Provide a DataFrame.index as the stock list 
     to update data, DataFrame['quantity'] &
     Data['pricepaid'] for the stocks """
  holdings = data # pd.read_excel(str(input("Type excel to work with: ")))
  portfolio = pd.DataFrame(index=holdings.iloc[:,0])
  portfolio['nominal'] = holdings['nominal'].values
  portfolio['pricePaid'] = holdings['price'].values
  portfolio['weights'] = (portfolio['nominal'] * portfolio['pricePaid']) / sum(portfolio['nominal'] * portfolio['pricePaid'])
  portfolio['notionalStart'] = sum(portfolio['nominal'] * portfolio['pricePaid'])
  portfolio['oldLiquidity'] = holdings['liquid'].values
  stocks = list(portfolio.index)
  portfolio['priceToday'] = (yahoo.download(stocks,period="7d",interval="2m",prepost=True)['Adj Close'].fillna(method='ffill')).tail(1).T
  nans = portfolio[portfolio['priceToday'].isna()]
  portfolio = portfolio[portfolio['priceToday'].notna()]
  portfolio['notionalToday'] = sum(portfolio['priceToday'] * portfolio['nominal'])
  portfolio['PnLpercent'] = portfolio['notionalToday'] / portfolio['notionalStart']
  portfolio['PnLpercentEach'] = portfolio['priceToday'] / portfolio['pricePaid']
  # En nuevo nominal sumamos el resultado obtenido mas el remanente liquido para reinvertir, siendo nuestro total disponible
  portfolio['nominalNew'] = (portfolio['weights'] * (portfolio['notionalToday'] + portfolio['oldLiquidity']) // portfolio['priceToday']) # nuevo nominal
  portfolio['adjust'] = portfolio['nominalNew'] - portfolio['nominal'] # ajuste nominal
  portfolio['percentReb'] = (portfolio['nominalNew'] * portfolio['priceToday']) / sum(portfolio['nominalNew'] * portfolio['priceToday'])
  # Columnas vinculantes para conectar mes anterior con el proximo ya armado
  portfolio['notionalRebalance'] = sum(portfolio['nominalNew'] * portfolio['priceToday'])
  portfolio['liquidityToReinvest'] =  (portfolio['notionalToday'] + portfolio['oldLiquidity']) - portfolio['notionalRebalance']
  return [portfolio,nans]

def DepositOrWithdraw(data, ammount):
  """Provide a DataFrame update with the ammount to change Notional"""
  ammount = float(ammount)
  holdings = data # pd.read_excel(str(input("Type excel to work with: ")))
  portfolio = pd.DataFrame(index=holdings['Unnamed: 0'].values)
  portfolio['nominal'] = holdings['nominal'].values
  portfolio['pricePaid'] = holdings['price'].values
  portfolio['weights'] = (portfolio['nominal'] * portfolio['pricePaid']) / sum(portfolio['nominal'] * portfolio['pricePaid'])
  portfolio['notionalStart'] = sum(portfolio['nominal'] * portfolio['pricePaid'])
  portfolio['oldLiquidity'] = holdings['liquid'].values
  stocks = list(portfolio.index)
  portfolio['priceToday'] = (yahoo.download(stocks,period="2d",interval="1m")['Adj Close'].fillna(method='ffill')).tail(1).T
  # na = portfolio[portfolio['priceToday'].isna()].index.to_list()
  portfolio = portfolio[portfolio['priceToday'].notna()]
  nans = portfolio[portfolio['priceToday'].isna()]
  portfolio['notionalToday'] = sum(portfolio['priceToday'] * portfolio['nominal'])
  portfolio['PnLpercent'] = portfolio['notionalToday'] / portfolio['notionalStart']
  portfolio['PnLpercentEach'] = portfolio['priceToday'] / portfolio['pricePaid']
  portfolio['DepositOrWithdraw'] = ammount
  # New nominal given by updated value of our shares plus rebalance with the available liquidity
  portfolio['capitalNew'] = (portfolio['oldLiquidity'] + portfolio['notionalToday'] + portfolio['DepositOrWithdraw'])
  portfolio['nominalNew'] = (portfolio['capitalNew'] * portfolio['weights']) // portfolio['priceToday']
  portfolio['adjust'] = portfolio['nominalNew'] - portfolio['nominal'] # ajuste nominal
  portfolio['percentReb'] = (portfolio['nominalNew'] * portfolio['priceToday']) / sum(portfolio['nominalNew'] * portfolio['priceToday'])
  # Link previous statements with new situation
  portfolio['notionalRebalance'] = sum(portfolio['nominalNew'] * portfolio['priceToday'])
  portfolio['liquidityToReinvest'] = portfolio['capitalNew'] - portfolio['notionalRebalance']
  return [portfolio,nans]


def AdjustRisk(data):
  """Provide the stock list of your portfolio
     to update risk by Component-Value-at-Risk"""
  portfolio = data # pd.read_excel(str(input("Type excel to work with: ")))
  listado = list(portfolio['Unnamed: 0'].values)
  data = yahoo.download(listado,period="1y",interval="60m")['Adj Close'].fillna(method='ffill')
  nans = data.loc[:, data.isna().any()].columns.to_list()
  data = data.dropna(axis=1)
  portfolio = portfolio[portfolio['Unnamed: 0'].isin(data.columns.to_list())]
  returns = np.log(data) - np.log(data.shift(1)) # logarithmic returns
  correlation = returns.corr() # correlation
  covariance = returns.cov()  # covariance
  instruments = pd.DataFrame(index= data.columns)
  sample = np.random.random_sample(size=(len(data.columns),1)) + (1.0 / len(data.columns))
  sample /= np.sum(sample)
  instruments['weigths'] = sample # secure allocation is equal 1
  instruments['deltas'] = (instruments.weigths * correlation).sum() # deltas as elasticity of the assets
  instruments['Stdev'] = returns.std()
  instruments['stress'] = (instruments.deltas * instruments.Stdev) * 3 # stress applied at 4 deviations
  instruments['portfolio_stress'] = instruments.stress.sum() # the stress of the portfolio
  risk = pd.DataFrame(index=data.columns)
  risk['numerator'] = (instruments.deltas.multiply(covariance)).sum()
  risk['denominator'] = data.pct_change().std() * (-2.365)
  risk['GradVaR'] = -risk.numerator / risk.denominator
  risk['CVaRj'] = risk.GradVaR * instruments.deltas # Component VaR of the Risk Factors j
  risk['thetai'] = (risk.CVaRj * correlation).sum() # Theta i of the instruments
  risk['CVaRi'] = risk.thetai * (1/len(data.columns)) # Component VaR of the Instruments i
  risk['totalCVaRi'] = risk.CVaRi.sum() #total CVaR of the portfolio
  risk['CVaRattribution'] = risk.CVaRi / risk.totalCVaRi # risk allocation by instrument in the portfolio
  riskadj = pd.DataFrame(index=data.columns)
  riskadj['base'] = instruments['weigths'].values
  riskadj['CVaRattribution'] = risk.CVaRattribution.sort_values(axis=0,ascending=False)
  riskadj['new'] = portfolio['weights'].values  # Choosing the option with the highest return
  riskadj['condition'] = (riskadj.base / riskadj.CVaRattribution)
  riskadj['newrisk'] = (riskadj.new / riskadj.CVaRattribution)
  riskadj['differences'] = (riskadj.newrisk - riskadj.condition)  # apply this result as a percentage to multiply new weights
  riskadj['adjustments'] = (riskadj.newrisk - riskadj.condition) / riskadj.condition #ALARM if its negative sum up the difference,
                                              #if it is positive rest it, you need to have 0
  riskadj['suggested'] = riskadj.new * (1 + riskadj.adjustments)
  riskadj['tototal'] = riskadj.suggested.sum()
  riskadj['MinCVaR'] = riskadj.suggested / riskadj.tototal
  result = pd.DataFrame(riskadj['MinCVaR'].values,columns=['MinCVaR'],index=data.columns)
  result[result.MinCVaR>=0.12] = 0.12 # ensures bounds limit
  result['MinCVaR'] = result['MinCVaR'] / sum(result['MinCVaR'])
  result['lastPrice'] = (data.tail(1).T.values)
  portfolio['MinCVaR'] = result['MinCVaR'].values
  portfolio['lastPrice'] = result['lastPrice'].values
  return [portfolio,nans]

def portfolioRiskUpdated(data):
  """Provide your portfolio composition to apply
     the update of risk by Component-Value-at-Risk"""
  update, nans = AdjustRisk(data)
  df = pd.DataFrame(index=update['Unnamed: 0'].values)
  df['nominal'] = update['nominal'].values
  df['pricePaid'] = update['price'].values  
  df['weights'] = (update['MinCVaR'].values) / sum(update['MinCVaR'].values) # new weights according to Update and ensures it is 100%
  df['notionalStart'] = sum(df['nominal'] * df['pricePaid'])
  df['oldLiquidity'] = update['liquid'].values
  df['priceToday'] = update['lastPrice'].values
  df['notionalToday'] = sum(df['priceToday'] * df['nominal'])
  df['PnLpercent'] = df['notionalToday'] / df['notionalStart']
  df['PnLpercentEach'] = df['priceToday'] / df['pricePaid']
  # En nuevo nominal sumamos el resultado obtenido mas el remanente liquido para reinvertir, siendo nuestro total disponible
  df['nominalNew'] = ((df['weights'] * (df['notionalToday'] + df['oldLiquidity'])) // df['priceToday']) # nuevo nominal
  df['adjust'] = df['nominalNew'] - df['nominal'] # ajuste nominal
  df['percentReb'] = (df['nominalNew'] * df['priceToday']) / sum(df['nominalNew'] * df['priceToday'])
  # Columnas vinculantes para conectar mes anterior con el proximo ya armado
  df['notionalRebalance'] = sum(df['nominalNew'] * df['priceToday'])
  df['liquidityToReinvest'] =  (df['notionalToday'] + df['oldLiquidity']) - df['notionalRebalance']
  return [df,nans]

def BacktoBasics(portfolio):
  """Convert back suggestions to original format"""
  df = pd.DataFrame(pd.DataFrame(data=(portfolio.notionalRebalance.values + portfolio.liquidityToReinvest.values),columns=['capital'],index=portfolio.index))
  df['price'] = portfolio['priceToday'].values
  df['weights'] = portfolio['percentReb'].values
  df['cash'] = (df['capital'] * df['weights'])
  df['nominal'] = df['cash'] // df['price']
  df['invested'] = df['price'] * df['nominal']
  df['percentage'] = df['invested'] / sum(df['invested'])
  df['total'] = sum(df['invested'])
  df['liquid'] = df['capital'] - df['total']
  return df 
