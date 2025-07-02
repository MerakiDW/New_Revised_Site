import pandas as pd
import numpy as np
import time
import datetime
import os
from .item_codes import item_code_mapping

def portfolio_sorting(trades_data): 
    trades_data['UNIT_PRICE'] = trades_data['EXTENDED']/trades_data['QUANTITY']
    trades_data['QUANTITY'] = trades_data['QUANTITY'].mask(trades_data.TRADE_TYPE.str.contains('S'),trades_data['QUANTITY']*-1)
    # print(trades_data)
    trades_data_drop = trades_data.drop(trades_data[trades_data['TRADE_NUM'].str.contains('ATR')].index)
    trades_data_drop = trades_data_drop.drop(trades_data_drop[trades_data_drop['TRADE_NUM'].str.contains('DIST')].index)
    trades_data_drop = trades_data_drop.drop(trades_data_drop[trades_data_drop['TRADE_NUM'].str.contains('EDIT')].index)
    trades_data_drop = trades_data_drop.drop(trades_data_drop[trades_data_drop['TRADE_NUM'].str.contains('NON')].index)

    trades_data_drop['TD'] = pd.to_datetime(trades_data_drop['TD'], format='%m/%d/%y')

    trades_data_drop = trades_data_drop.sort_values(by=['CLIENT_NUM', 'TD']).reset_index(drop=True)

    for index, row in trades_data_drop.iterrows():
        if row['TRADE_TYPE'] == 'S':
            b_trade = trades_data_drop[
                (trades_data_drop['TRADE_TYPE'] == 'B') & 
                (trades_data_drop['CLIENT_NUM'] == row['CLIENT_NUM']) & 
                (trades_data_drop['ITEM_CODE'] == row['ITEM_CODE']) &
                (trades_data_drop['TD'] <= row['TD'])
            ]

            for b_index, b_row in b_trade.iterrows():
                if row['QUANTITY'] + b_row['QUANTITY'] >= 0:
                    trades_data_drop.at[b_index, 'QUANTITY'] += row['QUANTITY']
                    trades_data_drop.drop(index, inplace=True)
                    break
                else:
                    row['QUANTITY'] += b_row['QUANTITY']
                    trades_data_drop.drop(b_index, inplace=True)


    trades_data_drop.reset_index(drop=True, inplace=True)
    # trades_data_drop.to_csv('portfolio_org.csv')

    trades_data_drop['UNIT_PRICE'] = trades_data_drop['EXTENDED']/trades_data_drop['QUANTITY']
    trades_data_drop['TD'] = pd.to_datetime(trades_data_drop['TD'], format='%m/%d/%y')


    portfolio_update = trades_data_drop[trades_data_drop['TRADE_TYPE'] == 'B']
    portfolio_final = portfolio_update[portfolio_update['QUANTITY'] != 0]

    return portfolio_final