from packages import *
os.system("python maintainer_report.py") # re-assurance to know it runs script

xlsx = pd.read_excel('./maintain.xlsx')
clients = xlsx

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
  holdings = pd.read_excel(xlsx.Path.values[i])
  name, action, capital, oldcapital, change = xlsx.Name[i], xlsx.Action[i],int(xlsx.Capital[i]),int(xlsx.oldCapital[i]), xlsx.Change[i]
  withdraw = ''
  if action == 'Change': # Change Status
    action = 'Cambio'
    withdraw = int(xlsx.Change[i])
    withdraw = '${:,.2f}'.format(withdraw).replace('.','p').replace(',','.').replace('p',',')

  portfolio = pd.DataFrame(index=holdings.iloc[:,0]) # rewrite
  portfolio = holdings.iloc[:,5:-2].copy()
  portfolio.index = holdings.iloc[:,0].to_list()
  portfolio['nominal'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['nominal'].astype(float)).values)]
  portfolio['invested'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['invested'].astype(float)).values)]
  portfolio['percentage'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['percentage'].astype(float)).values * 100.0)]
  change = '${:,.2f}'.format(change).replace('.','p').replace(',','.').replace('p',',')
  capital = '${:,.2f}'.format(capital).replace('.','p').replace(',','.').replace('p',',')
  oldcapital = '${:,.2f}'.format(oldcapital).replace('.','p').replace(',','.').replace('p',',')
  portfolio = portfolio.rename(columns={'nominal':'CANTIDAD','invested':'INVERTIDO','percentage':'PONDERACIÓN'})
  email = xlsx.Email[i]
  
  text = f"""<h1>Buenos dias {name}.</h1><br />"""
  optional = ''
  if withdraw != '':
    optional = ' Cambio de Capital por ' + f'{withdraw}'
  details = f"""<h3>Datos Inversión Cambiada:
                  <ul>
                    <li>Operación de {action}.{optional}</li>
                    <li>Monto de Inversión: {capital}. Anterior {oldcapital}</li>
                    <li>Change {change}</li>
                  </ul>
                </h3> """
              
  html_close = portfolio.to_html(na_rep = "").replace('<table','<table id="effect" style="width:70%; height:auto;"').replace('<th>','<th style = "background-color: rgb(60,179,113); color:black">')


  warning = """<h3>Tras esta decisión debemos estar pendientes a:</h3><br /> 
            <p>La tendencia del mercado y a las necesidades para operar para el monitoreo diario de la inversión.</p>"""
  signature = '<h2>Se adjunta excel con details completo y con propuesta de rebalanceo</h2>'
  html_file = style + highlight + text + details + html_close + warning + signature + end_html

  recipients = ['your@gmail.com', f'{clients.Email.values[i]}']

  # In order to save & test the actual template we are sending
  if i == 0:
     e = open('templateUpdate.html','w') 
     e.write(html_file)
     e.close()



  def sendEmail(html_file):
      msg = MIMEMultipart('alternative')
      msg['X-Priority'] = '1'
      msg['Subject'] = f"Actualización QUANVAS {name} {today}"
      msg['From'] = credentials.account
      msg['To'] = ",".join(recipients)
      # Large Excel 
      fp = open(f'{xlsx.Path.values[i]}', 'rb')
      parte = MIMEBase('application','vnd.ms-excel')
      parte.set_payload(fp.read())
      encoders.encode_base64(parte)
      parte.add_header('Content-Disposition', 'attachment', filename=f'Cuenta Actualizada {name}.xlsx')
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
      newname = f'{xlsx.NewName.values[i]}'
      os.rename(f'{xlsx.Path.values[i]}',f'{xlsx.NewName.values[i]}')
      todb = newname.replace('Update','DATABASE')
      shutil.move(f'{newname}',f'{todb}')


  e = sendEmail(html_file)
  print(f"{dt.datetime.now().strftime('%H:%M:%S:%f')} UPDATE to {name} SENT!!!")
  e

server.quit()
