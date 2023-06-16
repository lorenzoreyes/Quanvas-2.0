# all packages set as macro
import pyRofex
import urllib.request
import pandas as pd
import datetime as dt
import yfinance as yahoo
import matplotlib.pyplot as plt
from pylab import mpl
import seaborn as sns
import numpy as np
import trackATM as tracker
import shutil, smtplib, re, os, ssl
import credentials, glob
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
from templateReport import * # template html of all content of the email
import random
from faker import Faker
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from apiBinance import *
import scipy.optimize as sco
from scipy import stats
import time, requests
from bs4 import BeautifulSoup
from selenium import webdriver,common
from selenium.webdriver.common import keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  #For being able to input key presses
