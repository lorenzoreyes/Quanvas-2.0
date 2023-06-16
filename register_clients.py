from packages import *
# needed fields to fill a form of a new client as a dict
# fields = Names	Emails	Money	Markets	(=>Symbol)	risk (=>Optimization)
# Symbol is giben by the Market, and Optimization by risk too

print("Register Clients to generate portfolios according their specs\n\n\n".center(60,'+'))
client_form = {'Names':[],'Emails':[],'Markets':[],'Symbol':[],'Money':[],'Risk':[]}

markets = {'1':'GSPC','2':'FTSE','3':'CEDEARS','4':'NIKKEI','5':'BOVESPA',\
           '6':'CANADA','7':'AUSTRALIA','8':'SHANGHAI', '9':'CRYPTO','10':'MERVAL'}

def register_client():
    client_form['Names'].append(input('type the Name\n\n\t\t'))
    client_form['Emails'].append(input('Email to contact\n\n\t\t'))
    mercado = (input("Type the market to operate:\n(1) SP500,\n(2) FTSE,\n(3) CEDEARS,\n(4) NIKKEI,\n (5) BOVESPA,\
        \n(6) CANADA,\n(7) AUSTRALIA,\n(8) Shanghai,\n(9) CRYPTO,\n(10) MERVAL.\n\n\t\t"))
    client_form['Markets'].append(int(mercado)-1)
    client_form['Symbol'].append(markets[f"{mercado}"])
    client_form['Money'].append(input('How much to invest?\n\n\t\t'))                             
    risk = (input('(1) MinVar,\n(2) SharpeRatio,\n(3) MonteVaR,\n(4) Monte_Sharpe\n\n\t\t'))
    client_form['Risk'].append(risk.replace('1','MinVaR').replace('2','SharpeRatio').replace('3','MonteVaR').replace('4','SharpeBound'))
    client_form['Path'] = client_form['Symbol'] + ' ' +  client_form['Name'] + ' ' + client_form['Emails'] + ' ' + client_form['Money'] + ' ' + str(dt.date.today()) + 'xlsx'
    return client_form
                             

def create():
    action = input("type [Enter] to add a client or else to exit\n\n\t\t")
    if action == '':
        add = register_client()
        create()
    else:
        print('Finished clients registration')
    return client_form   

if __name__ == '__main__':
    create()
    client_form = pd.DataFrame(list(client_form.values()),index=list(client_form.keys())).T
    writer = pd.ExcelWriter('new_clients.xlsx',engine='xlsxwriter')
    client_form.to_excel(writer)
    writer.close()
