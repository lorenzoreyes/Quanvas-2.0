from packages import * 
import copy 
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')
pd.options.display.float_format = '{:,.2f}'.format

data = pd.read_csv('Estimaciones.csv',encoding="ISO-8859-1", delimiter=';')
data = data.drop(columns=['idProvincia','idDepartamento'])
data[(data['Cultivo']!='Soja 1ra') & (data['Cultivo']!='Soja 2da')]

cultivos = list(set(data['Cultivo'].to_list()))
granos = cultivos.copy()

temporadas = list(set(data['Campaña']))

# reordeno por Departamento-Provincia en una sola columna
data['Ciudad'] = [data['Departamento'].values[i] + ' de ' + data['Provincia'].values[i] for i in range(len(data))]
data = data.drop(columns=['Departamento','Provincia'])

data['Producción']     = [float(i.replace('SD','0')) for i in data['Producción'].astype(str).to_list()]
data['Rendimiento']    = [float(i.replace('SD','0')) for i in data['Rendimiento'].astype(str).to_list()]
data['Sup. Sembrada']  = [float(i.replace('SD','0')) for i in data['Sup. Sembrada'].astype(str).to_list()]

for i in range(len(cultivos)):
    cultivos[i] = data[data['Cultivo'].values==cultivos[i]]
    cultivos[i].index = cultivos[i]['Campaña'] #[i.split('/')[0] for i in cultivos[i]['Campaña']]
    # romper ano y poner provicinas rendimeinto y beta sup cosechada vs rinde
    productores = list(set(cultivos[i]['Ciudad']))
    df = pd.DataFrame(0,columns=productores,index=list(set(cultivos[i].index)))
    df['Campaña'] = df.index
    indice = (df.index.to_list()).copy()
    produccion = []
    for j in productores:
        provincia = j 
        j = cultivos[i][cultivos[i]['Ciudad']==j]
        for k in df['Campaña'].to_dict():
            if k in j['Campaña']:
              produccion.append(j[j['Campaña']==k]['Producción'].values[0])
            else:
              produccion.append(0)

    del df['Campaña']
    size = int(len(produccion)/len(productores))
    chunks = [produccion[x:x+size] for x in range(0,len(produccion),int(len(produccion)/len(productores)))]
    for h in range(len(df.columns)):
        df.iloc[:,h] = chunks[h] 

    cultivos[i] = df
    cultivos[i].index = [i.split('/')[0] for i in indice] 
    cultivos[i] = cultivos[i].sort_index(ascending=True)
    ponderacion, total = list(cultivos[i].iloc[-1,:].astype(int)), sum(cultivos[i].iloc[-1,:].astype(int))
    peso = [round(i*100.0/total,2) for i in ponderacion]
    cultivos[i].columns = [df.columns[i] + ' ' + str(peso[i]) for i in range(len(peso))]
    cultivos[i][f'{granos[i]}'] = cultivos[i].sum(axis=1)

#por ciudades
data['Campaña'] = [i.split('/')[0] for i in data['Campaña'].to_list()]
data.index = data['Campaña']
ciudades = list(set(data['Ciudad'].to_list()))
for i in range(len(ciudades)):
    ciudades[i] = data[data['Ciudad'].values==ciudades[i]]
    ejercicios = sorted(list(set(ciudades[i]['Campaña'])))
    producido = list(set(ciudades[i]['Cultivo']))
    df = pd.DataFrame(0,columns=producido,index=ejercicios)
    for p in producido:
        resultado = ciudades[i][ciudades[i]['Cultivo']==p]['Producción'].to_dict()
        values = {k:v for (k,v) in zip(ejercicios,[0]*len(ejercicios))}
        obtained = [resultado[i] if i in resultado else values[i] for i in ejercicios]
        df[p] = obtained

    ciudades[i] = df

# sembrada
sembrada = list(set(data['Ciudad'].to_list()))
for i in range(len(ciudades)):
    sembrada[i] = data[data['Ciudad'].values==sembrada[i]]
    ejercicios = sorted(list(set(sembrada[i]['Campaña'])))
    producido = list(set(sembrada[i]['Cultivo']))
    df = pd.DataFrame(0,columns=producido,index=ejercicios)
    for p in producido:
        resultado = sembrada[i][sembrada[i]['Cultivo']==p]['Sup. Sembrada'].to_dict()
        values = {k:v for (k,v) in zip(ejercicios,[0]*len(ejercicios))}
        obtained = [resultado[i] if i in resultado else values[i] for i in ejercicios]
        df[p] = obtained

    sembrada[i] = df
    sembrada[i] = sembrada[i].divide(sembrada[i].T.sum(),axis=0)

