#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# # Connecting/Query SQL Database

# In[2]:


#cnx = mysql.connector.connect(
##    host='tta-riskapp-external-data-prod.cqnfeqzazysv.eu-west-1.rds.amazonaws.com',
#    user='trading',
#    password='Risk123!@#',
#    database='tradingpro_mt4_server2'
#)

## Perform database operations
#cursor = cnx.cursor()

# Define the SQL query
#query = "SELECT T.TICKET AS Deal, T.LOGIN AS Login, T.OPEN_TIME AS 'Open_Time', T.CMD AS Type, T.SYMBOL AS Symbol, T.VOLUME AS Volume, T.OPEN_PRICE AS 'Open_Price', T.CLOSE_TIME AS 'Close_Time', T.CLOSE_PRICE AS 'Close_Price', T.COMMISSION AS Commission, T.PROFIT AS Profit, U.CURRENCY AS Currency FROM tradingpro_mt4_server2.MT4_TRADES AS T LEFT JOIN tradingpro_mt4_server2.MT4_USERS AS U ON T.LOGIN = U.LOGIN WHERE T.CMD != 7 AND T.CMD != 6 AND T.CLOSE_TIME >= '2023-01-01 00:00:00' AND T.CLOSE_TIME < '2023-02-01 00:00:00';"

# Execute the query
#cursor.execute(query)

# Fetch all rows from the result set
#result = cursor.fetchall()


# Convert the result to a pandas DataFrame
#columns = [col[0] for col in cursor.description]
#df = pd.DataFrame(result, columns=columns)

#print(df)

#Close the cursor and connection
#cursor.close()
#cnx.close()



# In[3]:


#os.chdir(r'C:\Users\john.moore.TT\OneDrive - Finalto Group\Documents - FT-RiskTeam\Trading Pro\Server 2\SQL Monthly Extracts')


# In[4]:


#jan_df.to_csv('jan_df.csv')


# # Reading and formatting data

# In[5]:


folder_path = "C:/users/john.moore.TT/OneDrive - Finalto Group/Documents - FT-RiskTeam/Trading Pro/Server 1/SQL Monthly Extracts"


# In[6]:


dataframes = []
#iterate over files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        
        df = pd.read_csv(file_path, encoding='latin-1')
        
        dataframes.append(df)
    
combined_df = pd.concat(dataframes, ignore_index=True)

combined_df


# In[7]:


combined_df.columns


# In[10]:


combined_df = combined_df.rename(columns = {'Open_Time':'Open Time', 'Close_Time':'Close Time', 'Open_Price':'Open Price', 'Close_Price':'Close Price'})
combined_df


# In[11]:


combined_df = combined_df.drop(columns={'Unnamed: 0'}, axis=1)
combined_df


# In[12]:


combined_df.dtypes


# In[13]:


# Assuming combined_df is the DataFrame containing the data
combined_df['Close Time'] = pd.to_datetime(combined_df['Close Time']).dt.strftime('%-m/%-d/%Y %H:%M')
combined_df['Open Time'] = pd.to_datetime(combined_df['Open Time']).dt.strftime('%-m/%-d/%Y %H:%M')


# In[14]:


combined_df['Close Time'] = pd.to_datetime(combined_df['Close Time'])
combined_df['Open Time'] = pd.to_datetime(combined_df['Open Time'])


# In[15]:


combined_df = combined_df.sort_values('Close Time')
combined_df


# In[16]:


combined_df['Type'] = combined_df['Type'].replace({1: 'Sell', 0: 'Buy'})
combined_df


# In[17]:


combined_df = combined_df[combined_df['Type'].isin(['Sell', 'Buy'])]
combined_df


# In[18]:


symbols_list = combined_df['Symbol'].unique()
symbols_list = pd.DataFrame(symbols_list, columns=['Value'])
symbols_list


# In[19]:


