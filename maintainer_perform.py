from packages import *
'''
We read the status of scanner.xlsx in order to know what operation 
we have to do to each client
0 nothing
1 update to original weigths
2 change amount of investment
3 reset risk

base on that we need to
(1) grab excel from DATABASE
(2) perform the change
(3) generate new name (grab old image and send it to OldPortolios folder)
Name must be
Update/{Operation} {Capital old} ..rest as convention was
(4) once all changes are done we reset scanner.xlsx to 0 (as everything was done)
(5) run update.py to inform proper changes to the clients
'''



clients = pd.read_excel('/.scanner.xlsx')
clients = clients[clients.Status!=0]
clients.index = range(len(clients))
excel = pd.DataFrame(clients.Path.to_list(),columns=['Path'])
excel.index= range(len(excel))
# create a common dataframe with all tickets, to avoid
# downloading tickets per each client

lista = []
for i in range(len(excel)):
    index = pd.read_excel(excel.Path.values[i])
    index = index.iloc[:,0].to_list()
    lista += index
    lista = list(dict.fromkeys(lista))

data = yahoo.download(lista,period="252d",interval="60m")["Adj Close"].fillna(method="ffill")
today = dt.date.today().strftime('%d-%m-%Y')

# 0 do nothing, 1 rebalance by update, 2 perform withdraw and 3 reset risk by CVaR

