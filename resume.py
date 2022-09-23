import pandas as pd, datetime as dt, numpy as np
import smtplib, re, os, ssl 
import credentials, glob 
import base64, shutil
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
import trackATM as tracker
from templateReport import * # template html of all content of the email
import yfinance as yahoo 

file = []

for filename in glob.iglob('./DATABASE/*'):
    file.append(filename)

excel = pd.DataFrame(file,columns=['Path'])

# create a common dataframe with all tickets, to avoid
# downloading tickets per each client

lista = []
for i in range(len(excel)):
    index = pd.read_excel(excel.Path.values[i])
    index = index.iloc[:,0].to_list()
    lista += index
    lista = list(dict.fromkeys(lista))

os.system("python scanner.py")
data = yahoo.download(lista,period="60d",interval="2m")["Adj Close"].fillna(method="ffill")
clients = pd.read_excel('./scanner.xlsx')
today = dt.date.today().strftime('%m-%d-%Y')

# iterate clients
# first grab the client & update data
# once updated, send the email
# First set the server
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
# login account + password
server.login(credentials.account,credentials.password)


for i in range(len(clients)):
  clients.Path.values[i] = str(clients.Path.values[i])
  holdings = pd.read_excel(clients.Path.values[i])
  file_path, timestamp = str(clients.Path.values[i]), str(clients.Path.values[i]).split()[-1].split('.')[0]
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
  portfolio['liquidityToReinvest'] =  (portfolio['notionalToday'] + portfolio['oldLiquidity']) - portfolio['notionalRebalance']
  cliente = str(clients.Name.values[i])
  portfolio.to_excel(f'{cliente} Update {today}.excel')
  portfolio.index = portfolio.index.to_list()  
  pnl = portfolio.PnLpercent.values[0].copy()
  portfolio = portfolio[portfolio.nominal!=0.0].dropna()
  portfolio['nominal'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['nominal'].astype(float)).values)]
  portfolio['pricePaid'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['pricePaid'].astype(float)).values)]
  portfolio['weights'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['weights'].astype(float)).values * 100.0)]
  portfolio['notionalStart'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['notionalStart'].astype(float)).values)]    
  portfolio['oldLiquidity'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['oldLiquidity'].astype(float)).values)]
  portfolio['priceToday'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['priceToday'].astype(float)).values)]
  portfolio['notionalToday'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['notionalToday'].astype(float)).values)]    
  portfolio['PnLpercent'], portfolio['PnLpercentEach'] = portfolio['PnLpercent'] - 1.0, portfolio['PnLpercentEach'] - 1.0
  portfolio['PnLpercent'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['PnLpercent'].astype(float)).values * 100.0)]
  portfolio['PnLpercentEach'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['PnLpercentEach'].astype(float)).values * 100.0)]
  portfolio['nominalNew'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['nominalNew'].astype(float)).values)]
  portfolio['adjust'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['adjust'].astype(float)).values)]
  portfolio['percentReb'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['percentReb'].astype(float)).values * 100.0)]
  portfolio['notionalRebalance'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['notionalRebalance'].astype(float)).values)]
  portfolio['liquidityToReinvest'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['liquidityToReinvest'].astype(float)).values)]
  oldNotional = portfolio.notionalStart.values[0]
  newNotional = portfolio.notionalToday.values[0]
  oldLiquidity = portfolio.oldLiquidity.values[0]
  portfolio = portfolio.drop(['notionalStart','notionalToday','oldLiquidity','PnLpercent','nominalNew',\
          'adjust','percentReb','notionalRebalance','liquidityToReinvest'],axis=1)
  portfolio = portfolio.rename(columns={'nominal':'Quantity','pricePaid':'Price Paid','weights':'Weights','priceToday':'Price Today','PnLpercentEach':'PnL Each'})


  text = f"""<h1>Brief resume of account {cliente} {today}.</h1><h3>Current state given the performance and composition simplified.<br /></h3>"""
  details = f"""<h3>
              <ul>
                <li>Accumulated return: {round((pnl * 100)-100,2)}%.</li>
                <li>Value today {newNotional} versus initial value {oldNotional}.</li>
                <li>Remaining liquidity to reinvest: {oldLiquidity}.</li>
                <li>Date of last change: {timestamp}.</li>
              </ul></h3>
              <br />"""
  html_close = portfolio.to_html(na_rep = "").replace('<table','<table id="effect" style="width:50%; height:auto;"').replace('<th>','<th style = "background-color: rgb(60,179,113); color:black">')


  warning = """<h3>Actions to consider:<br/>
                <ul>
                    <li>Update Porfolio: by rebalance weigths.</li>
                    <li>Change amount invested by withdraw or deposit.</li>
                    <li>Reset risk level.</li>
                </ul></h3>"""
  warning += """<h3>Factors to keep an eye on:<br /> 
            <p>Market Tendency. Considering technichal anaylis, fundamental view or a certain event..<br />Liquidity needs.</p>
        </ul></h3>"""
  signature = '<p>We hope this brief keep you updated.<br /></p><p>Without nothing more, welcome to QUANVAS.</p>'
  signature += '<h1>An excel file is attached to view the whole recommendation.</h1>'
  html_file = style + highlight + text + details + html_close + warning + signature + end_html
  
  # In order to save & test the actual template we are sending
  if i == 0:
     e = open('template.html','w') 
     e.write(html_file)
     e.close()

  #recipients = ['your@gmail.com']#, f'{clients.Email.values[i]}']
  recipients = [f'{clients.Email.values[i]}']

  def sendEmail(html_file):
      msg = MIMEMultipart('alternative')
      msg['X-Priority'] = '1'
      msg['Subject'] = f"QUANVAS Account Brief {cliente} {today}"
      msg['From'] = credentials.account
      msg['To'] = ",".join(recipients)
      # Large Excel 
      fp = open(f'{cliente} Update {today}.excel', 'rb')
      parte = MIMEBase('application','vnd.ms-excel')
      parte.set_payload(fp.read())
      encoders.encode_base64(parte)
      parte.add_header('Content-Disposition', 'attachment', filename=f'Resumen Cuenta {cliente}.excel')
      msg.attach(parte)
      part1 = html_file
      part1 = MIMEText(part1, 'html')
      msg.attach(part1)
      part1 = html_file
      part1 = MIMEText(part1, 'html')
      msg.attach(part1)
      server.sendmail(credentials.account,
                    recipients,
                    msg.as_string())


  e = sendEmail(html_file)
  os.remove(f'{cliente} Update {today}.excel')
  print(f"{dt.datetime.now().strftime('%H:%M:%S:%f')} Portfolio to {cliente} {file_path} SENT!!!")
  e

server.quit()