os.chdir("C:/users/john.moore.TT/OneDrive - Finalto Group/Documents - FT-RiskTeam/Trading Pro")


# In[20]:


#symbols_list.to_csv('Symbols_list.csv')


# In[21]:


symbols = pd.read_csv(r"C:\Users\john.moore.TT\OneDrive - Finalto Group\Documents - FT-RiskTeam\Trading Pro\Server 1\symbols.csv")
symbols


# In[22]:


symbols.columns


# In[23]:


#symbols = symbols.drop(columns={'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9'}, axis=1)
#symbols


# In[24]:


combined_df = pd.merge(combined_df, symbols, on='Symbol', how='left')
combined_df


# In[25]:


combined_df.columns


# In[26]:


#combined_df = combined_df.drop(columns={'Unnamed: 17'}, axis=1)
#combined_df


# In[27]:


# This calculates the Profit based on the USC Columns 
#combined_df['Profit'] = np.where(combined_df['Currency'] == 'USC', combined_df['Profit'] / 100, combined_df['Profit'])
#combined_df


# # Formatting DF

# In[28]:


combined_df.columns


# In[29]:


#def format_df(combined_df):
    #combined_df = combined_df.drop(columns = {'Unnamed: 17',
    #   'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21',
    #   'Unnamed: 22', 'Unnamed: 23', 'Unnamed: 24', 'Unnamed: 25',
    #   'Unnamed: 26'}, axis=1)
#    combined_df = combined_df.rename(columns = {'Open Time': 'Open Time', 'Close Time':'Close Time'})
#    combined_df['Close Time'] = pd.to_datetime(combined_df['Close Time'])
#    combined_df['Open Time'] = pd.to_datetime(combined_df['Open Time'])
#    combined_df = combined_df.sort_values(by='Close Time', ascending=True)
#    combined_df = combined_df[combined_df['Close Time'] > '2020-01-01']
#    combined_df = combined_df.fillna(0)
    
#    return combined_df


# In[30]:


#combined_df = format_df(combined_df)
#combined_df


# In[31]:


#combined_df = combined_df[combined_df['Profit'] <= 5000000]
#combined_df


# In[32]:


combined_df.sort_values('Profit', ascending=False).head(20)


# In[33]:


combined_df = combined_df[combined_df['Symbol'] != 'XNGUSD']


# In[34]:


combined_df['Login'] = combined_df['Login'].astype(str).str.replace(',', '').astype(float)
combined_df


# In[35]:


combined_df = combined_df.sort_values(by='Close Time')
combined_df


# In[36]:


combined_df['Time in Trade (min)'] = (combined_df['Close Time'] - combined_df['Open Time']).dt.total_seconds() / 60
combined_df


# In[37]:


combined_df['Month'] = combined_df['Close Time'].dt.strftime('%b')
combined_df


# In[38]:


combined_df = combined_df.rename(columns = {' Multiplier ':'Multiplier'})
combined_df.columns


# In[39]:


combined_df['Multiplier'] = combined_df['Multiplier'].astype(float)
combined_df


# In[40]:


# This is wrong
def calculate_usd_notional(row):
    if row['Instrument Type'] == "FX":
        return 2 * row['Volume'] * row['Multiplier'] * row['USD CNV']
    else:
        return 2 * row['Volume'] * row['Multiplier'] * row['Close Price'] * row['USD CNV']
    
combined_df['USD Notional'] = combined_df.apply(calculate_usd_notional, axis=1).fillna(0)
combined_df


# In[41]:


combined_df[combined_df['Symbol'] == 'XAUUSD']


# In[42]:


combined_df.sort_values('USD Notional', ascending=False).head(25)


# In[43]:


pd.set_option('display.max_columns', None)


# In[44]:


combined_df.dtypes


# In[45]:


combined_df['Profit'] = pd.to_numeric(combined_df['Profit'], errors='coerce')


# In[47]:


