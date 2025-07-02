import pandas as pd
from datetime import datetime


def leadboard_func(data):
    replace_mapping = {
        'TMG': 'grp_1_tory',
        'MA': 'grp_1_arries',
        'JAD': 'grp_1_dobesh',
        'JGE': 'grp_1_etz',
        'RVG': 'grp_1_goodin',
        'MG': 'grp_1_miles',
        'MRH': 'mike grp_1_horsey',
        'ROB': 'grp_1_mclaughlin',
        'KBO': 'grp_1_orrick',
        'GST': 'grp_1_streets',
        'SPC': 'grp_1_steve',
        'SMS': 'grp_1_shayla',
        'JDB': 'grp_1_josh'
    }

    ###monehtly sales
    buy_trades = data[data['TRADE_TYPE'] == 'B']
    current_month = datetime.now().month
    current_month_trades = buy_trades[buy_trades['TD'].dt.month == current_month]
    monehtly_leaderboard_data = current_month_trades.groupby('TRADER')['EXTENDED'].sum().reset_index()
    monthly_leaderboard_data = monehtly_leaderboard_data.sort_values(by='EXTENDED', ascending=False).reset_index(drop=True)


    ##########YTD sales
    ytd_trades = data[data['TRADE_TYPE'] == 'B']
    current_year = datetime.now().year
    current_year_trades = ytd_trades[ytd_trades['TD'].dt.year == current_year]
    year_leaderboard_data= current_year_trades.groupby('TRADER')['EXTENDED'].sum().reset_index()
    year_leaderboard_data = year_leaderboard_data.sort_values(by='EXTENDED', ascending=False).reset_index(drop=True)



    #### rare coin monthly
    current_month_rare_trades = current_month_trades[current_month_trades['TRADE_NUM'].str.contains('R')]
    monthly_leaderboard_rare = current_month_rare_trades.groupby('TRADER')['EXTENDED'].sum().reset_index()


    #### rare coin ytd
    current_year_rare_trades = current_year_trades[current_year_trades['TRADE_NUM'].str.contains('R')]
    year_leaderboard_rare = current_year_rare_trades.groupby('TRADER')['EXTENDED'].sum().reset_index()
    year_leaderboard_rare = year_leaderboard_rare.sort_values(by='EXTENDED', ascending=False).reset_index(drop=True)


    return monthly_leaderboard_data, year_leaderboard_data, monthly_leaderboard_rare, year_leaderboard_rare


