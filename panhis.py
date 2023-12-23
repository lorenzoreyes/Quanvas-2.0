from packages import *
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')

today = dt.date.today()

os.system("curl https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/panhis.xls > panhis.xlsx")
print("Panhis downloaded")