#max_profit = 1000000
#mask = combined_df['Profit'] <= max_profit
#combined_df= combined_df[mask]


# # Getting PL by Account and Symbol

# In[48]:


def drawdown(combined_df):
    combined_df = combined_df.sort_values(by='Close Time')
    #This gets running PL from Client's POV\n",
    #combined_df['Running PL'] = combined_df['Profit'].cumsum().round(2)
    #Getting PL in Finalto's POV forc calculating our drawdown\n",
    combined_df['Running PL'] = (combined_df['Profit'].cumsum().round(2))
    combined_df['HighWater'] = combined_df['Running PL'].cummax()
    combined_df['Drawdown'] = (combined_df['Running PL'] - combined_df['HighWater'])
    
    
    return combined_df


# In[49]:


combined_df = drawdown(combined_df)
combined_df


# In[50]:


combined_df['Time Bucket'] = pd.cut(combined_df['Time in Trade (min)'], bins=20, labels=False) + 1
combined_df


# # Running Notional 

# In[51]:


def calculate_directional_notional(combined_df, symbol):
    # Filter closed trades for the specified symbol
    symbol_trades = combined_df[combined_df['Symbol'] == symbol]

    # Sort trades by closing time
    symbol_trades = symbol_trades.sort_values('Close Time')

    # Calculate directional notional
    symbol_trades['DirectionalNotional'] = symbol_trades.apply(lambda row: row['USD Notional']
                                                               if row['Type'] == 'Buy'
                                                               else -row['USD Notional'],
                                                               axis=1)
    
    symbol_trades['RunningDirectionalNotional'] = symbol_trades['DirectionalNotional'].cumsum()

    return symbol_trades[['Close Time', 'Symbol', 'DirectionalNotional', 'RunningDirectionalNotional']]


# In[ ]:


symbols_trades = calculate_directional_notional(combined_df, 'XAUUSD')


# In[ ]:


symbols_trades


# In[ ]:


start_time = '2023-01-01 00:00:00'
end_time = '2023-01-16 23:59:00'

filtered_trades = combined_df[(combined_df['Symbol'] == 'XAUUSD') & (combined_df['Close Time'] >= start_time) & (combined_df['Close Time'] <= end_time)]
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


winning_trades/total_trades


# In[ ]:


combined_df


# In[ ]:


pd.options.display.float_format = '{:,.2f}'.format

# Calculate total USD Profit and USD Notional
total_profit = combined_df['Profit'].sum()
total_notional = combined_df['USD Notional'].sum()

# Calculate average Time in Trade (min)
average_time_in_trade = combined_df['Time in Trade (min)'].mean()

# Calculate average winning trade USD Profit
average_winning_profit = combined_df.loc[combined_df['Profit'] > 0, 'Profit'].mean()

# Calculate average losing trade USD Profit
average_losing_profit = combined_df.loc[combined_df['Profit'] < 0, 'Profit'].mean()

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


top_symbols_pl = combined_df.groupby('Symbol')['Profit'].sum().nlargest(5).reset_index()
top_symbols_pl


# In[ ]:


# Top and bottom symbols by Notional 


# In[ ]:


top_symbols = combined_df.groupby('Symbol')['USD Notional'].sum().nlargest(5).index
filtered_combined_df = combined_df[(combined_df['Symbol'].isin(top_symbols)) & (combined_df['USD Notional'] <= 300000000)]
sorted_combined_df = filtered_combined_df.sort_values('USD Notional', ascending=False)

top_symbols_df = filtered_combined_df.groupby('Symbol').agg({'USD Notional': 'sum', 'Profit': 'sum'}).reset_index()
top_symbols_df


# In[ ]:


top_symbols_df = top_symbols_df.sort_values('USD Notional', ascending=False)
top_symbols_df


# In[ ]:


top_symbols_df['PL/MM'] = top_symbols_df['Profit'] / (top_symbols_df['USD Notional']/1000000)
top_symbols_df


