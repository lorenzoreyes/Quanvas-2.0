from packages import *

file = []

for filename in glob.iglob('./NewOnes/*'):
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

excel['Symbol'] = [i.split()[0][2:] for i in excel.Path.to_list()]
excel['Name'] = [' '.join(i.split()[1:3]) for i in excel.Path.to_list()]
excel['Email'] = [(i.split()[3]) for i in excel.Path.to_list()]
excel['Capital'] = [i.split()[4] for i in excel.Path.to_list()]
excel['Optimization'] = [i.split()[-2] for i in excel.Path.to_list()]
excel['Status'] = 0
excel['Change'] = 0
excel['TimeStamp'] = dt.datetime.today().strftime('%H:%M:%S %d-%m-%Y')
excel.index = range(len(excel))

writer = pd.ExcelWriter('NewOnes.xlsx',engine='xlsxwriter')
excel.to_excel(writer)
writer.save()
clients = excel

today = dt.date.today().strftime('%d-%m-%Y')

# iterate clients
# first grab the client & update data
# once updated, send the email
# First set the server
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
# login account + password
server.login(credentials.account,credentials.password)

for i in range(len(file)):
  holdings = pd.read_excel(excel.Path.values[i])
  portfolio = holdings.iloc[:,5:-2].copy()
  portfolio.index = holdings.iloc[:,0].to_list()
  capital, investment, liquidity, risk = holdings.capital[0].copy(), holdings.total[0].copy(),holdings.liquid[0].copy(),excel.Path[i].split()[-2]
  portfolio['nominal'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['nominal'].astype(float)).values)]
  portfolio['invested'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['invested'].astype(float)).values)]
  portfolio['percentage'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['percentage'].astype(float)).values * 100.0)]
  investment = '${:,.2f}'.format(investment).replace('.','p').replace(',','.').replace('p',',')
  capital = '${:,.2f}'.format(capital).replace('.','p').replace(',','.').replace('p',',')
  liquidity = '${:,.2f}'.format(liquidity).replace('.','p').replace(',','.').replace('p',',')

  portfolio = portfolio.rename(columns={'nominal':'Nominal','invested':'Invested','percentage':'Weight'})
  cliente = excel.Path[i].split()[1] + ' ' + excel.Path[i].split()[2]
  email = excel.Path[i].split()[3]

  text = f"""<h1>Welcome {cliente} to QUANVAS.</h1><br /><h3>At the current date {today} we had generated a portfolio recommendation based on your risk profile.<br /></h3>"""
  details = f"""<h3>Portfolio aspects:
              <ul>
                <li>Amount to invest: {capital}.</li>
                <li>Risk Profile: {risk}.</li>
                <li>Risk vary from 1 to 4, from more conservative to more agressive..Monte_VaR, Monte_Sharpe, MinVaR, Sharpe</li>
                <li>Effectively invested: {investment}.</li>
                <li>Liquidity remained to invest: {liquidity}.</li>
              </ul></h3> """

  html_close = portfolio.to_html(na_rep = "").replace('<table','<table id="effect" style="width:70%; height:auto;"').replace('<th>','<th style = "background-color: rgb(60,179,113); color:black">')

  warning = """<h3>Actions to consider:<br/>
                <ul>
                    <li>Update Porfolio: by rebalance weigths.</li>
                    <li>Change amount invested by withdraw or deposit.</li>
                    <li>Reset risk level.</li>
                </ul></h3>"""
  warning += """<h3>Factors to keep an eye on:<br />
            <p>Market Tendency. Considering technichal anaylis, fundamental view or a certain event..<br />Liquidity needs.</p>
        </ul></h3>"""
  signature = '<p>We hope this brief keep you updated.<br /></p><p>Without nothing more, welcome QUANVAS.</p>'
  signature += '<h1>An excel file is attached to view the whole recommendation.</h1>'
  html_file = style + highlight + text + details + html_close + warning + signature + end_html

  recipients = ['your@gmail.com', f'{clients.Email.values[i]}']

  # In order to save & test the actual template we are sending
  if i == 0:
      e = open(f'template.html','w')
      e.write(html_file)
      e.close()

  def sendEmail(html_file):
      msg = MIMEMultipart('alternative')
      msg['X-Priority'] = '1'
      msg['Subject'] = f"Welcome to QUANVAS {cliente} {today}"
      msg['From'] = credentials.account
      msg['To'] = ",".join(recipients)
      # Large Excel
      fp = open(f'{excel.Path.values[i]}', 'rb')
      parte = MIMEBase('application','vnd.ms-excel')
      parte.set_payload(fp.read())
      encoders.encode_base64(parte)
      parte.add_header('Content-Disposition', 'attachment', filename=f'Account Rec {cliente}.xlsx')
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
      name = f'{excel.Path.values[i]}'
      os.makedirs('DATABASE',exist_ok=True)
      todb = name.replace('NewOnes','DATABASE')
      os.rename(f'{name}',f'{todb}')


  e = sendEmail(html_file)
  print(f"{dt.datetime.now().strftime('%H:%M:%S:%f')} Portfolio to {cliente} SENT!!!")
  e

server.quit()
