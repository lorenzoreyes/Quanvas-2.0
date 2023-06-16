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
excel['Optimization'] = [i.split()[5] for i in excel.Path.to_list()]
excel['Status'] = 0
excel['Change'] = 0
excel['TimeStamp'] = dt.datetime.today().strftime('%H:%M:%S %d-%m-%Y')
excel.index = range(len(excel))

writer = pd.ExcelWriter('NewOnes.xlsx',engine='xlsxwriter')
excel.to_excel(writer)
writer.close()
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
  portfolio = pd.DataFrame(index=holdings.iloc[:,0]) 
  portfolio = holdings.iloc[:,5:-2].copy()
  portfolio.index = holdings.iloc[:,0].to_list()
  capital, investment, liquidity, risk = holdings.capital[0].copy(), holdings.total[0].copy(),holdings.liquid[0].copy(),excel.Path[i].split()[-2]
  portfolio['nominal'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['nominal'].astype(float)).values)]
  portfolio['invested'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['invested'].astype(float)).values)]
  portfolio['percentage'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['percentage'].astype(float)).values * 100.0)]
  investment = '${:,.2f}'.format(investment).replace('.','p').replace(',','.').replace('p',',')
  capital = '${:,.2f}'.format(capital).replace('.','p').replace(',','.').replace('p',',')
  liquidity = '${:,.2f}'.format(liquidity).replace('.','p').replace(',','.').replace('p',',')
  
  portfolio = portfolio.rename(columns={'nominal':'CANTIDAD','invested':'INVERTIDO','percentage':'PONDERACIÓN'})
  cliente = excel.Path[i].split()[1] + ' ' + excel.Path[i].split()[2]
  limite = excel.Path[i].split().index([i for i in excel.Path[i].split() if '@' in i][0])
  name = ' '.join(excel.Path[i].split()[1:limite])
  email = [i for i in excel.Path[i].split() if '@' in i][0]
  
  text = f"""<h1>Gracias {name} por haber asistido a la FLISOL de la ScrollArmy 22 de Abril Pergamino.</h1><br /><h3>Como evento se busca promocionar el software libre, enseñar Linux y demostrar
  su uso en otros campos. En el caso de la charla de Python y Finanzas se ilustra el uso del lenguaje para todo el proceso de tareas de finanzas como Crear, Leer, Modificar y Eliminar (CRUD) una inversión con solo clicks.
  Siguiente evento MetaData Septiembre, el agro y mundo tech en un solo lugar Pergamino.<br /></h3>"""
  details = f"""<h3>Redes de todos los gustos:
              <ul>
                <li><a target='_blank' href='https://lorenzoreyes.dev'>Página Personal</a> todos los servicios.</li>
                <li><a target='_blank' href='https://www.twitch.tv/2pesos_lorenzoreyes'>Twitch</a>, sesiones live-coding y varieté.</li>
                <li><a target='_blank' href='https://www.youtube.com/channel/UCU6-WSlGv3hMsvsH8aFn0BQ'>Youtube</a> videos de paso a paso del libro.</li>
                <li><a target='_blank' href='https://www.facebook.com/groups/1385919778888014'>Facebook</a>, el lugar del chisme.</li>
                <li><a target='_blank' href='https://twitter.com/lorenzoreyes_x'>Twitter</a>, la red donde esta el hate.</li>
                <li><a target='_blank' href='https://discord.gg/gQUsFDcS'>Discord</a>, chat de la comunidad.</li>
                <li><a target='_blank' href='https://github.com/lorenzoreyes/Finanzas.py'>Github</a>, libro y codigo del paso a paso.</li>
              </ul></h3> """

  details +=  f"""<h3>A la fecha de {today} se ha creado la siguiente recomendación en base al mercado que desea operar y acorde a su perfil de riesgo.<br /></h3>"""
        
  details += f"""<h3>Datos de su inversión:
              <ul>
                <li>Monto de Inversión: {capital}.</li>
                <li>Perfil de Riesgo: {risk}.</li>
                <li>Riesgos de 1 a 4 de Conservador a más Agresivo (MinVar, Sharpe, Monte_VaR, Monte_Sharpe).</li>
                <li>INVERTIDO: {investment}.</li>
                <li>Liquidez remanente para reinvertir: {liquidity}.</li>
                <li>Tenencia en Oro (PAXG-USD) es a fines de cobertura.</li>
              </ul></h3> """
              
  html_close = portfolio.to_html(na_rep = "").replace('<table','<table id="effect" style="width:70%; height:auto;"').replace('<th>','<th style = "background-color: rgb(60,179,113); color:black">')

  warning = """<h3>ACCIONES A CONSIDERAR:<br/>
                <ul>
                    <li>Actualizar Cartera: una vez por mes.</li>
                    <li>Cambiar Monto invertido: ya sea por preferencia o necesidad de liquidez.</li>
                    <li>Resetear nivel de riesgo: en busca de un rebalanceo para minimizar el riesgo.</li>
                </ul></h3>"""
  warning += """<h3>Factores a estar atentos:<br /> 
            <p>Tendencia del mercado. Ya sea por análisis técnico, fundamental o evento a esperar.<br />Necesidad de liquidez para terminar posiciones.</p>
        </ul></h3>"""
  signature = '<p>Esperamos que esta minuta lo mantenga informado.<br /></p><p>Sin más saludamos, equipo <a href="https://scrollarmy.com.ar">ScrollArmy</a></p>'
  signature += '<h1>Se adjunta excel con details completo y con propuesta de rebalanceo</h1>'
  html_file = style + highlight + text + details + html_close + warning + signature + end_html

  recipients = ['lreyes@udesa.edu.ar', email]
  # In order to save & test the actual template we are sending
  if i == 0:
      e = open(f'template.html','w') 
      e.write(html_file)
      e.close()


  def sendEmail(html_file):
      msg = MIMEMultipart('alternative')
      msg['X-Priority'] = '1'
      msg['Subject'] = f"FLISOL ScrollArmy {name} {today}"
      msg['From'] = credentials.account
      msg['To'] = ",".join(recipients)
      # Large Excel 
      fp = open(f'{excel.Path.values[i]}', 'rb')
      parte = MIMEBase('application','vnd.ms-excel')
      parte.set_payload(fp.read())
      encoders.encode_base64(parte)
      parte.add_header('Content-Disposition', 'attachment', filename=f'Resumen Cuenta {name}.xlsx')
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
      rename = f'{excel.Path.values[i]}'
      todb = rename.replace('NewOnes','DATABASE')
      os.rename(f'{rename}',f'{todb}')


  e = sendEmail(html_file)
  print(f"{dt.datetime.now().strftime('%H:%M:%S:%f')} Portfolio to {name} SENT!!!")
  e

server.quit()
