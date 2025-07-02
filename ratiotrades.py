import pandas as pd
import numpy as np
import requests
import time
from bs4 import BeautifulSoup
import datetime
import os
from .item_codes import item_code_mapping

pd.options.display.float_format = "{:,.3f}".format
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 50)


### WHAT IS RUN CURRENRTLY DONT DELETE UNTIL AFTER FIX  
# file = r'/Users/koahiggins/webappkoalocal/webapp/web_app_koa/website/trades_webpost.csv'
# dataframe = pd.read_csv(file)

def display_ratio_trades(calculated_df):
    columns_to_check = list(range(10, 22)) + list(range(23, 27)) + list(range(27, 35))
    ratio_trades = calculated_df[(calculated_df.iloc[:, columns_to_check] > 10).any(axis=1)]
    ratio_trades = ratio_trades.iloc[:, :35]

    item_code_name_mapping = {
        'GUEG0100000000': 'Gold American Eagle 1oz',
        'GUEGHO00000000': 'Gold American Eagle 1/2oz',
        'GUEGQO00000000': 'Gold American Eagle 1/4oz',
        'GUEGTO00000000': 'Gold American Eagle 1/10oz',
        'BUFFALOGOLD000': 'Gold American Buffalo 1oz',
        'GCML0100000000': 'Gold Canadian Maple Leaf 1oz',
        'GCMLTO00000000': 'Gold Canadian Maple Leaf 1/10oz',
        'GSKR0100000000': 'Gold South African Krugerrand 1oz',
        'GLKN0100000000': 'Gold Australian Kangaroo 1oz',
        'PHILHARMONICS0': 'Gold Austrian Philharmonic 1oz',
        'PHILHARMONICQO': 'Gold Austrian Philharmonic 1/4oz',
        'PHILHARMONICTO': 'Gold Austrian Philharmonic 1/10oz',
        'GOLDBAR0100000': 'Gold Bullion Bar 1oz',
        'GOLDBAR1000000': 'Gold Bullion Bar 10oz',
        'KILOBARGOLD000': 'Gold Bullion Bar 1kg',
        'GOLDBAR1C00000': 'Gold Bullion Bar 100oz',
        'SUDB1000000000': 'Silver Bullion Bar 10oz',
        'SUDB0100000000': 'Silver Bullion Bar 1oz',
        'SUDB1C00000000': 'Silver Bullion Bar 100oz',
        'SUEG0100000000': 'Silver American Eagle Coin 1oz',
        'SCML0100000000': 'Silver Canadian Maple Leaf 1oz',
        'SUDN0100000000': 'Silver Bullion Round 1oz',
        'PALCMP01000000': 'Palladium Canadian Maple Leaf 1oz',
        'PALLADIUM01000': 'Palladium Bullion Bars 1oz',
        'PALLADIUM00100': 'Palladium Bullion Bars 10oz',
        'PALLADIUM1C000': 'Palladium Bullion Bars 100oz',
        'PGUEG010000000': 'Platinum American Eagle 1oz',
        'PCML0100000000': 'Platinum Canadian Maple Leaf 1oz',
        'PLATINUM010000': 'Platinum Bullion Bar 1oz',
        'PUEB1000000000': 'Platinum Bullion Bar 10oz',
    }
    ratio_trades['ITEM_CODE'].replace(item_code_name_mapping, inplace=True)
    return ratio_trades

