import os, shutil, glob 
import pandas as pd, numpy as np
import datetime as dt

'''
Reads files at DATABASE, create columns 
Status = [0,1,2,3] for 
0 do nothing
1 rebalance weigths to original values
2 change ammount of investment
3 update risk

Change amount +/- to change investment
TImestamp track record changes

End result ==> scanner.xlsx
'''
file = []

for filename in glob.iglob('./DATABASE/*'):
    file.append(filename)
    
file = pd.DataFrame(file,columns=['Path'])
file['Symbol'] = [i.split()[0][2:].split('/')[-1] for i in file.Path.to_list()]
file['Name'] = [' '.join(i.split()[1:3]) for i in file.Path.to_list()]
file['Email'] = [(i.split()[3]) for i in file.Path.to_list()]
file['Capital'] = [i.split()[4] for i in file.Path.to_list()]
file['Optimization'] = [i.split()[-2] for i in file.Path.to_list()]
file['Status'] = 0
file['Change'] = 0
file['TimeStamp'] = [(i.split()[-1][0:10]) for i in file.Path.to_list()]
file.index = range(len(file))

writer = pd.ExcelWriter('scanner.xlsx',engine='xlsxwriter')
file.to_excel(writer)
writer.save()
