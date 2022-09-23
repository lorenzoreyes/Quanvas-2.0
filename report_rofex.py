import smtplib    
from contextlib import contextmanager
import pandas as pd, datetime as dt,numpy as np
import re, os, ssl
import credentials, glob 
import base64
from templateReport import * # template html of all content of the email
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
from argentinafx import *

today = dt.date.today().strftime('%Y-%m-%d')
xcel = excel.sort_index(axis=0,ascending=False)
indice = []
for i in range(len(excel)):
    indice.append(dt.datetime.strptime(excel.index[i],'%Y-%m-%d'))
    

excel.index = indice

excel = excel.groupby([excel.index.year,excel.index.month]).mean()
excel = excel.rename_axis(['year','month']).reset_index()
excel = excel.sort_index(axis=0,ascending=False)

indice = []
excel.month = excel.month.replace({1:'ENE',2:'FEB',3:'MAR',4:'ABR',5:'MAY',6:'JUN',7:'JUL',8:'AGO',9:'SEP',10:'OCT',11:'NOV',12:'DIC'})
for i in range(len(excel)):
    indice.append(str(excel.year.values[i]) + ' ' + str(excel.month.values[i]))
    
excel.index = indice
del excel['year']
del excel['month']    

excel['Cedears Rate'] = ['$ {:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((excel['Cedears Rate'].astype(float)).values)]
excel['ADRs Rate'] = ['$ {:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list(excel['ADRs Rate'].astype(float))]
excel['Dollar+Taxes'] = ['$ {:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list(excel['Dollar+Taxes'].astype(float))]

html_file = excel.to_html(na_rep = "").replace('<th>','<th  style="background-color:rgb(60,120,60); color:black">').replace('<table>','<table style="width:100%">')


# We assume that the image file is in the same directory that you run your Python script from
fp = open('/home/lorenzo/Quanvas/Exchanges.png', 'rb')
image1 = MIMEImage(fp.read())
fp.close()

# send especific email
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
# login account + password
server.login(credentials.account,credentials.password)

clients = pd.read_excel('/home/lorenzo/Quanvas/scanner.excel')
hoy = dt.date.today().strftime('%d-%m-%Y')
destinatarios = ['akirafierro@gmail.com'] #['your@gmail.com', f'{clients.Email.values[i]}']

preview = """<h2>El Estado del mercado cambiario argentino se describe bajo los siguientes indicadores.</h2>"""
preview += f"""<h3><ul>
                    <li>Cambio Dolar MEP:  {round(mep3R*100.0,2)}%    [MEP HOY    ${round(mep,2)}, 3 Meses Antes ${round(mep3,2)}].</li>
                    <li>Cambio Dolar ADR:  {round(adr3R*100.0,2)}%    [ADR HOY    ${round(adr,2)}, 3 Meses Antes ${round(adr3,2)}].</li>
                    <li>Cambio Dolar País: {round(dollar3R*100.0,2)}% [Dolar HOY$ ${round(dollar,2)}, 3 Meses Antes ${round(dollar3,2)}].</li>
                </ul></h3>"""

plotForex = f"""<img src="cid:Exchanges" style="width:80%; display: block; margin-left: auto; margin-right: auto;" loading="lazy">"""  

firma = """<h2>Esperamos que esta minuta lo mantenga informado.</h2>
            <h2>Sin más saludamos, equipo QUANVAS.</h2> """

tosend = preview + plotForex + firma

def sendEmails(message):
    msg = MIMEMultipart('alternative',text='URGENT!')
    msg['X-Priority'] = '1'
    msg['Subject'] = f"Quanvas Estado Cambiario Argentino {clients.Name[i]} {hoy}"
    msg['From'] = credentials.account
    msg['To'] = ",".join(destinatarios) 
    # body of the email
    part1 = message
    #part1 = _fix_eols(part1).encode('utf-8')
    part1 = MIMEText(part1, 'html')
    msg.attach(part1)
    ## Specify the  ID according to the img src in the HTML part
    image1.add_header('Content-ID', '<Exchanges>')
    msg.attach(image1)
    server.sendmail(credentials.account,
                    destinatarios,
                    msg.as_string())
    

for i in range(3):#(len(clients)):    
  morning = f'<h2>Buenos dias {clients.Name.values[i]}</h2>'

  message = style + highlight + morning + tosend + html_file + firma + end_html 

  e = sendEmails(message)
  print(f"{dt.datetime.now().strftime('%H:%M:%S:%f')} Quanvas Report {clients.Name.values[i]} at {clients.Email.values[i]} SENT!!!")
  e

server.close()
