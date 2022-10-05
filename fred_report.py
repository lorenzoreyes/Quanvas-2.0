'''
We want to gather principal factors to pay attention
in order to diagnose tha economic situation of USA
treasury rates (Create curve 3monthBill-30yearMaturity)
Macro Indicators
Relationship with the rest of FoRex Coins
'''
from packages import * 
from federal import *


start = str(dt.date.today().year - 2)
rates = ['DTB3','DTB6','DGS1','DGS2','DGS3','DGS5','DGS10','DGS20','DGS30']

queries = rates.copy()


for i in range(len(rates)):
    queries[i] = fred.get_series(rates[i],observation_start=f'1/1/{start}')
    queries[i] = pd.DataFrame(queries[i].values, columns = [f'{rates[i]}'], index = queries[i].index)
    
treasuries = pd.concat([queries[0],queries[1],queries[2],queries[3],queries[4],\
    queries[5],queries[6],queries[7],queries[8]]).sort_index()

treasuries = treasuries.fillna(method='ffill').dropna()