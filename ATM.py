from packages import *
import trackATM as tracker
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')
pd.options.display.float_format = '{:,.2f}'.format
# We want to iterate excels, perform a task and save changes
# designed in TrackUpdate.py Grab an input int
# of excel to perform task (monitor, update, withdraw, etc)
# from the command line.

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
        portfolio_name()

    lista = [order,data, path, client, name]
    return lista

def portfolio_operation():
    lista = portfolio_name()
    order, data, path, client, name = lista
    print(f"What task do you want to do to {client[f'{name} Portfolios'][order]} ?:\n(1) Monitor Portfolio? To watch performance.\n(2) Do a Deposit or Withdraw? Specify the ammount of capital to change.\n(3) Update risk? By adding new information.\n\n")
    choice = input("Type your Task: ...  ")
    if choice == '1':
        data, operation = tracker.PortfolioMonitor(data), 'Update'
    elif choice == '2':
        amount = int(input("How much you want to change?\n\n"))
        data, operation = tracker.DepositOrWithdraw(data,amount), 'Change'
    elif choice == '3':
        data, operation = tracker.portfolioRiskUpdated(data), 'Reset'

    lista = [data,f'{client[f"{name} Portfolios"][order]}',order, operation]
    return lista # data saved as a list because we can track name of the client to further save

# 3. Print it out. Make a decisition, (a) save and do something else, (b) don't save and do something else or (c) quit.
def operation():
  choice = portfolio_operation() # call function
  excel, name, request, transchoice = choice
  print(excel[['pricePaid','priceToday','PnLpercentEach']])
  print(f"Accumulated Return of\n{name} is\n[{excel.PnLpercent.values[0] - 1 :.4%}]\t [$ {round(excel.notionalToday.values[0] + excel.oldLiquidity.values[0],2)}]".center(50,'_'))
  question = (input("What you want to do? \n(1) Save and do something else, \n(2) Don't save, do something else \nOr (3) Quit.\n\nDecide:  "))
  if question == '1':
      basics = excel.copy()
      folder = os.makedirs('Oldportfolios',exist_ok=True)
      old = name.replace('./DATABASE/','./Oldportfolios/')
      shutil.move(f'{name}',f'{old}')
      basics = tracker.BacktoBasics(basics)
      newCapital = str(int(basics.total.values[0] + basics.liquid.values[0]))
      oldCapital = ''.join(name.split('/')[-1].split()[-3])
      filename = ' '.join(name.split('/')[-1].split()[:-3]) + ' ' + newCapital + ' ' + ' '.join(name.split('/')[-1].split()[-2].split())
      sheet = filename + ' ' + str(dt.date.today())
      new = os.makedirs('Update',exist_ok=True)
      path = './Update/' + transchoice + ' ' + oldCapital + ' ' + sheet
      writer = pd.ExcelWriter(f'{path}.xlsx', engine='xlsxwriter')
      basics.to_excel(writer, sheet_name=str(dt.date.today()))
      excel.to_excel(writer,sheet_name='change made, old New')
      writer.save()
      operation()
  elif question == '2':
      operation()
  elif type(question) != ('1' or '2'):
      print("See ya next time buddy")

# final iterator of eternal loop. Save recommendation, do another operation or leave.
if __name__ =='__main__':
  operation()

