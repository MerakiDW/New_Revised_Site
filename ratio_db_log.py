import pandas as pd
import numpy as np
import requests
import time
from bs4 import BeautifulSoup
import datetime
import os
from .item_codes import item_code_mapping
import re

pd.options.display.float_format = "{:,.3f}".format
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 50)

def ratio_trades_func(historical_data):
    def gold_product_bid_ask(num_range):

        ###webscraper
        url = "https://bullionvalues.org/WebService/BVDataService.asmx/GetCurrentGoldPricing"

        payload = {
            "startRowIndex": 0,
            "maximumRows": 100,
            "sortExpression": [],
            "filterExpression": []
        }
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Host": "bullionvalues.org",
            "Origin": "https://bullionvalues.org",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
            "Connection": "keep-alive",
            "Referer": "https://bullionvalues.org/",
            "Content-Length": "79",
            "Cookie": "ASP.NET_SessionId=hv5z3jlvpzngew0qfmrynrwb",
            "X-Requested-With": "XMLHttpRequest"
        }
        response = requests.request("POST", url, json=payload, headers=headers)
        bid_ask_list = ['GenericPricing_Product','GenericPricing_BidPrice', 'GenericPricing_AskPrice']
        product_list = []

        for data_num in range(num_range):
            for bid_ask in bid_ask_list:
                if bid_ask == 'GenericPricing_Product':
                    product_name = response.json()['d']['Data'][data_num][bid_ask]
                    patterns_to_remove = ["ISO", "Accredited", "9995", "Pre1965", "1965-1969", "995", "9999", "*", "-", "%"]
                    product_name = re.sub(r'\(.*?\)', '', product_name)
                    for pattern in patterns_to_remove:
                        product_name = product_name.replace(pattern, "")
                        product_name = product_name.replace("(", " ")
                        product_name = product_name.replace(")", " ")

                        # Replace other characters with underscores
                        product_name = product_name.replace("/", "_")
                        product_name = product_name.replace(".", "_")
                        product_name = product_name.replace(" ", "_")

                        # Remove consecutive underscores
                        while "__" in product_name:
                            product_name = product_name.replace("__", "_")

                        if product_name.endswith("_"):
                            product_name = product_name[:-1]

                        product_name = product_name.replace("U_S", "US")

                    product_list.append(product_name)

                else:
                    
                    product_val = response.json()['d']['Data'][data_num][bid_ask]
                    product_val_clean = ('').join(product_val[0:].split(','))
                    product_float = float(product_val_clean)
                    if data_num == 18:
                        product_float = product_float*100
                        product_list.append(product_float)
                    else:
                        product_list.append(product_float)
                        
        
        return product_list



    gold_product_bid_ask(19)

    gold_df = pd.DataFrame({'Metal': gold_product_bid_ask(19)[::3], 'Bid': gold_product_bid_ask(19)[1::3], 'Ask': gold_product_bid_ask(19)[2::3]}).set_index('Metal').T
    gold_df.columns.name = None
    gold_df


    def silver_product_bid_ask(num_range):

        ###webscraper
        url2 = "https://bullionvalues.org/WebService/BVDataService.asmx/GetCurrentSilverPricing"

        payload = {
            "startRowIndex": 0,
            "maximumRows": 100,
            "sortExpression": [],
            "filterExpression": []
        }
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Host": "bullionvalues.org",
            "Origin": "https://bullionvalues.org",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
            "Connection": "keep-alive",
            "Referer": "https://bullionvalues.org/",
            "Content-Length": "79",
            "Cookie": "ASP.NET_SessionId=hv5z3jlvpzngew0qfmrynrwb",
            "X-Requested-With": "XMLHttpRequest"
        }

        response = requests.request("POST", url2, json=payload, headers=headers)

        bid_ask_list = ['GenericPricing_Product','GenericPricing_BidPrice', 'GenericPricing_AskPrice']
        product_list = []

        for data_num in range(num_range):
            for bid_ask in bid_ask_list:
                if bid_ask == 'GenericPricing_Product':
                    product_name = response.json()['d']['Data'][data_num][bid_ask]
                    patterns_to_remove = ["ISO", "Accredited", "9995", "Pre1965", "1965-1969", "995", "9999", "*", "-", "%"]
                    product_name = re.sub(r'\(.*?\)', '', product_name)
                    for pattern in patterns_to_remove:
                        product_name = product_name.replace(pattern, "")
                        product_name = product_name.replace("(", " ")
                        product_name = product_name.replace(")", " ")

                        # Replace other characters with underscores
                        product_name = product_name.replace("/", "_")
                        product_name = product_name.replace(".", "_")
                        product_name = product_name.replace(" ", "_")

                        # Remove consecutive underscores
                        while "__" in product_name:
                            product_name = product_name.replace("__", "_")

                        if product_name.endswith("_"):
                            product_name = product_name[:-1]

                        product_name = product_name.replace("U_S", "US")

                    product_list.append(product_name)

                else:
                    
                    product_val = response.json()['d']['Data'][data_num][bid_ask]
                    product_val_clean = ('').join(product_val[0:].split(','))
                    product_float = float(product_val_clean)
                    if data_num == 7:
                        product_float = product_float*100
                        product_list.append(product_float)
                    else:
                        product_list.append(product_float)
        return product_list

    silver_product_bid_ask(10)


    silver_df = pd.DataFrame({'Metal': silver_product_bid_ask(10)[::3], 'Bid': silver_product_bid_ask(10)[1::3], 'Ask': silver_product_bid_ask(10)[2::3]}).set_index('Metal').T
    silver_df.columns.name = None
    silver_df

    def palladium_product_bid_ask(num_range):

        ###webscraper
        url3 = "https://bullionvalues.org/WebService/BVDataService.asmx/GetCurrentPalladiumPricing"

        payload = {
            "startRowIndex": 0,
            "maximumRows": 100,
            "sortExpression": [],
            "filterExpression": []
        }
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Host": "bullionvalues.org",
            "Origin": "https://bullionvalues.org",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
            "Connection": "keep-alive",
            "Referer": "https://bullionvalues.org/",
            "Content-Length": "79",
            "Cookie": "ASP.NET_SessionId=hv5z3jlvpzngew0qfmrynrwb",
            "X-Requested-With": "XMLHttpRequest"
        }

        response = requests.request("POST", url3, json=payload, headers=headers)

        bid_ask_list = ['GenericPricing_Product','GenericPricing_BidPrice', 'GenericPricing_AskPrice']
        product_list = []

        for data_num in range(num_range):
            for bid_ask in bid_ask_list:
                if bid_ask == 'GenericPricing_Product':
                    product_name = response.json()['d']['Data'][data_num][bid_ask]
                    patterns_to_remove = ["ISO", "Accredited", "9995", "Pre1965", "1965-1969", "995", "9999", "*", "-", "%"]
                    product_name = re.sub(r'\(.*?\)', '', product_name)
                    for pattern in patterns_to_remove:
                        product_name = product_name.replace(pattern, "")
                        product_name = product_name.replace("(", " ")
                        product_name = product_name.replace(")", " ")

                        # Replace other characters with underscores
                        product_name = product_name.replace("/", "_")
                        product_name = product_name.replace(".", "_")
                        product_name = product_name.replace(" ", "_")

                        # Remove consecutive underscores
                        while "__" in product_name:
                            product_name = product_name.replace("__", "_")

                        if product_name.endswith("_"):
                            product_name = product_name[:-1]

                        product_name = product_name.replace("U_S", "US")

                    product_list.append(product_name)

                else:
                    
                    product_val = response.json()['d']['Data'][data_num][bid_ask]
                    product_val_clean = ('').join(product_val[0:].split(','))
                    product_float = float(product_val_clean)
                    if data_num == 4:
                        product_float = product_float*100
                        product_list.append(product_float)
                    else:
                        product_list.append(product_float)
        

        return product_list

    palladium_product_bid_ask(5)

    palladium_df = pd.DataFrame({'Metal': palladium_product_bid_ask(5)[::3], 'Bid': palladium_product_bid_ask(5)[1::3], 'Ask': palladium_product_bid_ask(5)[2::3]}).set_index('Metal').T
    palladium_df.columns.name = None
    palladium_df

    def paltinum_product_bid_ask(num_range):

        ###webscraper
        url4 = "https://bullionvalues.org/WebService/BVDataService.asmx/GetCurrentPlatinumPricing"

        payload = {
            "startRowIndex": 0,
            "maximumRows": 100,
            "sortExpression": [],
            "filterExpression": []
        }
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Host": "bullionvalues.org",
            "Origin": "https://bullionvalues.org",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
            "Connection": "keep-alive",
            "Referer": "https://bullionvalues.org/",
            "Content-Length": "79",
            "Cookie": "ASP.NET_SessionId=hv5z3jlvpzngew0qfmrynrwb",
            "X-Requested-With": "XMLHttpRequest"
        }

        response = requests.request("POST", url4, json=payload, headers=headers)


        bid_ask_list = ['GenericPricing_Product','GenericPricing_BidPrice', 'GenericPricing_AskPrice']
        product_list = []

        for data_num in range(num_range):
            for bid_ask in bid_ask_list:
                if bid_ask == 'GenericPricing_Product':
                    product_name = response.json()['d']['Data'][data_num][bid_ask]
                    patterns_to_remove = ["ISO", "Accredited", "9995", "Pre1965", "1965-1969", "995", "9999", "*", "-", "%"]
                    product_name = re.sub(r'\(.*?\)', '', product_name)
                    for pattern in patterns_to_remove:
                        product_name = product_name.replace(pattern, "")
                        product_name = product_name.replace("(", " ")
                        product_name = product_name.replace(")", " ")

                        # Replace other characters with underscores
                        product_name = product_name.replace("/", "_")
                        product_name = product_name.replace(".", "_")
                        product_name = product_name.replace(" ", "_")

                        # Remove consecutive underscores
                        while "__" in product_name:
                            product_name = product_name.replace("__", "_")

                        if product_name.endswith("_"):
                            product_name = product_name[:-1]

                        product_name = product_name.replace("U_S", "US")

                    
                    product_list.append(product_name)

                else:
                    
                    product_val = response.json()['d']['Data'][data_num][bid_ask]
                    product_val_clean = ('').join(product_val[0:].split(','))
                    product_float = float(product_val_clean)
                    if data_num == 5:
                        product_float = product_float*50
                        product_list.append(product_float)
                    else:
                        product_list.append(product_float)
        

        return product_list

    paltinum_product_bid_ask(6)


    #### makes current ratios
    platinum_df = pd.DataFrame({'Metal': paltinum_product_bid_ask(6)[::3], 'Bid': paltinum_product_bid_ask(6)[1::3], 'Ask': paltinum_product_bid_ask(6)[2::3]}).set_index('Metal').T
    platinum_df.columns.name = None
    platinum_df

    metals_df = pd.merge(gold_df, silver_df, left_index=True, right_index=True)
    metals_df = pd.merge(metals_df, platinum_df, left_index=True, right_index=True)
    metals_df = pd.merge(metals_df, palladium_df, left_index=True, right_index=True)


    metals_ratio = pd.DataFrame()

    for product in metals_df.columns:
        ratio_row_list = []
        for prod2 in metals_df.columns:
            if product == prod2:
                const_append = metals_df[product].iloc[0]/metals_df[product].iloc[0]
                ratio_row_list.append(const_append)

            else:
                ratio_append = metals_df[product].iloc[0]/metals_df[prod2].iloc[1]
                ratio_row_list.append(ratio_append)
        metals_ratio[product] = ratio_row_list
        
    metals_ratio.set_index(metals_df.columns, inplace=True)
    
        

    metals_ratio = metals_ratio.T
    metals_ratio.index.name = 'product_index'
    



    # print(metals_ratio)
    # metals_ratio.to_csv('current_ratios.csv')
    ####
    ### 
    historical_data['Gold_Bullion_Bar_100_oz']*=100
    historical_data['Silver_Bullion_Bar_1000_oz']*=1000
    historical_data['Platinum_Bullion_Bars_50_oz']*=50
    historical_data['Palladium_Bullion_Bars_100_oz']*=100
    
    return historical_data, metals_ratio




