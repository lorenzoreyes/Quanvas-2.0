import pyRofex, os
import urllib.request
import pandas as pd
import datetime as dt 
import yfinance as yahoo
import matplotlib.pyplot as plt 
from pylab import mpl
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')

today = dt.date.today()
end = dt.date.today()
start = end - dt.timedelta(365) 

# trigger update for Central Bank excel
os.system("python bcra.py")

reservas = pd.read_excel('seriese.xlsx',sheet_name='RESERVAS')

# Sheet Reservas
reservas = reservas.iloc[8:,:]
reservas = pd.DataFrame(reservas.iloc[:,-2].values,columns=['Spot'],index=reservas.iloc[:,0].values)

# initialize API Connection Educational Account
pyRofex.initialize(user="MD_REYES",
                   password="Lorenzo6+",
                   account="88406W",
                   environment=pyRofex.Environment.LIVE)

# make a list of all available month from current to 12 forwards
hoy = dt.date.today() - dt.timedelta(365)
fechas = list(pd.date_range(hoy,end+dt.timedelta(300),freq='M'))

# create proper tickets as a dictionary       
# format 'Currency/MONTH/YEAR' => Dollar Future August 2022 => DLR/AGO22
meses = {1:'ENE',2:'FEB',3:'MAR',4:'ABR',5:'MAY',6:'JUN',7:'JUL',8:'AGO',9:'SEP',10:'OCT',11:'NOV',12:'DIC'}
str(hoy.year)[-2:]
tickets = []
for i in range(len(fechas)):
  tickets.append('DLR/' + meses[(fechas[i]).month] + str((fechas[i]).year)[-2:])

# iterate the download
futuros = tickets.copy()

response = pyRofex.get_all_instruments()

for inst in response['instruments']:
    futuros.append(inst['instrumentId']['symbol'])

for i in range(len(tickets)):
    print(f'Is {tickets[i]} a valid instrument? {tickets[i] in futuros}')
    

for i in range(len(tickets)):
    historic_trades = pyRofex.get_trade_history(tickets[i], start_date=start, end_date=end)
    trades = pd.DataFrame(historic_trades['trades']) # get dataframe from trades dictionary
    asset = pd.DataFrame(trades.price.values,columns=[f'{tickets[i]}'],index=trades.datetime)    
    asset.index = [dt.datetime.strptime(i,('%Y-%m-%d %H:%M:%S.%f')) for i in asset.index.to_list()]
    #asset = asset.groupby([asset.index.year,asset.index.month,asset.index.day,asset.index.hour,asset.index.minute]).mean()
    futuros[i] = asset

# concatenate all dataframes and sort index so no information get deleted
#dolar = pd.concat([futuros[0],futuros[1],futuros[2],futuros[3],futuros[4],futuros[5],futuros[6],futuros[7],futuros[8],futuros[9],futuros[10],futuros[11],futuros[12],futuros[13],futuros[14],futuros[15],futuros[16],futuros[17],futuros[18],futuros[19],futuros[20],futuros[21]]).sort_index()

dolar = pd.concat([futuros[0],futuros[1]]).sort_index()

for i in range(2,len(tickets)):
    dolar = pd.concat([dolar,futuros[i]]).sort_index()

#dolar = dolar.fillna(method='bfill')    

# download USD/ARS spot from Rofex CEM (Only available via web)
spot = reservas

#spot.index = indice
spot = spot.loc[f'{dolar.index[0]}':].dropna()

dolar = pd.concat([spot,dolar]).sort_index()
dolar['Spot'] = dolar['Spot'].fillna(method='bfill').fillna(method='ffill')
dolar[dolar.columns[1:-10]] = dolar[dolar.columns[1:-10]].fillna(method='bfill')
dolar.iloc[:,-10:] = dolar.iloc[:,-10:].fillna(method='ffill')
cable = pd.read_excel(f'Central Bank Report {today}.xlsx')
cable.index = cable['Unnamed: 0'].to_list()
cable = cable.loc[f'{dolar.index[0]}':]

dolar = dolar.join(cable['Cable Apple'])

dolar['Cable Apple'] = dolar['Cable Apple'].fillna(method='bfill').fillna(method='ffill')
order = [dolar.columns.to_list()[-1]]+dolar.columns.to_list()[:-1]
dolar = dolar[order]

cierre = dolar.fillna(method='ffill').copy()
columnas = []
for i in range(len(cierre.columns)):
    columnas.append(str(cierre.columns[i]) + ' $' + str(round(cierre.fillna(method='ffill').iloc[-1,i],2)))
    
cierre = dolar.copy()
cierre.columns = columnas
cierre.index = [str(i)[:10] for i in cierre.index.to_list()]
# close
fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
cierre.iloc[:,0:2].plot(ax=ax1, lw=9.,color='k')
cierre.iloc[:,2:].plot(ax=ax1, lw=5)
ax1.set_title('Dollar, Spot & Futures Series', fontsize=150, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=3)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=40)
plt.xticks(size=50)
plt.yticks(size=60)
plt.savefig('SpotnFutures.png',bbox_inches='tight')
# return
cierre = dolar.pct_change().cumsum().fillna(method='ffill').copy() * 100.0
columnas = []

for i in range(len(cierre.columns)):
    columnas.append(str(cierre.columns[i]) + ' ' + str(round(cierre.iloc[-1,i],2)) + '%')

cierre.columns = columnas


