from flask import Flask
from flask_jsonpify import jsonpify
from packages import *
app = Flask(__name__)

from products import products

@app.route('/atm')
def atm():
    return atm.operation()

@app.route('/market')
def market():
    excel = pd.read_excel('Central-Bank-Report.xlsx')
    excel.index = excel['Unnamed: 0'].to_list()
    del excel['Unnamed: 0']
    excel = excel[['tc_oficial', 'solidario', 'Cable Apple', 'FX Fundamental',
       'Monetarista Blue','AL30']].tail(20)
    excel.columns = ['Oficial','Solidario','Cable','Fx-Fundamental','Monetarista','AL30']
    excel = excel[~excel.index.duplicated(keep='first')].to_json(orient='table')
    return excel 

if __name__=='__main__':
    app.run(debug=True)
