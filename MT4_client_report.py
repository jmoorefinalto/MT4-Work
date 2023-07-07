#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
import os
import csv
from pathlib import Path
from datetime import date, datetime, time, timedelta
from dateutil import relativedelta
import win32com.client as client
from win32com.client import Dispatch, DispatchEx
from pretty_html_table import build_table
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as md
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter
import mysql.connector


# # Connecting to SQL Database

# In[ ]:


#pip install mysql.connector


# In[ ]:


cnx = mysql.connector.connect(
    host='tta-riskapp-external-data-prod.cqnfeqzazysv.eu-west-1.rds.amazonaws.com',
    user='trading',
    password='Risk123!@#',
    database='tradingpro_mt4_server1'
)


# In[ ]:


# Perform database operations
cursor = cnx.cursor()

# Define the SQL query
query = "SELECT LOGIN, CURRENCY FROM MT4_USERS"

# Execute the query
cursor.execute(query)

# Fetch all rows from the result set
result = cursor.fetchall()


# Convert the result to a pandas DataFrame
columns = [col[0] for col in cursor.description]
users = pd.DataFrame(result, columns=columns)

print(users)

#Close the cursor and connection
cursor.close()
cnx.close()


# In[ ]:


users = users.rename(columns = {'LOGIN': 'Login'})
users


# # Changing to correct working directory

# In[ ]:





# In[ ]:


folder_path = "C:/users/john.moore.TT/OneDrive - Finalto Group/Documents - FT-RiskTeam/Trading Pro/Server 1"


# In[ ]:


dataframes = []
#iterate over files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        
        df = pd.read_csv(file_path, encoding='latin-1')
        
        dataframes.append(df)
    
combined_df = pd.concat(dataframes, ignore_index=True)

combined_df


# In[ ]:


symbols_list = combined_df['Symbol'].unique()
symbols_list = pd.DataFrame(symbols_list, columns=['Value'])
symbols_list


# In[ ]:


os.chdir("C:/users/john.moore.TT/OneDrive - Finalto Group/Documents - FT-RiskTeam/Trading Pro")


# In[ ]:


#symbols_list.to_csv('Symbols_list.csv')


# In[ ]:


symbols = pd.read_csv(r"C:\Users\john.moore.TT\OneDrive - Finalto Group\Documents - FT-RiskTeam\Trading Pro\symbols.csv")
symbols


# In[ ]:


symbols.columns


# In[ ]:


#symbols = symbols.drop(columns={'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9'}, axis=1)
#symbols


# In[ ]:


combined_df = pd.merge(combined_df, symbols, on='Symbol', how='left')
combined_df


# In[ ]:


combined_df = pd.merge(combined_df, users, on='Login', how='left')
combined_df


# In[ ]:


combined_df.columns


# In[ ]:


#combined_df = combined_df.drop(columns={'Unnamed: 17'}, axis=1)
#combined_df


# In[ ]:


combined_df = combined_df.drop(columns={'Unnamed: 17',
       'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21',
       'Unnamed: 22', 'Unnamed: 23', 'Unnamed: 24', 'Unnamed: 25',
       'Unnamed: 26'}, axis=1)
combined_df


# In[ ]:


combined_df['Profit'] = np.where(combined_df['CURRENCY'] == 'USC', combined_df['Profit'] / 100, combined_df['Profit'])
combined_df


# # Formatting DF

# In[ ]:


combined_df.columns


# In[ ]:


def format_df(combined_df):
    #combined_df = combined_df.drop(columns = {'Unnamed: 17',
    #   'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21',
    #   'Unnamed: 22', 'Unnamed: 23', 'Unnamed: 24', 'Unnamed: 25',
    #   'Unnamed: 26'}, axis=1)
    combined_df = combined_df.rename(columns = {'Open Time': 'Open Time', 'Close Time':'Close Time'})
    combined_df['Close Time'] = pd.to_datetime(combined_df['Close Time'])
    combined_df['Open Time'] = pd.to_datetime(combined_df['Open Time'])
    combined_df = combined_df.sort_values(by='Close Time', ascending=True)
    combined_df = combined_df[combined_df['Close Time'] > '2020-01-01']
    combined_df = combined_df.fillna(0)
    
    return combined_df


# In[ ]:


combined_df = format_df(combined_df)
combined_df


# In[ ]:


#combined_df = combined_df[combined_df['Profit'] <= 5000000]
#combined_df


# In[ ]:


