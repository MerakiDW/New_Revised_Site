import requests
from . import db
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
pd.options.display.float_format = '{:,.2}'.format
pd.set_option('display.max_rows', 50)


### eventually db

sales_file = r'/Users/koahiggins/webappkoalocal/webapp/web_app_koa/website/trades.csv'
sales_df = pd.read_csv(sales_file)#.set_index('TD')
# sales_df.index = pd.to_datetime(sales_df.index)
sales_df_drop = sales_df.drop(sales_df[sales_df['TRADE_NUM'].str.contains('ATR')].index)
sales_df_drop = sales_df_drop.drop(sales_df_drop[sales_df_drop['TRADE_NUM'].str.contains('DIST')].index)
sales_df_drop = sales_df_drop.drop(sales_df_drop[sales_df_drop['TRADE_NUM'].str.contains('EDIT')].index)
sales_df_drop = sales_df_drop.drop(sales_df_drop[sales_df_drop['TRADE_NUM'].str.contains('NON')].index)

sales_df_drop['TD'] = pd.to_datetime(sales_df_drop['TD'], format='%m/%d/%y')
sales_df_drop


sales_data_bull = sales_df_drop.drop(sales_df_drop[sales_df_drop['TRADE_NUM'].str.contains('R')].index)


sales_data_rarecoin = sales_df_drop[sales_df_drop['TRADE_NUM'].str.contains('R')]


trader_db_mapping = {
                    'grp_1_tory': ['TMG'],
                    'grp_1_arries': ['MA'],
                    'grp_1_dobesh': ['JAD'],
                    'grp_1_etz': ['JGE'],
                    'grp_1_goodin': ['RVG'],
                    'grp_1_miles': ['MG'],
                    'grp_1_horsey': ['MRH'],
                    'grp_1_mclaughlin': ['ROB'],
                    'grp_1_orrick': ['KBO'],
                    'grp_1_streets': ['GST'],
                    'grp_1_steve': ['SPC'],
                    'grp_1_shayla': ['SMS'],
                    'grp_1_josh': ['JDB']
                }

def replace_trader_dbcode(number):
                    for name, numbers in trader_db_mapping.items():
                        if number in numbers:
                            return name
                    return number


sales_data_bull.loc[:, 'TRADER'] = sales_data_bull['TRADER'].apply(replace_trader_dbcode)
sales_data_rarecoin.loc[:, 'TRADER'] = sales_data_rarecoin['TRADER'].apply(replace_trader_dbcode)

### bullion
sales_buy_data = sales_data_bull.drop(sales_data_bull[sales_data_bull['TRADE_TYPE'].str.contains('S')].index).reset_index()
sales_sell_data = sales_data_bull.drop(sales_data_bull[sales_data_bull['TRADE_TYPE'].str.contains('B')].index).reset_index()

sales_buy_data_len = len(sales_buy_data)
sales_sell_data_len =len(sales_sell_data)

sales_buy_data_total = sales_buy_data['EXTENDED'].sum()
sales_sell_data_total = sales_sell_data['EXTENDED'].sum()


# rare coin
sales_rare_buy_data = sales_data_rarecoin.drop(sales_data_rarecoin[sales_data_rarecoin['TRADE_TYPE'].str.contains('S')].index).reset_index()
sales_rare_sell_data = sales_data_rarecoin.drop(sales_data_rarecoin[sales_data_rarecoin['TRADE_TYPE'].str.contains('B')].index).reset_index()

sales_rare_buy_data_len = len(sales_rare_buy_data)
sales_rare_sell_data_len = len(sales_rare_sell_data)

sales_rare_buy_data_total = sales_rare_buy_data['EXTENDED'].sum()
sales_rare_sell_data_total = sales_rare_sell_data['EXTENDED'].sum()