for i in range(len(clients)):
    if clients.Status.values[i] == 0:
        pass
    elif clients.Status.values[i] == 1:
      # Update values of the portfolio
      holdings = pd.read_excel(excel.Path.values[i])
      previous = holdings.copy()
      path = str(clients['Path'][i])
      oldcapital = str(clients.Path[i].split()[-3])
      action = 'Update'
      portfolio = pd.DataFrame(index=holdings.iloc[:,0]) 
      info = data.copy()
      update = []
      for j in range(len(portfolio)):
          update.append(info[f'{portfolio.index.values[j]}'].values[-1])
      portfolio = pd.DataFrame(index=holdings.iloc[:,0]) # rewrite
      portfolio['nominal'] = holdings['nominal'].values
      portfolio['pricePaid'] = holdings['price'].values
      portfolio['weights'] = (portfolio['nominal'] * portfolio['pricePaid']) / sum(portfolio['nominal'] * portfolio['pricePaid'])
      portfolio['notionalStart'] = sum(portfolio['nominal'] * portfolio['pricePaid'])
      portfolio['oldLiquidity'] = holdings['liquid'].values
      stocks = list(portfolio.index)
      portfolio['priceToday'] = update
      portfolio['notionalToday'] = sum(portfolio['priceToday'] * portfolio['nominal'])
      portfolio['PnLpercent'] = portfolio['notionalToday'] / portfolio['notionalStart']
      portfolio['PnLpercentEach'] = portfolio['priceToday'] / portfolio['pricePaid']
      # En nuevo nominal sumamos el resultado obtenido mas el remanente liquido para reinvertir, siendo nuestro total disponible
      portfolio['nominalNew'] = (portfolio['weights'] * (portfolio['notionalToday'] + portfolio['oldLiquidity']) // portfolio['priceToday']) # nuevo nominal
      portfolio['adjust'] = portfolio['nominalNew'] - portfolio['nominal'] # ajuste nominal
      portfolio['percentReb'] = (portfolio['nominalNew'] * portfolio['priceToday']) / sum(portfolio['nominalNew'] * portfolio['priceToday'])
      # Columnas vinculantes para conectar mes anterior con el proximo ya armado
      portfolio['notionalRebalance'] = sum(portfolio['nominalNew'] * portfolio['priceToday'])
      portfolio['liquidityToReinvest'] =  ((portfolio['notionalToday'] + portfolio['oldLiquidity']) - portfolio['notionalRebalance'])
      capital = str(int(portfolio.notionalToday.values[0] + portfolio.liquidityToReinvest.values[0]))
      basics = portfolio.copy()
      basics = tracker.BacktoBasics(basics)
      folder, operations = os.makedirs('Oldportfolios',exist_ok=True), os.makedirs('Update',exist_ok=True)
      name = path
      older, newer = path.replace('./DATABASE/','./Oldportfolios/'), path.replace('./DATABASE/',f'./Update/{action} {oldcapital} ')
      shutil.move(f'{name}',f'{older}')
      newName = ' '.join(newer.split()[:-1])
      newName = newName.split()
      newName[-2] = str(capital)
      # New Name UPDATED to the end
      newName = ' '.join(newName) + ' ' + str(dt.date.today()) + '.xlsx'
      writer = pd.ExcelWriter(f'{newName}',engine='xlsxwriter')
      basics.to_excel(writer,sheet_name=f'Updated {dt.date.today()}')
      portfolio.to_excel(writer,sheet_name='Update Done')
      previous.to_excel(writer,sheet_name='Previous Composition')
      writer.save()
      # Reset Status to 0 as the time done the operation
      clients.Status.values[i] = 0
      clients.TimeStamp.values[i] = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

      # Change Capital
    elif clients.Status.values[i] == 2:
      # Change capital ammount of the investment, positive or negative, satisfying original weights
      holdings = pd.read_excel(excel.Path.values[i])
      previous = holdings.copy()
      path = str(clients['Path'][i])
      oldcapital = str(clients.Path[i].split()[-3])
      action = 'Change'
      portfolio = pd.DataFrame(index=holdings.iloc[:,0]) 
      info = data.copy()
      update = []
      for j in range(len(portfolio)):
          update.append(info[f'{portfolio.index.values[j]}'].values[-1])
      portfolio = pd.DataFrame(index=holdings.iloc[:,0]) # rewrite
      portfolio['nominal'] = holdings['nominal'].values
      portfolio['pricePaid'] = holdings['price'].values
      portfolio['weights'] = (portfolio['nominal'] * portfolio['pricePaid']) / sum(portfolio['nominal'] * portfolio['pricePaid'])
      portfolio['notionalStart'] = sum(portfolio['nominal'] * portfolio['pricePaid'])
      portfolio['oldLiquidity'] = holdings['liquid'].values
      portfolio['priceToday'] = update
      portfolio['notionalToday'] = sum(portfolio['priceToday'] * portfolio['nominal'])
      portfolio['PnLpercent'] = portfolio['notionalToday'] / portfolio['notionalStart']
      portfolio['PnLpercentEach'] = portfolio['priceToday'] / portfolio['pricePaid']
      portfolio['DepositOrWithdraw'] = float(clients.Change.values[i])
      portfolio['capitalNew'] = (portfolio['oldLiquidity'] + portfolio['notionalToday'] + portfolio['DepositOrWithdraw'])
      portfolio['nominalNew'] = (portfolio['capitalNew'] * portfolio['weights']) // portfolio['priceToday']
      portfolio['adjust'] = portfolio['nominalNew'] - portfolio['nominal'] # ajuste nominal
      portfolio['percentReb'] = (portfolio['nominalNew'] * portfolio['priceToday']) / sum(portfolio['nominalNew'] * portfolio['priceToday'])
      # Link previous statements with new situation
      portfolio['notionalRebalance'] = sum(portfolio['nominalNew'] * portfolio['priceToday'])
      portfolio['liquidityToReinvest'] = portfolio['capitalNew'] - portfolio['notionalRebalance']
      capital = str(int(portfolio.capitalNew.values[0]))
      basics = portfolio.copy()
      basics = tracker.BacktoBasics(basics)
      folder, operations = os.makedirs('Oldportfolios',exist_ok=True), os.makedirs('Update',exist_ok=True)
      name = path
      older, newer = path.replace('./DATABASE/','./Oldportfolios/'), path.replace('./DATABASE/',f'./Update/{action} {oldcapital} ')
      shutil.move(f'{name}',f'{older}')
      newName = ' '.join(newer.split()[:-1])
      newName = newName.split()
      newName[-2] = str(capital)
      # NewName Changed at the end. To iterate mails acknowledging the operation made
      newName = ' '.join(newName) + ' ' + str(dt.date.today()) + f' {clients.Change.values[i]}.xlsx'
      writer = pd.ExcelWriter(f'{newName}',engine='xlsxwriter')
      basics.to_excel(writer,sheet_name=f"Changed {dt.date.today()}")
      portfolio.to_excel(writer,sheet_name='Operation Change')
      previous.to_excel(writer,sheet_name='Previous Composition')
      writer.save()
      clients.TimeStamp.values[i] = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
      # Reset Status to 0 as there any changes pending to do
      clients.Status.values[i] = 0
      clients.Change.values[i] = 0

      # Reset Risk
    elif clients.Status.values[i] == 3:
      # Update risk levels by resetting Component-Value-at-Risk
      # All process to gather Component-Value-at-Risk and apply it to current prices
      holdings = pd.read_excel(excel.Path.values[i])
      previous = holdings.copy()
      path = str(clients['Path'][i])
      oldcapital = str(clients.Path[i].split()[-3])
      action = 'Reset'
      portfolio = pd.DataFrame(index=holdings.iloc[:,0]) 
      info = data.copy()
      update = pd.DataFrame(info[f'{portfolio.index[0]}'].values,columns=[f'{portfolio.index.values[0]}'],index=info.index)
      for j in range(1, len(portfolio)):
          update[f'{portfolio.index.values[j]}'] = info[f'{portfolio.index[j]}'].values
      returns = update.pct_change()
      correlation = returns.corr() # correlation
      covariance = returns.cov()  # covariance
      instruments = pd.DataFrame(index= update.columns)
      sample = np.random.random_sample(size=(len(update.columns),1)) + (1.0 / len(data.columns))
      sample /= np.sum(sample)
      instruments['weights'] = sample # secure allocation is equal 1
      instruments['deltas'] = (instruments.weights * correlation).sum() # deltas as elasticity of the assets
      instruments['Stdev'] = returns.std()
      instruments['stress'] = (instruments.deltas * instruments.Stdev) * 3 # stress applied at 4 deviations
      instruments['portfolio_stress'] = instruments.stress.sum() # the stress of the portfolio
      risk = pd.DataFrame(index=update.columns)
      risk['numerator'] = (instruments.deltas.multiply(covariance)).sum()
      risk['denominator'] = update.pct_change().std() * (-2.365)
      risk['GradVaR'] = -risk.numerator / risk.denominator
      risk['CVaRj'] = risk.GradVaR * instruments.deltas # Component VaR of the Risk Factors j
      risk['thetai'] = (risk.CVaRj * correlation).sum() # Theta i of the instruments
      risk['CVaRi'] = risk.thetai * (1/len(update.columns)) # Component VaR of the Instruments i
      risk['totalCVaRi'] = risk.CVaRi.sum() #total CVaR of the portfolio
      risk['CVaRattribution'] = risk.CVaRi / risk.totalCVaRi # risk allocation by instrument in the portfolio
      riskadj = pd.DataFrame(index=update.columns)
      riskadj['base'] = instruments['weights'].values
      riskadj['CVaRattribution'] = risk.CVaRattribution.sort_values(axis=0,ascending=False)
      riskadj['new'] = holdings['weights'].values  # Choosing the option with the highest return
      riskadj['condition'] = (riskadj.base / riskadj.CVaRattribution)
      riskadj['newrisk'] = (riskadj.new / riskadj.CVaRattribution)
      riskadj['differences'] = (riskadj.newrisk - riskadj.condition)  # apply this result as a percentage to multiply new weights
      riskadj['adjustments'] = (riskadj.newrisk - riskadj.condition) / riskadj.condition #ALARM if its negative sum up the difference, 
                                                  #if it is positive rest it, you need to have 0
      riskadj['suggested'] = riskadj.new * (1 + riskadj.adjustments)   
      riskadj['tototal'] = riskadj.suggested.sum()
      riskadj['MinCVaR'] = riskadj.suggested / riskadj.tototal
      riskadj[riskadj.MinCVaR>= 0.12] = 0.12
      riskadj['MinCVaR'] = riskadj['MinCVaR'] / sum(riskadj['MinCVaR'])
      portfolio = pd.DataFrame(index=holdings.iloc[:,0]) # rewrite
      portfolio['nominal'] = holdings['nominal'].values
      portfolio['pricePaid'] = holdings['price'].values
      portfolio['weights'] = riskadj.MinCVaR.values 
      portfolio['notionalStart'] = sum(portfolio['nominal'] * portfolio['pricePaid'])
      portfolio['oldLiquidity'] = holdings['liquid'].values
      portfolio['priceToday'] = update.tail(1).T.values
      portfolio['notionalToday'] = sum(portfolio['priceToday'] * portfolio['nominal'])
      portfolio['PnLpercent'] = portfolio['notionalToday'] / portfolio['notionalStart']
      portfolio['PnLpercentEach'] = portfolio['priceToday'] / portfolio['pricePaid']
      portfolio['nominalNew'] = ((portfolio['weights'] * (portfolio['notionalToday'] + portfolio['oldLiquidity'])) // portfolio['priceToday']) # nuevo nominal
      portfolio['adjust'] = portfolio['nominalNew'] - portfolio['nominal'] # ajuste nominal
      portfolio['percentReb'] = (portfolio['nominalNew'] * portfolio['priceToday']) / sum(portfolio['nominalNew'] * portfolio['priceToday'])
      # Columnas vinculantes para conectar mes anterior con el proximo ya armado
      portfolio['notionalRebalance'] = sum(portfolio['nominalNew'] * portfolio['priceToday'])
      portfolio['liquidityToReinvest'] =  (portfolio['notionalToday'] + portfolio['oldLiquidity']) - portfolio['notionalRebalance']
      capital = str(int(portfolio.notionalToday.values[0] + portfolio.liquidityToReinvest.values[0]))
      basics = portfolio.copy()
      basics = tracker.BacktoBasics(basics)
      folder, operations = os.makedirs('Oldportfolios',exist_ok=True), os.makedirs('Update',exist_ok=True)
      name = path
      older, newer = path.replace('./DATABASE/','./Oldportfolios/'), path.replace('./DATABASE/',f'./Update/{action} {oldcapital} ')
      shutil.move(f'{name}',f'{older}')
      newName = ' '.join(newer.split()[:-1])
      newName = newName.split()
      newName[-2] = str(capital)
      # Change RISKUPDATED to the end
      newName = ' '.join(newName) + ' ' + str(dt.date.today()) + '.xlsx'
      writer = pd.ExcelWriter(f'{newName}',engine='xlsxwriter')
      basics.to_excel(writer,sheet_name=f"Risk {dt.date.today()}")
      portfolio.to_excel(writer,sheet_name='Risk Updated')
      previous.to_excel(writer,sheet_name='Previous Composition')
      writer.save()
      clients.TimeStamp.values[i] = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
      # Reset Status to 0 as there any changes pending to do
      clients.Status.values[i] = 0
      clients.Change.values[i] = 0


# Remove unnecessary & repeated columns 
to_delete = list(filter(lambda i: (i[0:3] == 'Unn'),clients.columns.to_list()))

for i in range(len(to_delete)):
    if to_delete[i] in clients.columns.to_list():
        del clients[f'{to_delete[i]}']

writer = pd.ExcelWriter('scanner.xlsx',engine='xlsxwriter')
clients.to_excel(writer)
writer.save()
