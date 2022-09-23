# Same script as scanner.py, but parsing old excel
# we have to notify via email to the client that the operation
# had been done and paste the new scenario they are in.
import os, shutil, glob 
import pandas as pd, numpy as np
import datetime as dt


file = []

for filename in glob.iglob('./Update/*'):
    file.append(filename)

excel = pd.DataFrame(file,columns=['Path'])

excel['Action'] = [i.split('/')[-1].split()[0] for i in excel.Path.to_list()]
excel['oldCapital'] = [i.split('/')[-1].split()[1] for i in excel.Path.to_list()]
excel['Symbol'] = [i.split('/')[-1].split()[2] for i in excel.Path.to_list()]
excel['Name'] = [' '.join(i.split('/')[-1].split()[3:5]) for i in excel.Path.to_list()]
excel['Email'] = [i.split('/')[-1].split()[5] for i in excel.Path.to_list()]
excel['Capital'] = [i.split('/')[-1].split()[6] for i in excel.Path.to_list()]
excel['Optimization'] = [i.split('/')[-1].split()[7] for i in excel.Path.to_list()]
excel['Date'] = [i.split('/')[-1].split()[8].split('.')[0] for i in excel.Path.to_list()]
excel['Change'] = excel.Capital.values.astype(int) - excel.oldCapital.values.astype(int)
excel['NewName'] =['/'.join(i.split('/')[:-1]) + '/' + ' '.join(i.split('/')[-1].split(' ')[2:-1]) + ' ' + str(dt.date.today()) + '.xlsx' for i in excel.Path.to_list()]
# excel to iterate to send emails
excel.index = range(len(excel))

writer = pd.ExcelWriter('maintain.xlsx',engine='xlsxwriter')
excel.to_excel(writer)
writer.save()