combined_df.sort_values('Profit', ascending=False).head(20)


# In[ ]:


combined_df['Login'] = combined_df['Login'].astype(str).str.replace(',', '').astype(float)
combined_df


# In[ ]:


combined_df = combined_df.sort_values(by='Close Time')
combined_df


# In[ ]:


combined_df['Time in Trade (min)'] = (combined_df['Close Time'] - combined_df['Open Time']).dt.total_seconds() / 60
combined_df


# In[ ]:


combined_df['Month'] = combined_df['Close Time'].dt.strftime('%b')
combined_df


# In[ ]:


combined_df = combined_df.rename(columns = {' Multiplier ':'Multiplier'})
combined_df.columns


# In[ ]:


combined_df['Multiplier'] = combined_df['Multiplier'].astype(float)
combined_df


# In[ ]:


def calculate_usd_notional(row):
    if row['Instrument Type'] == "FX":
        return 2 * row['Volume'] * row['Multiplier'] * row['USD CNV']
    else:
        return 2 * row['Volume'] * row['Multiplier'] * row['USD CNV']
    
combined_df['USD Notional'] = combined_df.apply(calculate_usd_notional, axis=1).fillna(0)
combined_df


# In[ ]:


combined_df.sort_values('USD Notional', ascending=False).head(25)


# In[ ]:


combined_df['USD Profit'] = (combined_df['Swap']+combined_df['Profit'])
combined_df


# In[ ]:


pd.set_option('display.max_columns', None)


# In[ ]:


combined_df.dtypes


# In[ ]:


combined_df['Profit'] = pd.to_numeric(combined_df['Profit'], errors='coerce')


# In[ ]:


combined_df = combined_df.drop(combined_df[combined_df['Symbol'] == 'xngusd'].index)
combined_df


# In[ ]:


#max_profit = 1000000
#mask = combined_df['Profit'] <= max_profit
#combined_df= combined_df[mask]


# # Getting PL by Account and Symbol

# In[ ]:


def drawdown(combined_df):
    combined_df = combined_df.sort_values(by='Close Time')
    #This gets running PL from Client's POV\n",
    combined_df['Running PL'] = combined_df['USD Profit'].cumsum().round(2)
    #Getting PL in Finalto's POV for calculating our drawdown\n",
    combined_df['Running PL'] = (combined_df['USD Profit'].cumsum().round(2))
    combined_df['HighWater'] = combined_df['Running PL'].cummax()
    combined_df['Drawdown'] = (combined_df['Running PL'] - combined_df['HighWater'])
    
    
    return combined_df


# In[ ]:


combined_df = drawdown(combined_df)
combined_df


# In[ ]:


combined_df['Time Bucket'] = pd.cut(combined_df['Time in Trade (min)'], bins=20, labels=False) + 1
combined_df


# # Running Notional 

# In[ ]:


def calculate_directional_notional(combined_df, symbol):
    # Filter closed trades for the specified symbol
    symbol_trades = combined_df[combined_df['Symbol'] == symbol]

    # Sort trades by closing time
    symbol_trades = symbol_trades.sort_values('Close Time')

    # Calculate directional notional
    symbol_trades['DirectionalNotional'] = symbol_trades.apply(lambda row: row['USD Notional']
                                                               if row['Type'] == 'buy'
                                                               else -row['USD Notional'],
                                                               axis=1)
    
    symbol_trades['RunningDirectionalNotional'] = symbol_trades['DirectionalNotional'].cumsum()

    return symbol_trades[['Close Time', 'Symbol', 'DirectionalNotional', 'RunningDirectionalNotional']]


# In[ ]:


symbols_trades = calculate_directional_notional(combined_df, 'eurusd')


# In[ ]:


symbols_trades


# In[ ]:


start_time = '2023-01-01 00:00:00'
end_time = '2023-01-16 23:59:00'

filtered_trades = combined_df[(combined_df['Symbol'] == 'xauusd') & (combined_df['Close Time'] >= start_time) & (combined_df['Close Time'] <= end_time)]
filtered_trades


# In[ ]:


sorted_trades = filtered_trades.sort_values('USD Notional', ascending=False)
sorted_trades


# In[ ]:


symbols_trades = symbols_trades[symbols_trades['DirectionalNotional'] <= 300000000]
symbols_trades


# In[ ]:


symbols_trades = symbols_trades[symbols_trades['DirectionalNotional'] >= -300000000]
symbols_trades


# In[ ]:


