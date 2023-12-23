from packages import *
options = Options()
options.add_experimental_option("prefs",{'download.prompt_for_download': False})
pd.options.display.float_format = '{:,.2f}'.format
import requests, re, json
import pandas as pd, datetime as dt
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--start-maximized");
chrome_options.headless = True # also works
bot = webdriver.Chrome(options=chrome_options)

bot.get('https://www.comafi.com.ar/custodiaglobal/2483-Programas-Cedear.cedearnote.note.aspx#shares')
sleep(3)
with open('comafi.xlsx','w+') as f:
    f.write(bot.page_source)
