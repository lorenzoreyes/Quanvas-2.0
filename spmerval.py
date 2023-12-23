from packages import *
from bs4 import BeautifulSoup

url = 'https://bolsar.info/paneles.php?panel=2&titulo=Panel%20General'
header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

gral = requests.get(url, headers=header)
soup = BeautifulSoup(gral.content, 'html.parser')
gral = soup.findAll('table')
gral = pd.read_html(str(gral[0]))[0]
acciones = sorted(list(set(panel.Especie)))

lider = requests.get('https://bolsar.info/lideres.php', headers=header)
soup = BeautifulSoup(lider.content, 'html.parser')
lider = soup.findAll('table')
lider= pd.read_html(str(lider[0]))[0]
lideres = sorted(list(set(lider.Especie)))

mercado = sorted(list(set(acciones + lideres)))
data = yahoo.download([i+'.BA' for i in mercado],period='1y')['Adj Close']