symbols_trades


# In[ ]:


symbols_trades['RunningDirectionalNotional'] = symbols_trades['DirectionalNotional'].cumsum()
symbols_trades


# # Cleaning data

# In[ ]:


#import matplotlib.pyplot as plt

#plt.figure(figsize=(10, 6))
#plt.bar(sorted_trades['Close Time'], sorted_trades['USD Notional'])
#plt.xlabel('Close Time')
#plt.ylabel('USD Notional')
#plt.title('Sorted Trades by USD Notional')
#plt.xticks(rotation=45)
#plt.show()


# In[ ]:


top_close_times_and_notional = symbols_trades.nlargest(n=5, columns='DirectionalNotional')[['Close Time', 'DirectionalNotional']]
top_close_times_and_notional


# # Summary DF

# In[ ]:


total_trades = combined_df.shape[0]
winning_trades = combined_df[combined_df['Profit'] > 0].shape[0]


# In[ ]:





# In[ ]:


winning_trades/total_trades


# In[ ]:


combined_df


# In[1]:


os.get_cwd()


# In[ ]:


pd.options.display.float_format = '{:,.2f}'.format

# Calculate total USD Profit and USD Notional
total_profit = combined_df['USD Profit'].sum()
total_notional = combined_df['USD Notional'].sum()

# Calculate average Time in Trade (min)
average_time_in_trade = combined_df['Time in Trade (min)'].mean()

# Calculate average winning trade USD Profit
average_winning_profit = combined_df.loc[combined_df['USD Profit'] > 0, 'USD Profit'].mean()

# Calculate average losing trade USD Profit
average_losing_profit = combined_df.loc[combined_df['USD Profit'] < 0, 'USD Profit'].mean()

# Calculate PL/MM
pl_per_million = total_profit / (total_notional / 1e6)

# Create summary DataFrame
summary_df = pd.DataFrame({'Total USD Profit': [total_profit],
                           'Total USD Notional': [total_notional],
                           'PL/MM': [pl_per_million],
                           'Average Time in Trade (min)': [average_time_in_trade],
                           'Average Winning Trade': [average_winning_profit],
                           'Average Losing Trade': [average_losing_profit]})

summary_df['Win%'] = winning_trades/total_trades
total_trades = '{:,}'.format(total_trades)
summary_df['Trade Count'] = total_trades 

# Adding Start Date and End Date to summary_df 
summary_df['Start Date'] = combined_df['Close Time'].min().strftime('%Y-%m-%d')
summary_df['End Date'] = combined_df['Close Time'].max().strftime('%Y-%m-%d')

# Calculating Sharpe and Sortino ratio
#risk_free_rate = 0.05  # risk-free rate (5%)
#average_return = combined_df['USD Profit'].mean()
#standard_deviation = combined_df['USD Profit'].std()
#downside_deviation = combined_df[combined_df['USD Profit'] < 0]['USD Profit'].std()

#summary_df['Sharpe Ratio'] = (average_return - risk_free_rate) / standard_deviation
#summary_df['Sortino Ratio'] = (average_return - risk_free_rate) / downside_deviation

# Display summary DataFrame
summary_df


# # Top and Bottom Symbols by PL

# In[ ]:


top_symbols_pl = combined_df.groupby('Symbol')['USD Profit'].sum().nlargest(5).reset_index()
top_symbols_pl


# In[ ]:


# Top and bottom symbols by Notional 


# In[ ]:


top_symbols = combined_df.groupby('Symbol')['USD Notional'].sum().nlargest(5).index
filtered_combined_df = combined_df[(combined_df['Symbol'].isin(top_symbols)) & (combined_df['USD Notional'] <= 300000000)]
sorted_combined_df = filtered_combined_df.sort_values('USD Notional', ascending=False)

top_symbols_df = filtered_combined_df.groupby('Symbol').agg({'USD Notional': 'sum', 'USD Profit': 'sum'}).reset_index()
top_symbols_df


# In[ ]:


top_symbols_df = top_symbols_df.sort_values('USD Notional', ascending=False)
top_symbols_df


# In[ ]:


top_symbols_df['PL/MM'] = top_symbols_df['USD Profit'] / (top_symbols_df['USD Notional']/1000000)
top_symbols_df


# In[ ]:


top_symbols_df.dtypes


# # Top symbols by Profit

# In[ ]:


