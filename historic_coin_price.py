import pandas as pd
import numpy as np
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import re


def historical_price_daily():

    today_date = datetime.today().strftime('%Y-%m-%d')

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
        bid_product_list = []
        ask_product_list = []

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

                    bid_product_list.append(product_name)
                    ask_product_list.append(product_name)

                if bid_ask == 'GenericPricing_BidPrice':
                    bid_product_val = response.json()['d']['Data'][data_num][bid_ask]
                    bid_product_val_clean = ('').join(bid_product_val[0:].split(','))
                    bid_product_float = float(bid_product_val_clean)
                    bid_product_list.append(bid_product_float)

                if bid_ask == 'GenericPricing_AskPrice':
                    ask_product_val = response.json()['d']['Data'][data_num][bid_ask]
                    ask_product_val_clean = ('').join(ask_product_val[0:].split(','))
                    ask_product_float = float(ask_product_val_clean)
                    ask_product_list.append(ask_product_float)

        
        return bid_product_list, ask_product_list



    gold_bid_list, gold_ask_list = gold_product_bid_ask(19)
    gold_bid_products = gold_bid_list[::2]
    gold_bid_prices = gold_bid_list[1::2]

    gold_ask_products = gold_ask_list[::2]
    gold_ask_prices = gold_ask_list[1::2]

    gold_bid_df = pd.DataFrame({product: [float(price)] for product, price in zip(gold_bid_products, gold_bid_prices)})
    gold_bid_df['TD'] = today_date

    gold_ask_df = pd.DataFrame({product: [float(price)] for product, price in zip(gold_ask_products, gold_ask_prices)})
    gold_ask_df['TD'] = today_date
    

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
        bid_product_list = []
        ask_product_list = []

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

                    bid_product_list.append(product_name)
                    ask_product_list.append(product_name)

                if bid_ask == 'GenericPricing_BidPrice':
                    bid_product_val = response.json()['d']['Data'][data_num][bid_ask]
                    bid_product_val_clean = ('').join(bid_product_val[0:].split(','))
                    bid_product_float = float(bid_product_val_clean)
                    bid_product_list.append(bid_product_float)

                if bid_ask == 'GenericPricing_AskPrice':
                    ask_product_val = response.json()['d']['Data'][data_num][bid_ask]
                    ask_product_val_clean = ('').join(ask_product_val[0:].split(','))
                    ask_product_float = float(ask_product_val_clean)
                    ask_product_list.append(ask_product_float)

        
        return bid_product_list, ask_product_list

    silver_bid_list, silver_ask_list = silver_product_bid_ask(10)
    silver_bid_products = silver_bid_list[::2]
    silver_bid_prices = silver_bid_list[1::2]

    silver_ask_products = silver_ask_list[::2]
    silver_ask_prices = silver_ask_list[1::2]

    silver_bid_df = pd.DataFrame({product: [float(price)] for product, price in zip(silver_bid_products, silver_bid_prices)})
    silver_bid_df['TD'] = today_date

    silver_ask_df = pd.DataFrame({product: [float(price)] for product, price in zip(silver_ask_products, silver_ask_prices)})
    silver_ask_df['TD'] = today_date

   

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
        bid_product_list = []
        ask_product_list = []

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

                    bid_product_list.append(product_name)
                    ask_product_list.append(product_name)

                if bid_ask == 'GenericPricing_BidPrice':
                    bid_product_val = response.json()['d']['Data'][data_num][bid_ask]
                    bid_product_val_clean = ('').join(bid_product_val[0:].split(','))
                    bid_product_float = float(bid_product_val_clean)
                    bid_product_list.append(bid_product_float)

                if bid_ask == 'GenericPricing_AskPrice':
                    ask_product_val = response.json()['d']['Data'][data_num][bid_ask]
                    ask_product_val_clean = ('').join(ask_product_val[0:].split(','))
                    ask_product_float = float(ask_product_val_clean)
                    ask_product_list.append(ask_product_float)

        
        return bid_product_list, ask_product_list

    pallad_bid_list, pallad_ask_list = palladium_product_bid_ask(5)
    pallad_bid_products = pallad_bid_list[::2]
    pallad_bid_prices = pallad_bid_list[1::2]

    pallad_ask_products = pallad_ask_list[::2]
    pallad_ask_prices = pallad_ask_list[1::2]
    
    pallad_bid_df = pd.DataFrame({product: [float(price)] for product, price in zip(pallad_bid_products, pallad_bid_prices)})
    pallad_bid_df['TD'] = today_date

    pallad_ask_df = pd.DataFrame({product: [float(price)] for product, price in zip(pallad_ask_products, pallad_ask_prices)})
    pallad_ask_df['TD'] = today_date


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
        bid_product_list = []
        ask_product_list = []

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

                    bid_product_list.append(product_name)
                    ask_product_list.append(product_name)

                if bid_ask == 'GenericPricing_BidPrice':
                    bid_product_val = response.json()['d']['Data'][data_num][bid_ask]
                    bid_product_val_clean = ('').join(bid_product_val[0:].split(','))
                    bid_product_float = float(bid_product_val_clean)
                    bid_product_list.append(bid_product_float)

                if bid_ask == 'GenericPricing_AskPrice':
                    ask_product_val = response.json()['d']['Data'][data_num][bid_ask]
                    ask_product_val_clean = ('').join(ask_product_val[0:].split(','))
                    ask_product_float = float(ask_product_val_clean)
                    ask_product_list.append(ask_product_float)

        
        return bid_product_list, ask_product_list

    plat_bid_list, plat_ask_list = paltinum_product_bid_ask(6)
    plat_bid_products = plat_bid_list[::2]
    plat_bid_prices = plat_bid_list[1::2]

    plat_ask_products = plat_ask_list[::2]
    plat_ask_prices = plat_ask_list[1::2]

    
    plat_bid_df = pd.DataFrame({product: [float(price)] for product, price in zip(plat_bid_products, plat_bid_prices)})
    plat_bid_df['TD'] = today_date

    plat_ask_df = pd.DataFrame({product: [float(price)] for product, price in zip(plat_ask_products, plat_ask_prices)})
    plat_ask_df['TD'] = today_date

    # print(gold_bid_df.columns)
    # print(silver_bid_df.columns)
    # print(pallad_bid_df.columns)
    # print(plat_bid_df.columns)

    bid_merged_df = pd.merge(gold_bid_df, silver_bid_df, on='TD').merge(plat_bid_df, on='TD').merge(pallad_bid_df, on='TD')
    ask_merged_df = pd.merge(gold_ask_df, silver_ask_df, on='TD').merge(plat_ask_df, on='TD').merge(pallad_ask_df, on='TD')
    # print(bid_merged_df.head(1))
    return bid_merged_df,ask_merged_df