cierre.columns = columnas
cierre.index = [str(i)[:10] for i in cierre.index.to_list()]

# cierre
fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
cierre.iloc[:,:2].plot(ax=ax1, lw=7., color='k')
cierre.iloc[:,2:].plot(ax=ax1, lw=7.)
ax1.set_title('Return of Spot & Futures', fontsize=150, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=40)
plt.xticks(size=50)
plt.yticks(size=60)
plt.savefig('futuresReturn.png',bbox_inches='tight')

# remaining days to calculate implied rate
caduca = []#.strftime('%Y-%m-%d')]
for i in range(22):
    caduca.append((pd.date_range((dt.date.today()-dt.timedelta(365)).strftime('%Y-%m-%d'),periods=22,freq='BM')[i]))
    
vida = pd.DataFrame(0,columns=caduca,index=cierre.index)
vida.index = [pd.Timestamp(i) for i in vida.index.to_list()]

# Tasa Implícita
tasa_implicita = pd.DataFrame(0,columns=dolar.columns[2:],index=vida.index)
# 1- (Future/Spot)-1    2- X (365 / days_pending)
for i in range(len(tasa_implicita.columns)):
    tasa_implicita[f'{tasa_implicita.columns[i]}'] = ((dolar.iloc[:,i+2].values/ dolar.iloc[:,1].values) -1)
    tasa_implicita[f'{tasa_implicita.columns[i]}'] =  (tasa_implicita[f'{tasa_implicita.columns[i]}'] * (365 / ((vida.columns[i] - vida.index).days).values)).values
    #tasa_implicita[f'{tasa_implicita.columns[i]}'] =  (tasa_implicita[f'{tasa_implicita.columns[i]}'] * (365 / vida.iloc[:,i].values)).values

tasa_implicita = tasa_implicita.sort_index(axis=0,ascending=True)

tea = pd.DataFrame(0,columns=dolar.columns[2:],index=vida.index)

for i in range(len(tea.columns)):
    tea[f'{tea.columns[i]}'] = ((1 + (((tasa_implicita.iloc[:,i].values)) * ((vida.columns[i] - vida.index).days).values) / 365)) ** (365 / (vida.columns[i] - vida.index).days) - 1.0
    
tea = tea.sort_index(axis=0,ascending=True)
tea[tea<0]= None
fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
tea.plot(ax=ax1, lw=4.)
ax1.set_title('Effective Annual Rate', fontsize=150, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=40)
plt.xticks(size=50)
plt.yticks(size=60)
plt.savefig('tea.png',bbox_inches='tight')



tna30 = pd.DataFrame(0,columns=dolar.columns[2:],index=vida.index)
for i in range(len(tna30.columns)):
    tna30[f'{tna30.columns[i]}'] = ((1 + tea.iloc[:,i].values) ** (1 / 12) - 1) * 12

tna30 = tna30.sort_index(axis=0,ascending=True)
tna30[tna30<0] = None
fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
tea.plot(ax=ax1, lw=4.)
ax1.set_title('Monthly Rate', fontsize=150, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=40)
plt.xticks(size=50)
plt.yticks(size=60)
plt.savefig('tna30.png',bbox_inches='tight')



tasa = tasa_implicita.copy() * 100.0
columnas = []
for i in range(len(tasa.columns)):
    if i < 12:
        columnas.append(str(tasa.columns[i]))
    else:
        columnas.append(str(tasa.columns[i]) + ' ' + str(round(tasa.iloc[-1,i],2)) + '%')


tasa.columns = columnas
tasa[tasa<0] = None
# cierre
fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
tasa.iloc[:,0].plot(ax=ax1, lw=7., color='k')
tasa.iloc[:,1:].plot(ax=ax1, lw=5.)
ax1.set_title('Implied Rate', fontsize=150, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=40)
plt.xticks(size=50)
plt.yticks(size=60)
plt.savefig('rateImpl.png',bbox_inches='tight')

monthly = dt.date.today() - dt.timedelta(30)
monthly5 = dt.date.today() - dt.timedelta(25)
monthly = monthly.strftime('%Y-%m-%d')
table = pd.DataFrame(dolar.tail(1).T.values,columns=['Close'],index=dolar.tail(1).T.index)
table['30 days'] = dolar.loc[f'{monthly}':f'{monthly5}'].mean().values
#table['Variación'] = table.iloc[:,0] - table.iloc[:,1]
table['Percent'] = ((table.iloc[:,0] - table.iloc[:,1]) - 1)
table['Impl. Rate'] = [None,None] + (tasa_implicita.iloc[-1,:].to_list())
table['Previous Impl. Rate'] = [None,None] + (tasa_implicita.loc[f'{monthly}':f'{monthly5}'].mean().to_list())
table['Effective Annual Rate'] = [None,None] + (tea.iloc[-1,:].to_list())
table['Impl. Rate 30d'] = [None,None] + (tna30.iloc[-1,:].to_list())
# SAVE table to inform futures scenario


writer = pd.ExcelWriter(f'ArgentinaForex {hoy}.xlsx',engine='xlsxwriter')
table.to_excel(writer,f'Dollar Futures {hoy}')
dolar.to_excel(writer,sheet_name='Spot & Futures')
tasa_implicita.to_excel(writer,sheet_name='Implied Rate')
tea.to_excel(writer, sheet_name='Annaul Eff. Rate')
tna30.to_excel(writer,sheet_name='Impl. R 30days')
writer.save()
