from packages import *

fake = Faker()

number = int(input('Number of clients to generate?\n\n\t\t'))

# lets generate a random client excel info
names = []
for _ in range(number):
    names.append(fake.name())

#  Pass it as a DataFrame
clients = pd.DataFrame(names,columns=['Names'],index=range(len(names)))

clients['Emails'] = 'your@gmail.com' #([i + '@gmail.com' for i in [i.replace(' ','') for i in names]])

money = []
for _ in range(len(clients)):
    money.append(random.randrange(1000,100000000,1))

clients['Money'] = money

mercados = ['GSPC','FTSE','CEDEARS','NIKKEI','BOVESPA','CANADA','AUSTRALIA','SHANGHAI','CRYPTO','MERVAL']

clients['Markets'] = 8 

symbol = []
for i in range(len(clients)):
    symbol.append(mercados[clients.Markets[i]])

clients['Symbol'] = symbol

risks = ['SharpeRatio','MonteVaR','MonteSharpe','MinVaR']
optimization = []
for _ in range(len(clients)):
    optimization.append(risks[random.randrange(0,4,1)])

clients['Risk'] = optimization

path = []
for i in range(len(clients)):
    path.append(str(clients.Symbol.values[i]) + ' ' + clients['Names'].values[i] + ' ' + str(clients.Emails.values[i]) + ' ' + str(clients['Risk'].values[i]) + str(' ') + str(dt.date.today()) + '.xlsx')

clients['Path'] = path

writer = pd.ExcelWriter('new_clients.xlsx',engine='xlsxwriter')
clients.to_excel(writer)
writer.close()