ciudad = dict(zip(list(set(data['Ciudad'].to_list())),ciudades))
sembrada = dict(zip(list(set(data['Ciudad'].to_list())),sembrada))
for i in ciudad.keys():i = 'PERGAMINO de BUENOS AIRES'
fig = plt.figure(figsize=(40,25))
    ax1 = fig.add_subplot(211)
    ciudad[i].plot(ax=ax1, lw=6.)
    ax1.set_title(f'{i}', fontsize=150, fontweight='bold')
    ax1.grid(True,color='k',linestyle='-.',linewidth=2)
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=20)
    plt.xticks(size=50)
    plt.yticks(size=60)
    ax2 = fig.add_subplot(212)
    sembrada[i].plot(ax=ax2, lw=6., legend=True)
    ax2.grid(True,color='k',linestyle='-.',linewidth=2)
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=20)
    plt.xlabel("Por Cultivo",fontsize=60)
    plt.xticks(size=50)
    plt.yticks(size=60)
    plt.savefig(f'{i}.png',bbox_inches='tight')

writer = pd.ExcelWriter('Granos.xlsx',engine='xlsxwriter')        
[cultivos[i].to_excel(writer, sheet_name=f'{granos[i]}') for i in range(len(granos))]
writer.close()
        
# cierre
for i in range(len(granos)):
    fig = plt.figure(figsize=(40,25))
    ax1 = fig.add_subplot(211)
    columnas = cultivos[i].iloc[-1,:].sort_values(ascending=False).head(20).index.to_list()
    cultivos[i].iloc[:,:-1].plot(ax=ax1, lw=5.)
    ax1.set_title(f'{granos[i]}', fontsize=150, fontweight='bold')
    ax1.grid(True,color='k',linestyle='-.',linewidth=2)
    ax1.legend(columnas,loc='center left', bbox_to_anchor=(1, 0.5),fontsize=40)
    plt.xticks(size=50)
    plt.yticks(size=60)
    ax2 = fig.add_subplot(212)
    cultivos[i].iloc[:,-1].plot(ax=ax2, color='r', lw=8., legend=True)
    ax2.grid(True,color='k',linestyle='-.',linewidth=2)
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=60)
    plt.xlabel(f"{granos[i]}",fontsize=60)
    plt.xticks(size=50)
    plt.yticks(size=60)
    plt.savefig(f'{granos[i]}.png',bbox_inches='tight')

rinde = list(set(data['Cultivo']))
for i in range(len(granos)):
    rinde[i] = data[data['Cultivo'].values==granos[i]]
    rinde[i].index = rinde[i]['Campaña'] #[i.split('/')[0] for i in cultivos[i]['Campaña']]
    # romper ano y poner provicinas rendimeinto y beta sup cosechada vs rinde
    productores = list(set(rinde[i]['Ciudad']))
    df = pd.DataFrame(0,columns=productores,index=list(set(rinde[i].index)))
    df['Campaña'] = df.index
    indice = (df.index.to_list()).copy()
    produccion = []
    for j in productores:
        provincia = j 
        j = rinde[i][rinde[i]['Ciudad']==j]
        for k in df['Campaña'].to_dict():
            if k in j['Campaña']:
              produccion.append(j[j['Campaña']==k]['Rendimiento'].values[0])
            else:
              produccion.append(0)
    
    del df['Campaña']
    size = int(len(produccion)/len(productores))
    chunks = [produccion[x:x+size] for x in range(0,len(produccion),int(len(produccion)/len(productores)))]
    for h in range(len(df.columns)):
        df.iloc[:,h] = chunks[h] 
    
    df = df.replace(0, np.nan)
    rinde[i] = df
    rinde[i].index = [i.split('/')[0] for i in indice] 
    rinde[i] = rinde[i].sort_index(ascending=True)
    rinde[i][f'Rinde{granos[i]}'] = rinde[i].sum(axis=1) / len(rinde[i])
    
