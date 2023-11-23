from packages import *

def optimizations(data):
  df,riskfree,pct,riskpct,mean,mean_rf,std,numerator,downside_risk,noa,weights,\
      observations,mean_returns,cov,alpha,rf,num_portfolios,Upbound = data

  def calc_portfolio_perf(weights, mean_returns, cov, rf):
    portfolio_return = np.sum(mean_returns * weights) * (len(mean_returns))
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov, weights))) * np.sqrt(len(mean_returns))
    sharpe_ratio = (portfolio_return - rf) / portfolio_std
    return portfolio_return, portfolio_std, sharpe_ratio

  def simulate_random_portfolios(num_portfolios, mean_returns, cov, rf):
    results_matrix = np.zeros((len(mean_returns)+3, num_portfolios))
    for i in range(num_portfolios):
        # set some bounds, as we dont want more than x% in?!?jedi=0,  an asset?!? (*_*o: Sized*_*) ?!?jedi?!?
        weights = np.random.uniform(low=0.0, high=0.125*len(mean_returns), size=(len(mean_returns)))
        weights[weights<0.025], weights[weights>0.125] = 0,0.125 # do not want micro allocation
        weights /= np.sum(weights)
        portfolio_return, portfolio_std, sharpe_ratio = calc_portfolio_perf(weights, mean_returns, cov, rf)
        results_matrix[0,i] = portfolio_return
        results_matrix[1,i] = portfolio_std
        results_matrix[2,i] = sharpe_ratio
        #iterate through the weight vector and add data to results array
        for j in range(0,len(weights)):
            results_matrix[j+3,i] = weights[j]
            results_df = pd.DataFrame(results_matrix.T,columns=['ret','stdev','sharpe'] + [ticker for ticker in df.columns.to_list()])

    return results_df

  results_frame = simulate_random_portfolios(num_portfolios, mean_returns, cov, rf)
  monte_sharpe = results_frame.iloc[results_frame['sharpe'].idxmax()][3:]
  monte_mvar = results_frame.iloc[results_frame['stdev'].idxmin()][3:]


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

  def portfolio(): # create a df that triggers optimizations above
    portfolio = pd.DataFrame(index=df.columns)
    portfolio['MinVaR'] = min_port_VaR().values
    portfolio['SharpeRatio'] = optimal().values
    portfolio['MonteVaR'] = monte_mvar.values
    portfolio['MonteSharpe'] = monte_sharpe.values
    return portfolio

  optimizations = portfolio()

  def AdjustRisk(portfolio): # Apply CVaR to all portfolio to reduce risk
    data = df
    returns = data.pct_change()
    correlation = returns.corr() # correlation
    covariance = returns.cov()  # covariance
    instruments = pd.DataFrame(index= data.columns)
    instruments['weights'] = 1/len(instruments.index) # secure equal allocation
    instruments['deltas'] = (instruments.weights * correlation).sum() # deltas as elasticity of the assets
    instruments['Stdev'] = returns.std()
    instruments['stress'] = (instruments.deltas * instruments.Stdev) * 3 # stress applied at 4 deviations
    instruments['portfolio_stress'] = instruments.stress.sum() # the stress of the portfolio
    risk = pd.DataFrame(index=data.columns)
    risk['numerator'] = (instruments.deltas.multiply(covariance)).sum()
    risk['denominator'] = data.pct_change().std() * (-1.96) # 95%, -2.365 is 99%
    risk['GradVaR'] = -risk.numerator / risk.denominator
    risk['CVaRj'] = risk.GradVaR * instruments.deltas # Component VaR of the Risk Factors j
    risk['thetai'] = (risk.CVaRj * correlation).sum() # Theta i of the instruments
    risk['CVaRi'] = risk.thetai * (1/len(data.columns)) # Component VaR of the Instruments i
    risk['totalCVaRi'] = risk.CVaRi.sum() #total CVaR of the portfolio
    risk['CVaRattribution'] = risk.CVaRi / risk.totalCVaRi # risk allocation by instrument in the portfolio
    riskadj = pd.DataFrame(index=data.columns)
    riskadj['base'] = instruments['weights'].values
    riskadj['CVaRattribution'] = risk.CVaRattribution.sort_values(axis=0,ascending=False)
    riskadj['new'] = portfolio.values  # Choosing the option with the highest return
    riskadj['condition'] = (riskadj.base / riskadj.CVaRattribution)
    riskadj['newrisk'] = (riskadj.new / riskadj.CVaRattribution)
    riskadj['differences'] = (riskadj.newrisk - riskadj.condition)  # apply this result as a percentage to multiply new weights
    riskadj['adjustments'] = (riskadj.newrisk - riskadj.condition) / riskadj.condition #ALARM if its negative sum up the difference, if it is positive rest it, you need to have 0
    riskadj['suggested'] = riskadj.new * (1 + riskadj.adjustments)
    riskadj['tototal'] = riskadj.suggested.sum()
    riskadj['MinCVaR'] = riskadj.suggested / riskadj.tototal
    return riskadj['MinCVaR']

  # create new df with all weights adjusted
  portfolioAdj = pd.DataFrame(index=optimizations.index)
  portfolioAdj['MinVaR'] = AdjustRisk(optimizations['MinVaR'])
  portfolioAdj['SharpeRatio'] = AdjustRisk(optimizations['SharpeRatio'])
  portfolioAdj['MonteVaR'] = AdjustRisk(optimizations['MonteVaR'])
  portfolioAdj['MonteSharpe'] = AdjustRisk(optimizations['MonteSharpe'])
  #portfolioAdj[portfolioAdj<0.025], portfolioAdj[portfolioAdj>0.125] = 0, 0.125
  portfolioAdj = portfolioAdj.fillna(0)
  # OVERWRITE optimizations with all risk adjusted
  optimizations = portfolioAdj

  Series = pd.DataFrame()
  Series['MonteVaR'] =((df * portfolioAdj['MonteVaR'].values).T.sum()).values
  Series['SharpeRatio'] = ((df * portfolioAdj['SharpeRatio'].values).T.sum()).values
  Series['MonteSharpe'] = ((df * portfolioAdj['MonteSharpe'].values).T.sum()).values
  Series['MinVaR'] =      ((df * portfolioAdj['MinVaR'].values).T.sum()).values
  Series['BenchmarkEWAP'] = df.T.mean().values
  Series = Series.iloc[1:,:]

  # SafeGuard Nans
  pct = Series.pct_change()
  pct = pct.iloc[1:,:]

  # sheet to have statistics metrics of the portfolio
  statistics_portfolios = pct.describe(percentiles=[0.01, 0.05, 0.10]).T
  #statistics_portfolios['mad'] = pct.mad()
  statistics_portfolios['skew'] = pct.skew()
  statistics_portfolios['kurtosis'] = pct.kurtosis()
  statistics_portfolios['annualizedStd'] = statistics_portfolios['std'] * np.sqrt(len(Series))
  statistics_portfolios['annualizedMean'] = statistics_portfolios['mean'] * len(Series)
  # Compensation is a bare metric return / volatility (sharpe ratio in a nutshell).
  statistics_portfolios['compensation'] = statistics_portfolios['annualizedMean'] / statistics_portfolios['annualizedStd']
  statistics_portfolios = statistics_portfolios.sort_values(by='compensation',ascending=False)

  # Choose the best return at the best risk available.
  winner = str(statistics_portfolios.index[0])

  return [df, portfolioAdj, statistics_portfolios]
