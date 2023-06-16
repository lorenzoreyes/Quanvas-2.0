from packages import *
fake = Faker()

number = int(input('Number of fake clients to backtest?\t\t\n\n'))


mercados = ['GSPC','FTSE','NIKKEI','BOVESPA','CANADA','AUSTRALIA','Shanghai','Crypto']

markets = []
for _ in range(number):
    markets.append(mercados[random.randrange(0,8,1)])
    
#  Pass it as a DataFrame
clients = pd.DataFrame(markets,columns=['Markets'],index=range(len(markets)))
    
names = []
for _ in range(number):
    names.append(fake.name())
    
clients['Names'] = names    
clients['Emails'] = ([i + '@gmail.com' for i in [i.replace(' ','') for i in names]])
money = []
for _ in range(len(clients)):
    money.append(random.randrange(100000,100000000,1))

clients['Money'] = money

#str(input("Choose Optimization\n1 SharpeRatio\n2 MonteVaR\n3 Monte_Sharpe\n4 MinVaR\nOther option is the winner\nMake your choice: "))
risks = ['SharpeRatio','MonteVaR','Monte_Sharpe','MinVaR']    

optimization = []
for _ in range(len(clients)):
    optimization.append(risks[random.randrange(0,4,1)])

clients['Optimization'] = optimization

# This two columns are to settle status to read, update, or change
status = []
for _ in range(len(clients)):
    status.append(random.randrange(0,4,1))

clients['Status'] = status

change = []
for i in range(len(clients)):
    if clients.Status.values[i] != 2:
        change.append(0)
    else:
        change.append(random.randrange(-10000000,100000000,1))


clients['Change'] = change

# timestamp last modification made
clients['TimeStamp'] = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')


writer = pd.ExcelWriter('clients.xlsx',engine='xlsxwriter')
clients.to_excel(writer)
writer.close()
