import pandas as pd
import yfinance as yahoo
import matplotlib.pyplot as plt
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
    #from pytickersymbols import PyTickerSymbols #https://pypi.org/project/pytickersymbols/
    
# obtain the sixth table of the page, with all data of the current Rofex20    
rofex = pd.read_html('https://www.rofex.com.ar/cem/CarteraVigenteROFEX20')[6] 

lista = list(rofex['Instrumento'].values)
lista = [i + '.BA' for i in lista]

data = yahoo.download(lista,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")

cartera = pd.DataFrame((data * (rofex.Cantidad.values / 1000000)).T.sum(),columns=['Rofex20Vigente'],index=data.index)
cartera = cartera.rename(columns={'Rofex20Vigente':f'Rofex20Vigente $ {round(cartera["Rofex20Vigente"].values[-1],3)}'})
fig = plt.figure(figsize=(30,20))
ax1 = fig.add_subplot(111)
cartera.plot(ax=ax1, lw=3., legend=True)
plt.legend(fontsize=20)
ax1.grid(linewidth=2)
plt.title(f'{cartera.columns.values[0]}', fontsize=30, fontweight='bold')
plt.xticks(size = 20)
plt.yticks(size = 20)
plt.show()
