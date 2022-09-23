import pandas as pd, datetime as dt
import smtplib, re, os 
import credentials, glob 
import base64, shutil
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
from templateReport import *
from scanner import *

### FROM THIS SCRIPT WE GATHER ALL DATA FOR THE REPORT
#from argentinafx import *

date = today = dt.date.today().strftime('%Y-%m-%d')

fp = open('./ArgentinaFX.png', 'rb')
image = MIMEImage(fp.read())
fp.close()

recipients = pd.read_excel('./scanner.xlsx')

for i in range(len(recipients)):
    memo = pd.read_excel(f'./Central Bank Report {today}.xlsx')
    memo.index = memo.iloc[:,0]
    memo = memo.iloc[:,-6:-1]

    memo = (memo.groupby([memo.index.year,memo.index.month,memo.index.day]).mean()).rename_axis(['year','month','day']).reset_index()
    memo = memo.sort_index(axis=0,ascending=False)
    memo.index = pd.to_datetime(memo[['year','month','day']]).dt.strftime('%Y-%m-%d')
    memo = memo.iloc[:,3:]
    memo.index = [dt.datetime.strptime(i,'%Y-%m-%d') for i in memo.index.to_list()]
    memo = memo.resample('M').mean().tail(6)

    table = memo.to_html(na_rep = "").replace('<table','<table id="effect" style="width:40%; height:auto;"').replace('<th>','<th style = "background-color: rgb(60,179,113); color:black">')
    text = f"""<h3>REPORTE CAMBIARIO, MANTENGASE INFORMADO.</h3>
    <p>Principales variables a estar atentos.<br /></p>"""
    text += """
            <p>Contenido:</p>
              <ul>
                <li>Grafica evolución espectro dolares argentinos.</li>i
                <br><br>
                <li>Tabla evolución mensual.</li>
              </ul>  
     """

    plots = f"""<img src="cid:ArgentinaFX" style="width:60%">
                 <div>{table}</div>
                """
  
    signature = '<p>Esperamos que esta in formación le sea de su utilidad.<br /></p><p>Saludos</p>'

    html_file = style + text + plots + signature + end_html

    if i == 0:
      e = open(f'market.html','w') 
      e.write(html_file)
      e.close()

    recipients = [f'{recipients.Email.values[i]}']

    def sendEmail(html_file):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"QUAVAS REPORT {dt.date.today}"
        msg['From'] = credentials.account
        msg['To'] = ",".join(recipients)  
        image.add_header('Content-ID', '<ArgentinaFX>')
        msg.attach(image)
        part1 = html_file
        part1 = MIMEText(part1, 'html')
        msg.attach(part1)
        part1 = html_file
        part1 = MIMEText(part1, 'html')
        msg.attach(part1)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        # login account + password
        server.login(credentials.account,credentials.password)
        server.sendmail(credentials.account,
                    recipients,
                    msg.as_string())
        server.quit()

    e = sendEmail(html_file)
    e
    print(f"{dt.datetime.now().strftime('%H:%M:%S:%f')} Report SENT!!!")
 