# Calculate total PL and USD Notional per symbol
symbol_pl = combined_df.groupby('Symbol')['USD Profit'].sum()
symbol_notional = combined_df.groupby('Symbol')['USD Notional'].sum()

# Sort symbols by total PL
sorted_symbols = symbol_pl.sort_values(ascending=False)

# Get top 5 symbols by PL
top_symbols = sorted_symbols.head(5)

# Create a DataFrame with top symbols and their USD Notional
top_symbols_df = pd.DataFrame({'Symbol': top_symbols.index, 'USD Profit': top_symbols.values})
top_symbols_df['USD Notional'] = [symbol_notional[symbol] for symbol in top_symbols.index]


# In[ ]:


top_symbols_df['PL/MM'] = top_symbols_df['USD Profit']/(top_symbols_df['USD Notional']/1000000)
top_symbols_df


# # Bottom Symbols by PL

# In[ ]:


# Calculate total PL and USD Notional per symbol
symbol_pl = combined_df.groupby('Symbol')['USD Profit'].sum()
symbol_notional = combined_df.groupby('Symbol')['USD Notional'].sum()

# Sort symbols by total PL
sorted_symbols = symbol_pl.sort_values(ascending=True)

# Get top 5 symbols by PL
bottom_symbols = sorted_symbols.head(5)

# Create a DataFrame with top symbols and their USD Notional
bottom_symbols_df = pd.DataFrame({'Symbol': bottom_symbols.index, 'USD Profit': bottom_symbols.values})
bottom_symbols_df['USD Notional'] = [symbol_notional[symbol] for symbol in bottom_symbols.index]


# In[ ]:


bottom_symbols_df['PL/MM'] = bottom_symbols_df['USD Profit']/(bottom_symbols_df['USD Notional']/1000000)
bottom_symbols_df


# # Top and Bottom logins

# In[ ]:


# Calculate aggregate metrics per Login
login_summary = combined_df.groupby('Login').agg({'USD Profit': 'sum',
                                                  'USD Notional': 'sum'})

# Calculate PL/MM for each Login
login_summary['PL/MM'] = login_summary['USD Profit'] / (login_summary['USD Notional'] / 1e6)

# Sort by USD Profit in descending order and select top 10 Logins
top_10_logins = login_summary.nlargest(10, 'USD Profit')

# Display the top 10 Logins dataframe
top_10_logins.index = top_10_logins.index.astype(str).str.replace(',', '')
#top_10_logins.index = top_10_logins.index.astype(int)
top_10_logins


# In[ ]:


# Calculate aggregate metrics per Login
login_summary = combined_df.groupby('Login').agg({'USD Profit': 'sum',
                                                  'USD Notional': 'sum'})

# Calculate PL/MM for each Login
login_summary['PL/MM'] = login_summary['USD Profit'] / (login_summary['USD Notional'] / 1e6)

# Sort by USD Profit in ascending order and select bottom 10 Logins
bottom_10_logins = login_summary.nsmallest(10, 'USD Profit')

# Display the bottom 10 Logins dataframe
bottom_10_logins.index = bottom_10_logins.index.astype(str).str.replace(',', '')
bottom_10_logins


# In[ ]:


# Calculate aggregate metrics per Login
login_summary = combined_df.groupby('Login').agg({'USD Profit': 'sum',
                                                  'USD Notional': 'sum'})

# Calculate PL/MM for each Login
login_summary['PL/MM'] = login_summary['USD Profit'] / (login_summary['USD Notional'] / 1e6)

# Sort by USD Notional in descending order and select top 10 Logins
top_10_logins_notional = login_summary.nlargest(10, 'USD Notional')

# Display the top 10 Logins dataframe
top_10_logins_notional.index = top_10_logins_notional.index.astype(str).str.replace(',', '')
top_10_logins_notional


# # PL & Drawdown Graphs

# In[ ]:


plt.style.use('fivethirtyeight')
plt.rcParams['axes.facecolor'] = 'black'
#fig.set_facecolor('black')


# In[ ]:


def plot_running_directional_notional(symbols_trades):
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(symbols_trades['Close Time'], symbols_trades['RunningDirectionalNotional'], label='Running Directional Notional (USD)')
    ax.set_xlabel('Date', color='w')
    ax.xaxis.set_major_locator(md.MonthLocator())
    plt.xticks(rotation=45, color='w')
    ax.set_ylabel('Directional Notional (USD)', color='w')
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    plt.yticks(color='w')
    plt.style.use('fivethirtyeight')
    plt.rcParams['axes.facecolor'] = 'black'
    fig.set_facecolor('black')
    plt.title("Trading Pro Server 1 EURUSD Running Directional Notional", fontsize=26, color='w')
    plt.show()


