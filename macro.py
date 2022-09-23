import os 
import yfinance as yahoo
import pandas as pd
import datetime as dt
import numpy as np
import scipy.optimize as sco
from scipy import stats
import scrap
import ssl

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

        df,riskfree,pct,riskpct,mean,mean_rf,std,numerator,downside_risk,noa,weigths,\
        observations,mean_returns,cov,alpha,rf,num_portfolios,Upbound = data

        def sharpe_unbound():
            sharpe = pd.DataFrame(mean_rf['Mean']/(std['Std']), columns=['SharpeRatio'],index=pct.columns)
            sharpe = sharpe.sort_values('SharpeRatio', axis=0, ascending=False)
            sharpe[sharpe.SharpeRatio<0.0] = 0.0
            sharpe = sharpe[sharpe.head(50)>0].fillna(0)
            sharpe = sharpe / sharpe.sum()
            sharpe[sharpe.SharpeRatio>=Upbound] = Upbound
            sharpe = sharpe / sharpe.sum()
            sharpe = sharpe.sort_values('SharpeRatio',axis=0,ascending=False)
            sharpe = sharpe.sort_index(axis=0,ascending=True)
            return sharpe

        def sortino_ratio():
            sortino_ratio = pd.DataFrame(mean_rf['Mean'].to_numpy()/downside_risk**(1/2),columns=['SortinoRatio'])
            sortino_ratio = sortino_ratio.sort_values('SortinoRatio',axis=0,ascending=False)
            sortino_ratio[sortino_ratio.SortinoRatio<0.0] = 0.0
            sortino_ratio = sortino_ratio[sortino_ratio.head(50)>0].fillna(0)
            sortino_ratio = sortino_ratio / sortino_ratio.sum()
            sortino_ratio = sortino_ratio.sort_index(axis=0,ascending=True)
            sortino_ratio[sortino_ratio.SortinoRatio>=Upbound] = Upbound
            sortino_ratio = sortino_ratio / sortino_ratio.sum()
            sortino_ratio = sortino_ratio.sort_values('SortinoRatio',axis=0,ascending=False)
            sortino_ratio = sortino_ratio.sort_index(axis=0,ascending=True)
            return sortino_ratio

        def calc_neg_sharpe(weights, mean_returns, cov, rf):
            portfolio_return = np.sum(mean_returns * weights) * observations
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov, weights))) * np.sqrt(observations)
            sharpe_ratio = (portfolio_return - rf) / portfolio_std
            return -sharpe_ratio

        def max_sharpe_ratio(mean_returns, cov, rf):
            num_assets = len(mean_returns)
            args = (mean_returns, cov, rf)
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            bound = (0.0,Upbound)
            bounds = tuple(bound for asset in range(num_assets))
            result = sco.minimize(calc_neg_sharpe, num_assets*[1./num_assets,], args=args,
                                method='SLSQP', bounds=bounds, constraints=constraints)
            return result

        def optimal():
            optimal_port_sharpe = max_sharpe_ratio(mean_returns, cov, rf)
            optimal = pd.DataFrame(index=df.columns)
            optimal['weights'] = optimal_sharpe = pd.DataFrame([round(x,4) for x in optimal_port_sharpe['x']],index=df.columns)
            optimal = optimal / optimal.sum()
            return optimal 

        def calc_portfolio_VaR(weights, mean_returns, cov, alpha, observations):
            portfolio_return = np.sum(mean_returns * weights) * observations
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov, weights))) * np.sqrt(observations)
            portfolio_var = abs(portfolio_return - (portfolio_std * stats.norm.ppf(1 - alpha)))
            return portfolio_var

        def min_VaR(mean_returns, cov, alpha, observations):
            num_assets = len(mean_returns)
            args = (mean_returns, cov, alpha, observations)
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            bound = (0.0,Upbound)
            bounds = tuple(bound for asset in range(num_assets))
            result = sco.minimize(calc_portfolio_VaR, num_assets*[1./num_assets,], args=args,
                                method='SLSQP', bounds=bounds, constraints=constraints)
            return result

        def min_port_VaR():
            min_port_VaR = min_VaR(mean_returns, cov, alpha, observations)
            minimal_VaR = pd.DataFrame(index=df.columns)
            minimal_VaR['weights'] = pd.DataFrame([round(x,4) for x in min_port_VaR['x']],index=df.columns)
            return minimal_VaR

        def portfolio():
            portfolio = pd.DataFrame(index=df.columns)
            portfolio['MinVaR'] = min_port_VaR().values
            portfolio['SharpeRatio'] = optimal().values
            portfolio['SortinoRatio'] = sortino_ratio()
            portfolio['SharpeUnbound'] = sharpe_unbound()
            return portfolio

        optimizations = portfolio()

        def AdjustRisk(portfolio):
            """Provide the stock list of your portfolio
               to update risk by Component-Value-at-Risk"""
            data = df 
            returns = data.pct_change()
            correlation = returns.corr() # correlation
            covariance = returns.cov()  # covariance
            instruments = pd.DataFrame(index= data.columns)
            instruments['weigths'] = 1/len(instruments.index) # secure equal allocation 
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
            riskadj['new'] = portfolio.values  # Choosing the option with the highest return
            riskadj['condition'] = (riskadj.base / riskadj.CVaRattribution)
            riskadj['newrisk'] = (riskadj.new / riskadj.CVaRattribution)
            riskadj['differences'] = (riskadj.newrisk - riskadj.condition)  # apply this result as a percentage to multiply new weights
            riskadj['adjustments'] = (riskadj.newrisk - riskadj.condition) / riskadj.condition #ALARM if its negative sum up the difference, 
                                                        #if it is positive rest it, you need to have 0
            riskadj['suggested'] = riskadj.new * (1 + riskadj.adjustments)   
            riskadj['tototal'] = riskadj.suggested.sum()
            riskadj['MinCVaR'] = riskadj.suggested / riskadj.tototal
            return riskadj['MinCVaR']
        
        portfolioAdj = pd.DataFrame(index=optimizations.index)
        portfolioAdj['MinVaR'] = AdjustRisk(optimizations['MinVaR'])
        portfolioAdj['SharpeRatio'] = AdjustRisk(optimizations['SharpeRatio'])
        portfolioAdj['SortinoRatio'] = AdjustRisk(optimizations['SortinoRatio'])
        portfolioAdj['SharpeUnbound'] = AdjustRisk(optimizations['SharpeUnbound'])
        # OVERWRITE optimizations with all risk adjusted
        optimizations = portfolioAdj

        Series = pd.DataFrame()
        Series['SortinoRatio'] = ((df * portfolioAdj['SortinoRatio'].values).T.sum()).values
        Series['SharpeRatio'] = ((df * portfolioAdj['SharpeRatio'].values).T.sum()).values
        Series['SharpeUnbound'] = ((df * portfolioAdj['SharpeUnbound'].values).T.sum()).values
        Series['MinVaR'] = ((df * portfolioAdj['MinVaR'].values).T.sum()).values
        Series['BenchmarkEWAP'] = df.T.mean().values
        Series = Series.iloc[1:,:]

        # SafeGuard Nans
        pct = Series.pct_change()
        pct = pct.iloc[1:,:] 
        portfolioAdj = portfolioAdj.fillna(0)

        # Statistics Diagnose of optimizations 
        statistics_portfolios = pct.describe(percentiles=[0.01, 0.05, 0.10]).T
        statistics_portfolios['mad'] = pct.mad()
        statistics_portfolios['skew'] = pct.skew()
        statistics_portfolios['kurtosis'] = pct.kurtosis()
        statistics_portfolios['annualizedStd'] = statistics_portfolios['std'] * np.sqrt(len(Series))
        statistics_portfolios['annualizedMean'] = statistics_portfolios['mean'] * len(Series)
        statistics_portfolios['compensation'] = statistics_portfolios['annualizedMean'] / statistics_portfolios['annualizedStd']
        statistics_portfolios = statistics_portfolios.sort_values(by='compensation',ascending=False)

        # Compensation is a bare metric return / volatility (sharpe ratio in a nutshell).
        # Choose the best return but also at the best risk available.

        winner = str(statistics_portfolios.index[0])

        # For Cedears current tickets and price. We work with the date related to SP equivalent due to accesability
        df = df
        if warning == 2:
            comafi = pd.read_html('https://www.comafi.com.ar/2254-CEDEAR-SHARES.note.aspx')[0]
            # sort by alphabetic order
            comafi = comafi.sort_values('Símbolo BYMA',axis=0,ascending=True)
            comafi.index = range(len(comafi)) # update index order values
            cells = list(comafi['Ticker en Mercado de Origen'].values)
            BA = list(optimizations.index.values) 
            cedears = []
            for k in range(len(BA)):
              cedears.append(comafi['Símbolo BYMA'][cells.index(f'{BA[k]}')])
            cedears = [k + '.BA' for k in cedears]
            df = yahoo.download(cedears,period="10d",interval="2m")['Adj Close'].fillna(method="ffill")

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
