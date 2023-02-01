#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 16:40:59 2023

@author: joachim
"""

import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

def get_cik_from_ticker(ticker):
    with open("company_tickers.json") as f:
        company_tickers = json.load(f)
    for key, values in company_tickers.items():
        if values["ticker"] == ticker:
            cik = values["cik_str"]
            if len(str(cik)) < 10:
                cik = str(cik).zfill(10)
            print(cik)
    return cik
        

def get_eps_10k(ticker):
    cik = get_cik_from_ticker(ticker)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    headers = {
        "User-Agent": "Mozilla/5.0",
        
    }
    response = requests.get(url, headers=headers)
    print(response)
    if response.status_code == 200:
        data = response.json()
    
    #EPS for all years
    op_income_obj = data['facts']['us-gaap']['EarningsPerShareBasic']['units']['USD/shares']
    eps = []
    end_date = []
    start_date = []
    filed_date = []
    end_date_check = datetime.datetime.now()
    for i in range(len(op_income_obj)):
        start_date_1 = pd.to_datetime(data['facts']['us-gaap']['EarningsPerShareBasic']['units']['USD/shares'][i]['start'])
        end_date_1 = pd.to_datetime(data['facts']['us-gaap']['EarningsPerShareBasic']['units']['USD/shares'][i]['end'])
        date_range = (end_date_1 - start_date_1).days
        
        if data['facts']['us-gaap']['EarningsPerShareBasic']['units']['USD/shares'][i]['form'] == "10-K" and date_range > 360:
            if end_date_1 != end_date_check:
                eps.append(data['facts']['us-gaap']['EarningsPerShareBasic']['units']['USD/shares'][i]['val'])
                end_date.append(data['facts']['us-gaap']['EarningsPerShareBasic']['units']['USD/shares'][i]['end'])
                start_date.append(data['facts']['us-gaap']['EarningsPerShareBasic']['units']['USD/shares'][i]['start'])
                filed_date.append(data['facts']['us-gaap']['EarningsPerShareBasic']['units']['USD/shares'][i]['filed'])
                end_date_check = end_date_1
    eps_df = pd.DataFrame({'EPS': eps, 'End Date': end_date, 'Start':start_date, 'filed': filed_date},)
    return eps_df


#ticker = input("Enter company ticker: ")
ticker = "ASML"
eps_df = get_eps_10k(ticker)
eps_df['End Date'] = pd.to_datetime(eps_df['End Date'])
eps_df = eps_df.sort_values(by='End Date')

fig, ax = plt.subplots()
ax.plot_date(eps_df['End Date'], eps_df['EPS'], '-')

xfmt = mdates.DateFormatter('%Y-%m-%d')
ax.xaxis.set_major_formatter(xfmt)
fig.autofmt_xdate()

title = f"{ticker}'s Earning's Per Share"
plt.title(title)
plt.show()