for i in range(len(granos)):
    fig = plt.figure(figsize=(40,25))
    ax1 = fig.add_subplot(211)
    columnas = rinde[i].iloc[-1,:].sort_values(ascending=False).head(20).index.to_list()
    rinde[i].iloc[:,:-1].plot(ax=ax1, lw=5.)
    ax1.set_title(f'Rinde - {granos[i]}', fontsize=150, fontweight='bold')
    ax1.grid(True,color='k',linestyle='-.',linewidth=2)
    ax1.legend(columnas,loc='center left', bbox_to_anchor=(1, 0.5),fontsize=40)
    plt.xticks(size=50)
    plt.yticks(size=60)
    ax2 = fig.add_subplot(212)
    rinde[i].iloc[:,-1].plot(ax=ax2, color='r', lw=8., legend=True)
    ax2.grid(True,color='k',linestyle='-.',linewidth=2)
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=60)
    plt.xlabel(f"Rinde{granos[i]}",fontsize=60)
    plt.xticks(size=50)
    plt.yticks(size=60)
    plt.savefig(f'Rinde-{granos[i]}.png',bbox_inches='tight')
    
stock = dict(zip(granos,cultivos))
    
provincias = pd.read_csv('Provincias.csv',encoding="ISO-8859-1", delimiter=';')
provincias['Producción'] = [int(str(i).replace('SD','0')) for i in provincias['Producción'].to_list()]
provincias['Rendimiento'] = [int(str(i).replace('SD','0')) for i in provincias['Rendimiento'].to_list()]
provincias['Sup. Cosechada'] = [int(str(i).replace('SD','0')) for i in provincias['Sup. Cosechada'].to_list()]

granos = list(set(data['Cultivo'].to_list()))
cosechas = granos.copy()
# cultivos / superficie
for i in range(len(granos)):
    cosechas[i] = provincias[provincias['Cultivo'].values==granos[i]]
    cosechas[i].index = cosechas[i]['Campaña'] 
    # romper ano y poner provicinas rendimeinto y beta sup cosechada vs rinde
    productores = list(set(cosechas[i]['Provincia']))
    df = pd.DataFrame(0,columns=productores,index=list(set(cosechas[i].index)))
    df['Campaña'] = df.index
    indice = (df.index.to_list()).copy()
    produccion = []
    for j in productores:
        provincia = j 
        j = cosechas[i][cosechas[i]['Provincia']==j]
        for k in df['Campaña'].to_dict():
            if k in j['Campaña']:
              produccion.append(j[j['Campaña']==k]['Sup. Sembrada'].values[0])
            else:
              produccion.append(0)
    
    del df['Campaña']
    size = int(len(produccion)/len(productores))
    chunks = [produccion[x:x+size] for x in range(0,len(produccion),int(len(produccion)/len(productores)))]
    for h in range(len(df.columns)):
        df.iloc[:,h] = chunks[h] 
        
    cosechas[i] = df
    cosechas[i].index = [i.split('/')[0] for i in indice] 
    cosechas[i] = cosechas[i].sort_index(ascending=True)
    cosechas[i][f'{granos[i]}'] = cosechas[i].sum(axis=1).values
        
superficie = pd.concat([cosechas[i].iloc[:,-1] for i in range(len(cosechas))],axis=1).sort_index()
superficie = superficie.drop(columns=['Soja 2da','Soja 1ra'])
ponderacion = superficie.div(superficie.sum(axis=1), axis=0)    

for i in range(len(granos)):
     fig = plt.figure(figsize=(40,25))
     ax1 = fig.add_subplot(111)
     cosechas[i].iloc[:,:-1].plot(ax=ax1, lw=5.)
     ax1.set_title(f'Rinde - {granos[i]}', fontsize=150, fontweight='bold')
     ax1.grid(True,color='k',linestyle='-.',linewidth=2)
     ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=40)
     plt.xticks(size=50)
     plt.yticks(size=60)
     
fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
columnas = (round(ponderacion.iloc[-1,:].sort_values(ascending=False)*100,2)).to_dict()
ponderacion.iloc[:-1,:-1].plot(ax=ax1, lw=10.)
ax1.set_title('Ponderacion de Cultivos', fontsize=150, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(columnas.items(),loc='center left', bbox_to_anchor=(1, 0.5),fontsize=30)
plt.xticks(size=50)
plt.yticks(size=60)

fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
columnas = (round(ponderacion.iloc[-1,:].sort_values(ascending=False)*100,2)).to_dict()
ponderacion.plot(ax=ax1, lw=10.)
ax1.set_title('Produccion de Cultivos', fontsize=150, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(columnas.items(),loc='center left', bbox_to_anchor=(1, 0.5),fontsize=30)
plt.xticks(size=50)
plt.yticks(size=60)
