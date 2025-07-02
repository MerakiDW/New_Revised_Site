import pandas as pd
import numpy as np
import time
import datetime
from .item_codes import item_code_mapping

def ratio_trade_calculations(portfolio_data, historical_data, current_product_ratios, client_data):
    ##### FIX INHERITANCDE ISSUE
    updated_client_broker_pairs = dict(zip(client_data['LeadNumbers'], client_data['BrokerNum']))
    portfolio_data['TRADE_BROKER'] = portfolio_data.apply(lambda row: updated_client_broker_pairs.get(row['CLIENT_NUM'], row['TRADE_BROKER']), axis=1)

    
    # current_product_ratios.set_index('product_index', inplace=True)
    historical_data.set_index('TD', inplace=True)
    portfolio_data.set_index('TD', inplace=True)
    current_product_ratios.set_index('product_index', inplace=True)

    portfolio_data.drop(columns=['id'], inplace=True)
    historical_data.drop(columns=['id'], inplace=True)
    current_product_ratios.drop(columns=['id'], inplace=True)
    # print(portfolio_data)
    portfolio_merge = portfolio_data.merge(historical_data, left_index=True, right_index=True, how='left')
    # print(portfolio_merge)
    portfolio_merge['ITEM_CODE'] = portfolio_merge['ITEM_CODE'].replace(item_code_mapping)

    unit_price_column = portfolio_merge['UNIT_PRICE']
    for column_index in range(8 + 1, len(portfolio_merge.columns)):
        portfolio_merge.iloc[:, column_index] = unit_price_column.div(portfolio_merge.iloc[:, column_index], axis=0)

    # print(portfolio_merge)
    portfolio_merge = portfolio_merge[portfolio_merge['UNIT_PRICE'] != 0]
    portfolio_merge.reset_index(inplace=True)
    # print(portfolio_merge)
    item_code_to_index = {
        'none': 'Gold_Bulk_Generic_Bullion',
        'GUEG0100000000': 'Gold_American_Eagle_1_oz',
        'GUEGHO00000000': 'Gold_American_Eagle_1_2_oz',
        'GUEGQO00000000': 'Gold_American_Eagle_1_4_oz',
        'GUEGTO00000000': 'Gold_American_Eagle_1_10_oz',
        'BUFFALOGOLD000': 'Gold_American_Buffalo_1_oz',
        'GCML0100000000': 'Gold_Canadian_Maple_Leaf_1_oz',
        'GCMLTO00000000': 'Gold_Canadian_Maple_Leaf_1_10_oz',
        'GSKR0100000000': 'Gold_South_African_Krugerrand_1_oz',
        'GLKN0100000000': 'Gold_Australian_Kangaroo_1_oz',
        'PHILHARMONICS0': 'Gold_Austrian_Philharmonic_1_oz',
        'PHILHARMONICQO': 'Gold_Austrian_Philharmonic_1_4_oz',
        'PHILHARMONICTO': 'Gold_Austrian_Philharmonic_1_10_oz',
        'none': 'Gold_Mexican_Fifty_Peso_1_2_oz',
        'none': 'Gold_Austrian_Corona_9802_oz',
        'GOLDBAR0100000': 'Gold_Bullion_Bar_1oz',
        'GOLDBAR1000000': 'Gold_Bullion_Bar_10oz',
        'KILOBARGOLD000': 'Gold_Bullion_Bar_1_kg',
        'GOLDBAR1C00000': 'Gold_Bullion_Bar_100_oz',
        'SUDB1000000000': 'Silver_Bullion_Bar_10_oz',
        'SUDB0100000000': 'Silver_Bullion_Bar_1_oz',
        'SUDB1C00000000': 'Silver_Bullion_Bar_100_oz',
        'none': 'Silver_Bulk_Generic_Bullion',
        'SUEG0100000000': 'Silver_American_Eagle_Coin_1_oz',
        'SCML0100000000': 'Silver_Canadian_Maple_Leaf_1_oz',
        'SUDN0100000000': 'Silver_Bullion_Round_1_oz',
        'none': 'Silver_Bullion_Bar_1000_oz',
        'none': 'US_40_Silver_Coinage_295_oz',
        'none': 'US_90_Silver_Coinage_715_oz',
        'none': 'Platinum_Bulk_Generic_Bullion',
        'PGUEG010000000': 'Platinum_American_Eagle_1_oz',
        'PCML0100000000': 'Platinum_Canadian_Maple_Leaf_1_oz',
        'PLATINUM010000': 'Platinum_Bullion_Bar_1_oz',
        'PUEB1000000000': 'Platinum_Bullion_Bar_10_oz',
        'none': 'Platinum_Bullion_Bars_50_oz',
        'none': 'Palladium_Bulk_Generic_Bullion',
        'PALCMP01000000': 'Palladium_Canadian_Maple_Leaf_1_oz',
        'PALLADIUM01000': 'Palladium_Bullion_Bars_1_oz',
        'PALLADIUM00100': 'Palladium_Bullion_Bars_10_oz',
        'PALLADIUM1C000': 'Palladium_Bullion_Bars_100_oz'
    }
    
    # print(current_product_ratios)
    for index, row in portfolio_merge.iterrows():
        item_code = row['ITEM_CODE']
        
        
        if item_code in item_code_to_index:
            # print(item_code)
            index_name = item_code_to_index[item_code]
 
            # Find the corresponding row in 'metals_ratio' using the index name
            ratio_row = current_product_ratios.loc[index_name]
            portfolio_ratios = row.iloc[10:]

            for i, (ratio_value, portfolio_value) in enumerate(zip(ratio_row, portfolio_ratios)):
                # Skip the division if portfolio_value is 0 or NaN
                if portfolio_value == 0 or pd.isna(portfolio_value):
                    continue

                else: 
                    condition_results = ((ratio_value - portfolio_value) / portfolio_value) * 100

                    portfolio_merge.at[index, portfolio_merge.columns[10 + i]] = condition_results


     
    portfolio_calculation = portfolio_merge[portfolio_merge['ITEM_CODE'].isin(item_code_to_index)]
    portfolio_calculation.iloc[:, 10:] = portfolio_calculation.iloc[:, 10:].round(2)
    # print(portfolio_calculation)
    # portfolio_calculation.to_csv('ratios_final.csv')
    return portfolio_calculation