# In[ ]:


top_symbols_df.dtypes


# # Top symbols by Profit

# In[ ]:


# Calculate total PL and USD Notional per symbol
symbol_pl = combined_df.groupby('Symbol')['Profit'].sum()
symbol_notional = combined_df.groupby('Symbol')['USD Notional'].sum()

# Sort symbols by total PL
sorted_symbols = symbol_pl.sort_values(ascending=False)

# Get top 5 symbols by PL
top_symbols = sorted_symbols.head(5)

# Create a DataFrame with top symbols and their USD Notional
top_symbols_df = pd.DataFrame({'Symbol': top_symbols.index, 'Profit': top_symbols.values})
top_symbols_df['USD Notional'] = [symbol_notional[symbol] for symbol in top_symbols.index]


# In[ ]:


top_symbols_df['PL/MM'] = top_symbols_df['Profit']/(top_symbols_df['USD Notional']/1000000)
top_symbols_df


# # Bottom Symbols by PL

# In[ ]:


# Calculate total PL and USD Notional per symbol
symbol_pl = combined_df.groupby('Symbol')['Profit'].sum()
symbol_notional = combined_df.groupby('Symbol')['USD Notional'].sum()

# Sort symbols by total PL
sorted_symbols = symbol_pl.sort_values(ascending=True)

# Get top 5 symbols by PL
bottom_symbols = sorted_symbols.head(5)

# Create a DataFrame with top symbols and their USD Notional
bottom_symbols_df = pd.DataFrame({'Symbol': bottom_symbols.index, 'Profit': bottom_symbols.values})
bottom_symbols_df['USD Notional'] = [symbol_notional[symbol] for symbol in bottom_symbols.index]


# In[ ]:


bottom_symbols_df['PL/MM'] = bottom_symbols_df['Profit']/(bottom_symbols_df['USD Notional']/1000000)
bottom_symbols_df


# # Top and Bottom logins

# In[ ]:


# Calculate aggregate metrics per Login
login_summary = combined_df.groupby('Login').agg({'Profit': 'sum',
                                                  'USD Notional': 'sum'})

# Calculate PL/MM for each Login
login_summary['PL/MM'] = login_summary['Profit'] / (login_summary['USD Notional'] / 1e6)

# Sort by USD Profit in descending order and select top 10 Logins
top_10_logins = login_summary.nlargest(10, 'Profit')

# Display the top 10 Logins dataframe
top_10_logins.index = top_10_logins.index.astype(str).str.replace(',', '')
#top_10_logins.index = top_10_logins.index.astype(int)
top_10_logins


# In[ ]:


# Calculate aggregate metrics per Login
login_summary = combined_df.groupby('Login').agg({'Profit': 'sum',
                                                  'USD Notional': 'sum'})

# Calculate PL/MM for each Login
login_summary['PL/MM'] = login_summary['Profit'] / (login_summary['USD Notional'] / 1e6)

# Sort by USD Profit in ascending order and select bottom 10 Logins
bottom_10_logins = login_summary.nsmallest(10, 'Profit')

# Display the bottom 10 Logins dataframe
bottom_10_logins.index = bottom_10_logins.index.astype(str).str.replace(',', '')
bottom_10_logins


# In[ ]:


# Calculate aggregate metrics per Login
login_summary = combined_df.groupby('Login').agg({'Profit': 'sum',
                                                  'USD Notional': 'sum'})

# Calculate PL/MM for each Login
login_summary['PL/MM'] = login_summary['Profit'] / (login_summary['USD Notional'] / 1e6)

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
    plt.title("Trading Pro Server 1 XAUUSD Running Directional Notional", fontsize=26, color='w')
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
monthly_profit = combined_df.groupby('Month')['Profit'].sum()
monthly_notional


# In[ ]:


month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']


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
instrument_type_profit = combined_df.groupby('Instrument Type')['Profit'].sum()


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