# In[ ]:


def plot_running_pl(combined_df):
    fig, ax = plt.subplots(figsize = (15, 6))
    ax.plot(combined_df['Close Time'], combined_df['Running PL'], label = 'Running PL (USD)')
    ax.set_xlabel('Date', color='w')
    ax.xaxis.set_major_locator(md.MonthLocator(bymonth=()))
    plt.xticks(rotation = 45, color='w')
    ax.set_ylabel('PL (USD)', color = 'w')
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,}'))
    plt.yticks(color='w')
    plt.style.use('fivethirtyeight')
    plt.rcParams['axes.facecolor'] = 'black'
    fig.set_facecolor('black')
    plt.title("Trading Pro Server 1 Running PL", fontsize=26, color='w')
    plt.show()


# In[ ]:


def drawdown_graph(combined_df):
    fig, ax = plt.subplots(figsize = (20, 15))
    ax.stackplot(combined_df['Close Time'], combined_df['Drawdown'], labels=['Drawdown'], alpha=0.8)
    ax.set_xlabel('Date', color='w')
    ax.xaxis.set_major_locator(md.MonthLocator(bymonth=()))
    plt.xticks(rotation=45, color='w')
    ax.set_ylabel('PL (USD)', color = 'w')
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,}'))
    plt.yticks(color='w')
    plt.style.use('fivethirtyeight')
    plt.rcParams['axes.facecolor'] = 'black'
    fig.set_facecolor('black')
    plt.title("Trading Pro Server 1 Drawdown from Highwater Mark" , fontsize=26, color='w')
    
    plt.show()


# In[ ]:


combined_df.sort_values('USD Notional', ascending=False).head(20)


# In[ ]:





# In[ ]:


plot_running_directional_notional(symbols_trades)


# In[ ]:


plot_running_pl(combined_df)


# In[ ]:


drawdown_graph(combined_df)


# # YTD Monthly Notional and PL Bar Charts

# In[ ]:


monthly_notional = combined_df.groupby('Month')['USD Notional'].sum()
monthly_profit = combined_df.groupby('Month')['USD Profit'].sum()
monthly_notional


# In[ ]:


month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']


# In[ ]:


monthly_notional = monthly_notional.reindex(month_order)
monthly_profit = monthly_profit.reindex(month_order)
monthly_notional


# In[ ]:


# Create bar chart for total USD Notional
plt.style.use('fivethirtyeight')
plt.rcParams['axes.facecolor'] = 'black'
#plt.set_facecolor('black')
plt.figure(figsize=(10, 6))
monthly_notional.plot(kind='bar')
plt.xlabel('Month')
plt.ylabel('Total USD Notional')
plt.title('Server 1 USD Notional per Month')
plt.show()


# In[ ]:





# In[ ]:


# Bar chart for USD Profit 
plt.figure(figsize=(10, 6))
monthly_profit.plot(kind='bar')
plt.xlabel('Month')
plt.ylabel('USD Profit')
plt.title('Server 1 USD Profit per Month')
plt.show()


# # Instrument Type Notional and Profit Bar Charts

# In[ ]:


combined_df


# In[ ]:


instrument_type_notional = combined_df.groupby('Instrument Type')['USD Notional'].sum()
instrument_type_profit = combined_df.groupby('Instrument Type')['USD Profit'].sum()


# In[ ]:


# Create bar chart for total USD Notional
plt.style.use('fivethirtyeight')
plt.rcParams['axes.facecolor'] = 'black'
#plt.set_facecolor('black')
plt.figure(figsize=(10, 6))
instrument_type_notional.plot(kind='bar')
plt.xlabel('Instrument Type')
plt.ylabel('Total USD Notional')
plt.title('Server 1 USD Notional per Instrument Type')
plt.show()


# In[ ]:


# Create bar chart for total USD Notional
plt.style.use('fivethirtyeight')
plt.rcParams['axes.facecolor'] = 'black'
#plt.set_facecolor('black')
plt.figure(figsize=(10, 6))
instrument_type_profit.plot(kind='bar')
plt.xlabel('Instrument Type')
plt.ylabel('Total USD Profit')
plt.title('Server 1 USD Profit per Instrument Type')
plt.show()


# In[ ]:





# In[ ]:





# In[ ]:




