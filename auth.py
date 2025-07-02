from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, jsonify
from .models import User, InboundPerformanceData, OutboundPerformanceData, TradesTable, LeadsTable, ClientsTable, HistoricalCoinPriceBid, HistoricalCoinPriceAsk, Updated_Portfolio, ToggleState, CurrentCoinRatios, RatioTradesTable
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from flask.logging import default_handler
#add logging info 
import pandas as pd
from .leaderboard import leadboard_func
from .ratiotrades import display_ratio_trades
from .mpm_performance import intermedia_api
from threading import Thread 
from .ratio_db_log import ratio_trades_func
from .portfolio_sort import portfolio_sorting
# from . import db
from datetime import datetime, timedelta
from pytz import timezone
import time
from .ratio_calculations import ratio_trade_calculations
from .item_codes import item_name_swap
from .historic_coin_price import historical_price_daily


verified_emails = ['koa@mcalvany.com', 'tory@mcalvany.com', 'michael@mcalvany.com']
mwm_verified = ['<User 1>']
mpm_verified = ['<User 1>', '<User 2>', '<User 2>']
admin_verified = ['<User 1>']

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        # app.logger('user= '+user)
        if user:
            if email in verified_emails:
                if check_password_hash(user.password, password):
                    flash('Logged in successfully!', category='success')
                    login_user(user, remember=False)
                    return redirect(url_for('views.home'))
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Accesss Denied, Contact Admin', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


def read_csv_file(file_path):
    df = pd.read_csv(file_path)
    return df


@auth.route('/mcalvanypm', methods=['GET','POST'])
@login_required
def mcalvany_pm():
    if current_user.is_authenticated:
        # file_path = '/Users/koahiggins/Desktop/test_excel.csv'
        # dataframe = read_csv_file(file_path)
        

        return render_template('MPM.html', user=current_user)
    else:
        flash('Access Denied, Contact Admin', category='error')
        return redirect(url_for('views.home'))
    

@auth.route('/leaderboard', methods=['GET','POST'])
@login_required
def leaderboard_mpm():
    if current_user.is_authenticated and current_user.is_broker() or current_user.is_authenticated and current_user.is_admin():
        broker_group = current_user.group_identifier
        trade_data = pd.read_sql_table('trades_table', db.engine)
        trader_values_to_keep = ['TMG', 'MA', 'JAD', 'JGE', 'RVG', 'MG', 'MRH', 'ROB', 'KBO', 'GST', 'SPC', 'SMS', 'JDB']
        replace_mapping = {
            'TMG': 'tory',
            'MA': 'arries',
            'JAD': 'jeff',
            'JGE': 'etz',
            'RVG': 'goodin',
            'MG': 'miles',
            'MRH': 'mike horsey',
            'ROB': 'mclaughlin',
            'KBO': 'kevin',
            'GST': 'genson',
            'SPC': 'steve',
            'SMS': 'shayla',
            'JDB': 'josh'
        }
        trade_data = trade_data[trade_data['TRADER'].isin(trader_values_to_keep)]
        trade_data['TRADER'] = trade_data['TRADER'].replace(replace_mapping)
        
        leaderboard_data, leaderboard_data1, leaderboard_data2, leaderboard_data3 = leadboard_func(trade_data)
        

        return render_template('leaderboard.html', user=current_user, leaderboard_data=leaderboard_data, leaderboard_data1=leaderboard_data1, leaderboard_data2=leaderboard_data2, leaderboard_data3=leaderboard_data3,)
    else:
        flash('Access Denied, Contact Admin', category='error')
        return redirect(url_for('views.home'))
    


@auth.route('/performance', methods=['GET','POST'])
@login_required
def performance_mpm():
    if current_user.is_authenticated and (current_user.is_broker() or current_user.is_admin()):

        def sec_to_hours(seconds):
            a=str(seconds//3600)
            b=str((seconds%3600)//60)
            c=str((seconds%3600)%60)
            d='{}h {}m {}s'.format(a, b, c)
            return d

        last_call_timestamp = session.get('last_api_call_timestamp')
        tz = timezone('UTC')
        
        current_time = datetime.now(tz)
        if last_call_timestamp is not None and (current_time - last_call_timestamp) < timedelta(hours=1):
            print(f'cannot make api call until {current_time - last_call_timestamp}')
            inbound_ops = pd.read_sql_table('inbound_performance_data', db.engine)
            outbound_ops = pd.read_sql_table('outbound_performance_data', db.engine)
            sales_data = pd.read_sql_table('trades_table', db.engine)
            leads_data = pd.read_sql_table('leads_table', db.engine)
            clients_data = pd.read_sql_table('clients_table', db.engine)
            current_broker_number = current_user.broker_number
            

            #leads + clients
            client_total = 'Select Date Range'
            vaulted_total = 'Select Date Range'
            leads_total = 'Select Date Range'
            new_leads = 'Select Date Range'
            new_clients = 'Select Date Range'
            new_vaulted = 'Select Date Range'
            new_client_refs = 'Select Date Range'


            leads_group = leads_data[leads_data['BrokerNum'] == current_broker_number]
            leads_total = (len(leads_group.index))
            total_vaulted_leads = (sum(leads_group['LeadSource'] == 'Vaulted'))
            # print(leads_data)


            clients_group = clients_data[clients_data['BrokerNum'] == current_broker_number]
            client_drop = clients_group[clients_group['LeadSource'].str.contains('Vaulted|Client Referral') == False]
            client_total = (len(client_drop.index))
            client_vaulted_total = (sum(clients_group['LeadSource'] == 'Vaulted'))
            
            vaulted_total = client_vaulted_total+total_vaulted_leads
            



            #sales
            
            keywords = ['ATR', 'DIST', 'EDIT', 'NON']
            
            for keyword in keywords:
                sales_data_drop = sales_data.drop(sales_data[sales_data['TRADE_NUM'].str.contains(keyword)].index)

            sales_data_reg = sales_data_drop.drop(sales_data_drop[sales_data_drop['TRADE_NUM'].str.contains('R')].index)
            sales_data_rare = sales_data_drop[sales_data_drop['TRADE_NUM'].str.contains('R')]

            sales_reg_group = sales_data_reg[sales_data_reg['TRADE_BROKER'] == current_broker_number]
            sales_rare_group = sales_data_rare[sales_data_rare['TRADE_BROKER'] == current_broker_number]

            trade_buy_num = 'Select Date Range'
            trade_sell_num = 'Select Date Range'
            trade_buy_val = 'Select Date Range'
            trade_sell_val = 'Select Date Range' 

            rare_buy_num = 'Select Date Range' 
            rare_sell_num = 'Select Date Range' 
            rare_buy_val = 'Select Date Range' 
            rare_sell_val = 'Select Date Range' 

            #calls
            broker_group = current_user.group_identifier

            call_in_total = 'Select Date Range'
            call_in_duration = 'Select Date Range'
            call_out_total = 'Select Date Range'
            call_out_duration = 'Select Date Range'

        
            if broker_group is not None:
                    #sales
                    temp_var_frontend = 'Maintenance'


                    #calls
                    grouped_outb_data = outbound_ops[outbound_ops['name_out'] == broker_group].reset_index()
                    grouped_inb_data = inbound_ops[inbound_ops['name_in'] == broker_group].reset_index()

                    current_month = datetime.utcnow().month
                    current_year = datetime.utcnow().year

                    data_range_dict = {
                        'January': (1, 1, current_year, 1, 31),  # January
                        'February': (2, 1, current_year, 2, 28),  # February
                        'March': (3, 1, current_year, 3, 31),  # March
                        'April': (4, 1, current_year, 4, 30),  # April
                        'May': (5, 1, current_year, 5, 31),  # May
                        'June': (6, 1, current_year, 6, 30),  # June
                        'July': (7, 1, current_year, 7, 31),  # July
                        'August': (8, 1, current_year, 8, 31),  # August
                        'September': (9, 1, current_year, 9, 30),  # September
                        'October': (10, 1, current_year, 10, 31),  # October
                        'November': (11, 1, current_year, 11, 30),  # November
                        'December': (12, 1, current_year, 12, 31),  # December
                        'Q1': (1, 1, current_year, 3, 31),  # Q1 (January to March)
                        'Q2': (4, 1, current_year, 6, 30),  # Q2 (April to June)
                        'Q3': (7, 1, current_year, 9, 30),  # Q3 (July to September)
                        'Q4': (10, 1, current_year, 12, 31),  # Q4 (October to December)
                        'YTD': (1, 1, current_year, current_month, 31)#datetime.now().day)  # YTD (January to current day)
                    }

                    
                    if request.method == 'POST':
                        date_range = request.form.get('dateRange')
                        posted_month = data_range_dict.get(date_range)
                        if posted_month is not None:
                            start_month, start_day, start_year, end_month, end_day = posted_month

                            inb_data_range = grouped_inb_data[
                                (grouped_inb_data['start_date'].dt.year == start_year) & 
                                (grouped_inb_data['start_date'].dt.month.between(start_month, end_month)) &  
                                (grouped_inb_data['start_date'].dt.day.between(start_day, end_day))
                            ]
                            outb_data_range = grouped_outb_data[
                                (grouped_outb_data['start_date'].dt.year == start_year) & 
                                (grouped_outb_data['start_date'].dt.month.between(start_month, end_month)) & 
                                (grouped_outb_data['start_date'].dt.day.between(start_day, end_day))    
                            ]

                            trades_data_range = sales_reg_group[
                                (sales_reg_group['TD'].dt.year == start_year) & 
                                (sales_reg_group['TD'].dt.month.between(start_month, end_month)) & 
                                (sales_reg_group['TD'].dt.day.between(start_day, end_day))    
                            ]

                            rare_trades_data_range = sales_rare_group[
                                (sales_rare_group['TD'].dt.year == start_year) & 
                                (sales_rare_group['TD'].dt.month.between(start_month, end_month)) & 
                                (sales_rare_group['TD'].dt.day.between(start_day, end_day))    
                            ]

                            
                            leads_data_range = leads_group[
                                (leads_group['Createdate'].dt.year == start_year) & 
                                (leads_group['Createdate'].dt.month.between(start_month, end_month)) & 
                                (leads_group['Createdate'].dt.day.between(start_day, end_day))    
                            ]

                            clients_data_range = clients_group[
                                (clients_group['Createdate'].dt.year == start_year) & 
                                (clients_group['Createdate'].dt.month.between(start_month, end_month)) & 
                                (clients_group['Createdate'].dt.day.between(start_day, end_day))    
                            ]

                            #calls
                            call_in_total = len(inb_data_range)
                            call_in_duration = inb_data_range['duration'].sum()
                            call_in_duration = sec_to_hours(call_in_duration)

                            
                            call_out_total = len(outb_data_range)
                            call_out_duration = outb_data_range['duration'].sum()
                            call_out_duration = sec_to_hours(call_out_duration)

                            #sales
                            trades_data_buy = trades_data_range.drop(trades_data_range[trades_data_range['TRADE_TYPE'].str.contains('S')].index)
                            trades_data_sell = trades_data_range.drop(trades_data_range[trades_data_range['TRADE_TYPE'].str.contains('B')].index)
                            trade_buy_num = (len(trades_data_buy.index))
                            trade_sell_num = (len(trades_data_sell.index))
                            trade_buy_val = "{:,.2f}".format(trades_data_buy['EXTENDED'].sum())
                            trade_sell_val = "{:,.2f}".format(trades_data_sell['EXTENDED'].sum())

                            rare_data_buy = rare_trades_data_range.drop(rare_trades_data_range[rare_trades_data_range['TRADE_TYPE'].str.contains('S')].index)
                            rare_data_sell = rare_trades_data_range.drop(rare_trades_data_range[rare_trades_data_range['TRADE_TYPE'].str.contains('B')].index)
                            rare_buy_num = (len(rare_data_buy.index))
                            rare_sell_num = (len(rare_data_sell.index))
                            rare_buy_val = "{:,.2f}".format(rare_data_buy['EXTENDED'].sum())
                            rare_sell_val = "{:,.2f}".format(rare_data_sell['EXTENDED'].sum())

                            #clients + leads
                            new_clients = (len(clients_data_range.index))
                            new_leads = (len(leads_data_range.index))
                            new_vaulted = (sum(leads_data_range['LeadSource'] == 'Vaulted'))
                            new_client_refs = (sum(clients_data_range['LeadSource'] == 'Client Referral'))
                            





            return render_template('performance.html', user=current_user, new_client_refs=new_client_refs, new_vaulted=new_vaulted, new_leads=new_leads, new_clients=new_clients, leads_total=leads_total,vaulted_total=vaulted_total, client_total=client_total ,call_in_total=call_in_total, call_in_duration=call_in_duration, call_out_total=call_out_total, call_out_duration=call_out_duration, trade_buy_num=trade_buy_num, trade_sell_num=trade_sell_num,trade_buy_val=trade_buy_val,trade_sell_val=trade_sell_val,rare_buy_num=rare_buy_num,rare_sell_num=rare_sell_num,rare_buy_val=rare_buy_val,rare_sell_val=rare_sell_val,temp_var_frontend=temp_var_frontend)
        else:
            intermedia_data = intermedia_api()

            if intermedia_data == 'XQ90-1':
                print('no new data called')

            else:    
                inbound_df, outbound_df = intermedia_api()

                # Add inbound dataframe to the database
                for _, row in inbound_df.iterrows():
                    inbound_data = InboundPerformanceData(
                        direction=row['Direction'],
                        duration=row['Duration'],
                        from_number=row['From Number'],
                        ring_duration=row['Ring Duration'],
                        start_date=row['Start Date'],
                        to_number=row['To Number'],
                        answered=row['Answered'],
                        user_id_in=row['User_id_in'],
                        name_in=row['Name_in']
                    )
                    db.session.add(inbound_data)
                
                # Add outbound dataframe to the database
                for _, row in outbound_df.iterrows():
                    outbound_data = OutboundPerformanceData(
                        direction=row['Direction'],
                        duration=row['Duration'],
                        from_number=row['From Number'],
                        ring_duration=row['Ring Duration'],
                        start_date=row['Start Date'],
                        to_number=row['To Number'],
                        answered=row['Answered'],
                        name_out=row['Name_out'],
                        user_id_out=row['User_id_out']
                    )
                    db.session.add(outbound_data)
                

                db.session.commit()

            session['last_api_call_timestamp'] = datetime.now(tz)

            inbound_ops = pd.read_sql_table('inbound_performance_data', db.engine)
            outbound_ops = pd.read_sql_table('outbound_performance_data', db.engine)
            
            broker_group = current_user.group_identifier
        
            if broker_group is not None:
                grouped_outb_data = outbound_ops[outbound_ops['name_out'] == broker_group].reset_index()
                grouped_inb_data = inbound_ops[inbound_ops['name_in'] == broker_group].reset_index()

                current_month = datetime.utcnow().month
                current_year = datetime.utcnow().year

                data_range_dict = {
                        'January': (1, 1, current_year, 1, 31),  # January
                        'February': (2, 1, current_year, 2, 28),  # February
                        'March': (3, 1, current_year, 3, 31),  # March
                        'April': (4, 1, current_year, 4, 30),  # April
                        'May': (5, 1, current_year, 5, 31),  # May
                        'June': (6, 1, current_year, 6, 30),  # June
                        'July': (7, 1, current_year, 7, 31),  # July
                        'August': (8, 1, current_year, 8, 31),  # August
                        'September': (9, 1, current_year, 9, 30),  # September
                        'October': (10, 1, current_year, 10, 31),  # October
                        'November': (11, 1, current_year, 11, 30),  # November
                        'December': (12, 1, current_year, 12, 31),  # December
                        'Q1': (1, 1, current_year, 3, 31),  # Q1 (January to March)
                        'Q2': (4, 1, current_year, 6, 30),  # Q2 (April to June)
                        'Q3': (7, 1, current_year, 9, 30),  # Q3 (July to September)
                        'Q4': (10, 1, current_year, 12, 31),  # Q4 (October to December)
                        'YTD': (1, 1, current_year, current_month, 31)#datetime.now().day)  # YTD (January to current day)
                    }

                    
                if request.method == 'POST':
                    date_range = request.form.get('dateRange')
                    posted_month = data_range_dict.get(date_range)
                    if posted_month is not None:
                        start_month, start_day, start_year, end_month, end_day = posted_month

                        inb_data_range = grouped_inb_data[
                                (grouped_inb_data['start_date'].dt.year == start_year) & 
                                (grouped_inb_data['start_date'].dt.month.between(start_month, end_month)) &  
                                (grouped_inb_data['start_date'].dt.day.between(start_day, end_day))
                            ]
                        outb_data_range = grouped_outb_data[
                                (grouped_outb_data['start_date'].dt.year == start_year) & 
                                (grouped_outb_data['start_date'].dt.month.between(start_month, end_month)) & 
                                (grouped_outb_data['start_date'].dt.day.between(start_day, end_day))    
                            ]

                            
                        call_in_total = len(inb_data_range)
                        call_in_duration = inb_data_range['duration'].sum()
                        call_in_duration = sec_to_hours(call_in_duration)

                            
                        call_out_total = len(outb_data_range)
                        call_out_duration = outb_data_range['duration'].sum()
                        call_out_duration = sec_to_hours(call_out_duration)
    
 
            return render_template('performance.html', user=current_user)
            
        

    else:
        flash('Access Denied, Contact Admin', category='error')
        return redirect(url_for('views.home'))


@auth.route('/tradingmpm', methods=['GET','POST'])
@login_required
def trading_mpm():
    if current_user.is_authenticated and current_user.is_broker() or current_user.is_authenticated and current_user.is_admin():
        broker_number = current_user.broker_number
        
        if broker_number is not None:
            trade_data = pd.read_sql_table('trades_table', db.engine)
            portfolio_data = pd.read_sql_table('updated__portfolio', db.engine)
            historical_coin_bid_data = pd.read_sql_table('historical_coin_price_bid', db.engine)
            historical_coin_ask_data = pd.read_sql_table('historical_coin_price_ask', db.engine)
            current_ratios = pd.read_sql_table('current_coin_ratios', db.engine)
            ratios_final = pd.read_sql_table('ratio_trades_table', db.engine)
            clients_data = pd.read_sql_table('clients_table', db.engine)
            update_states = ToggleState.query.all()

            # print(historical_coin_bid_data.columns)

            portfolio_updates = False
            calculation_updates = False

            last_price_timestamp = session.get('last_prices_call_timestamp')
            tz = timezone('UTC')
            current_time = datetime.now(tz)
            if last_price_timestamp is not None and (current_time - last_price_timestamp) > timedelta(hours=1):
                historical_data, current_ratios = ratio_trades_func(historical_coin_bid_data)
                bid_merge_values, ask_merge_values = historical_price_daily()
                # print(bid_merge_values.dtypes)

                db.session.query(CurrentCoinRatios).delete()
                for index, row in current_ratios.iterrows():
  
                    coin_ratio = CurrentCoinRatios(
                        product_index=index,
                        Gold_Bulk_Generic_Bullion=row['Gold_Bulk_Generic_Bullion'],
                        Gold_American_Eagle_1_oz=row['Gold_American_Eagle_1_oz'],
                        Gold_American_Eagle_1_2_oz=row['Gold_American_Eagle_1_2_oz'],
                        Gold_American_Eagle_1_4_oz=row['Gold_American_Eagle_1_4_oz'],
                        Gold_American_Eagle_1_10_oz=row['Gold_American_Eagle_1_10_oz'],
                        Gold_American_Buffalo_1_oz=row['Gold_American_Buffalo_1_oz'],
                        Gold_Canadian_Maple_Leaf_1_oz=row['Gold_Canadian_Maple_Leaf_1_oz'],
                        Gold_Canadian_Maple_Leaf_1_10_oz=row['Gold_Canadian_Maple_Leaf_1_10_oz'],
                        Gold_South_African_Krugerrand_1_oz=row['Gold_South_African_Krugerrand_1_oz'],
                        Gold_Australian_Kangaroo_1_oz=row['Gold_Australian_Kangaroo_1_oz'],
                        Gold_Austrian_Philharmonic_1_oz=row['Gold_Austrian_Philharmonic_1_oz'],
                        Gold_Austrian_Philharmonic_1_4_oz=row['Gold_Austrian_Philharmonic_1_4_oz'],
                        Gold_Austrian_Philharmonic_1_10_oz=row['Gold_Austrian_Philharmonic_1_10_oz'],
                        Gold_Mexican_Fifty_Peso_1_2_oz=row['Gold_Mexican_Fifty_Peso_1_2_oz'],
                        Gold_Austrian_Corona_9802_oz=row['Gold_Austrian_Corona_9802_oz'],
                        Gold_Bullion_Bar_1oz=row['Gold_Bullion_Bar_1oz'],
                        Gold_Bullion_Bar_10oz=row['Gold_Bullion_Bar_10oz'],
                        Gold_Bullion_Bar_1_kg=row['Gold_Bullion_Bar_1_kg'],
                        Gold_Bullion_Bar_100_oz=row['Gold_Bullion_Bar_100_oz'],
                        Silver_Bullion_Bar_10_oz=row['Silver_Bullion_Bar_10_oz'],
                        Silver_Bullion_Bar_1_oz=row['Silver_Bullion_Bar_1_oz'],
                        Silver_Bullion_Bar_100_oz=row['Silver_Bullion_Bar_100_oz'],
                        Silver_Bulk_Generic_Bullion=row['Silver_Bulk_Generic_Bullion'],
                        Silver_American_Eagle_Coin_1_oz=row['Silver_American_Eagle_Coin_1_oz'],
                        Silver_Canadian_Maple_Leaf_1_oz=row['Silver_Canadian_Maple_Leaf_1_oz'],
                        Silver_Bullion_Round_1_oz=row['Silver_Bullion_Round_1_oz'],
                        Silver_Bullion_Bar_1000_oz=row['Silver_Bullion_Bar_1000_oz'],
                        US_40_Silver_Coinage_295_oz=row['US_40_Silver_Coinage_295_oz'],
                        US_90_Silver_Coinage_715_oz=row['US_90_Silver_Coinage_715_oz'],
                        Platinum_Bulk_Generic_Bullion=row['Platinum_Bulk_Generic_Bullion'],
                        Platinum_American_Eagle_1_oz=row['Platinum_American_Eagle_1_oz'],
                        Platinum_Canadian_Maple_Leaf_1_oz=row['Platinum_Canadian_Maple_Leaf_1_oz'],
                        Platinum_Bullion_Bar_1_oz=row['Platinum_Bullion_Bar_1_oz'],
                        Platinum_Bullion_Bar_10_oz=row['Platinum_Bullion_Bar_10_oz'],
                        Platinum_Bullion_Bars_50_oz=row['Platinum_Bullion_Bars_50_oz'],
                        Palladium_Bulk_Generic_Bullion=row['Palladium_Bulk_Generic_Bullion'],
                        Palladium_Canadian_Maple_Leaf_1_oz=row['Palladium_Canadian_Maple_Leaf_1_oz'],
                        Palladium_Bullion_Bars_1_oz=row['Palladium_Bullion_Bars_1_oz'],
                        Palladium_Bullion_Bars_10_oz=row['Palladium_Bullion_Bars_10_oz'],
                        Palladium_Bullion_Bars_100_oz=row['Palladium_Bullion_Bars_100_oz']
                    )

                    db.session.add(coin_ratio)

                current_date = datetime.now().date()
                current_date = datetime.combine(current_date, datetime.min.time())
                # print(current_date)
                historical_bid_update = HistoricalCoinPriceBid.query.filter(HistoricalCoinPriceBid.TD == current_date).first()
                historical_ask_update = HistoricalCoinPriceAsk.query.filter(HistoricalCoinPriceAsk.TD == current_date).first()

                # print(historical_bid_update)
                # temp = False

                if not historical_ask_update:
                    for index, row in ask_merge_values.iterrows():
          
                        TD = datetime.strptime(row['TD'], "%Y-%m-%d")
                        ask_instance = HistoricalCoinPriceAsk(
                            TD=TD,
                            Gold_Bulk_Generic_Bullion=row['Gold_Bulk_Generic_Bullion'],
                            Gold_American_Eagle_1_oz=row['Gold_American_Eagle_1_oz'],
                            Gold_American_Eagle_1_2_oz=row['Gold_American_Eagle_1_2_oz'],
                            Gold_American_Eagle_1_4_oz=row['Gold_American_Eagle_1_4_oz'],
                            Gold_American_Eagle_1_10_oz=row['Gold_American_Eagle_1_10_oz'],
                            Gold_American_Buffalo_1_oz=row['Gold_American_Buffalo_1_oz'],
                            Gold_Canadian_Maple_Leaf_1_oz=row['Gold_Canadian_Maple_Leaf_1_oz'],
                            Gold_Canadian_Maple_Leaf_1_10_oz=row['Gold_Canadian_Maple_Leaf_1_10_oz'],
                            Gold_South_African_Krugerrand_1_oz=row['Gold_South_African_Krugerrand_1_oz'],
                            Gold_Australian_Kangaroo_1_oz=row['Gold_Australian_Kangaroo_1_oz'],
                            Gold_Austrian_Philharmonic_1_oz=row['Gold_Austrian_Philharmonic_1_oz'],
                            Gold_Austrian_Philharmonic_1_4_oz=row['Gold_Austrian_Philharmonic_1_4_oz'],
                            Gold_Austrian_Philharmonic_1_10_oz=row['Gold_Austrian_Philharmonic_1_10_oz'],
                            Gold_Mexican_Fifty_Peso_1_2_oz=row['Gold_Mexican_Fifty_Peso_1_2_oz'],
                            Gold_Austrian_Corona_9802_oz=row['Gold_Austrian_Corona_9802_oz'],
                            Gold_Bullion_Bar_1oz=row['Gold_Bullion_Bar_1oz'],
                            Gold_Bullion_Bar_10oz=row['Gold_Bullion_Bar_10oz'],
                            Gold_Bullion_Bar_1_kg=row['Gold_Bullion_Bar_1_kg'],
                            Gold_Bullion_Bar_100_oz=row['Gold_Bullion_Bar_100_oz'],
                            Silver_Bullion_Bar_10_oz=row['Silver_Bullion_Bar_10_oz'],
                            Silver_Bullion_Bar_1_oz=row['Silver_Bullion_Bar_1_oz'],
                            Silver_Bullion_Bar_100_oz=row['Silver_Bullion_Bar_100_oz'],
                            Silver_Bulk_Generic_Bullion=row['Silver_Bulk_Generic_Bullion'],
                            Silver_American_Eagle_Coin_1_oz=row['Silver_American_Eagle_Coin_1_oz'],
                            Silver_Canadian_Maple_Leaf_1_oz=row['Silver_Canadian_Maple_Leaf_1_oz'],
                            Silver_Bullion_Round_1_oz=row['Silver_Bullion_Round_1_oz'],
                            Silver_Bullion_Bar_1000_oz=row['Silver_Bullion_Bar_1000_oz'],
                            US_40_Silver_Coinage_295_oz=row['US_40_Silver_Coinage_295_oz'],
                            US_90_Silver_Coinage_715_oz=row['US_90_Silver_Coinage_715_oz'],
                            Platinum_Bulk_Generic_Bullion=row['Platinum_Bulk_Generic_Bullion'],
                            Platinum_American_Eagle_1_oz=row['Platinum_American_Eagle_1_oz'],
                            Platinum_Canadian_Maple_Leaf_1_oz=row['Platinum_Canadian_Maple_Leaf_1_oz'],
                            Platinum_Bullion_Bar_1_oz=row['Platinum_Bullion_Bar_1_oz'],
                            Platinum_Bullion_Bar_10_oz=row['Platinum_Bullion_Bar_10_oz'],
                            Platinum_Bullion_Bars_50_oz=row['Platinum_Bullion_Bars_50_oz'],
                            Palladium_Bulk_Generic_Bullion=row['Palladium_Bulk_Generic_Bullion'],
                            Palladium_Canadian_Maple_Leaf_1_oz=row['Palladium_Canadian_Maple_Leaf_1_oz'],
                            Palladium_Bullion_Bars_1_oz=row['Palladium_Bullion_Bars_1_oz'],
                            Palladium_Bullion_Bars_10_oz=row['Palladium_Bullion_Bars_10_oz'],
                            Palladium_Bullion_Bars_100_oz=row['Palladium_Bullion_Bars_100_oz']
                        )
                        db.session.add(ask_instance)
                if not historical_bid_update:
                    for index, row in bid_merge_values.iterrows():
          
                        TD = datetime.strptime(row['TD'], "%Y-%m-%d")
                        bid_instance = HistoricalCoinPriceBid(
                            TD=TD,
                            Gold_Bulk_Generic_Bullion=row['Gold_Bulk_Generic_Bullion'],
                            Gold_American_Eagle_1_oz=row['Gold_American_Eagle_1_oz'],
                            Gold_American_Eagle_1_2_oz=row['Gold_American_Eagle_1_2_oz'],
                            Gold_American_Eagle_1_4_oz=row['Gold_American_Eagle_1_4_oz'],
                            Gold_American_Eagle_1_10_oz=row['Gold_American_Eagle_1_10_oz'],
                            Gold_American_Buffalo_1_oz=row['Gold_American_Buffalo_1_oz'],
                            Gold_Canadian_Maple_Leaf_1_oz=row['Gold_Canadian_Maple_Leaf_1_oz'],
                            Gold_Canadian_Maple_Leaf_1_10_oz=row['Gold_Canadian_Maple_Leaf_1_10_oz'],
                            Gold_South_African_Krugerrand_1_oz=row['Gold_South_African_Krugerrand_1_oz'],
                            Gold_Australian_Kangaroo_1_oz=row['Gold_Australian_Kangaroo_1_oz'],
                            Gold_Austrian_Philharmonic_1_oz=row['Gold_Austrian_Philharmonic_1_oz'],
                            Gold_Austrian_Philharmonic_1_4_oz=row['Gold_Austrian_Philharmonic_1_4_oz'],
                            Gold_Austrian_Philharmonic_1_10_oz=row['Gold_Austrian_Philharmonic_1_10_oz'],
                            Gold_Mexican_Fifty_Peso_1_2_oz=row['Gold_Mexican_Fifty_Peso_1_2_oz'],
                            Gold_Austrian_Corona_9802_oz=row['Gold_Austrian_Corona_9802_oz'],
                            Gold_Bullion_Bar_1oz=row['Gold_Bullion_Bar_1oz'],
                            Gold_Bullion_Bar_10oz=row['Gold_Bullion_Bar_10oz'],
                            Gold_Bullion_Bar_1_kg=row['Gold_Bullion_Bar_1_kg'],
                            Gold_Bullion_Bar_100_oz=row['Gold_Bullion_Bar_100_oz'],
                            Silver_Bullion_Bar_10_oz=row['Silver_Bullion_Bar_10_oz'],
                            Silver_Bullion_Bar_1_oz=row['Silver_Bullion_Bar_1_oz'],
                            Silver_Bullion_Bar_100_oz=row['Silver_Bullion_Bar_100_oz'],
                            Silver_Bulk_Generic_Bullion=row['Silver_Bulk_Generic_Bullion'],
                            Silver_American_Eagle_Coin_1_oz=row['Silver_American_Eagle_Coin_1_oz'],
                            Silver_Canadian_Maple_Leaf_1_oz=row['Silver_Canadian_Maple_Leaf_1_oz'],
                            Silver_Bullion_Round_1_oz=row['Silver_Bullion_Round_1_oz'],
                            Silver_Bullion_Bar_1000_oz=row['Silver_Bullion_Bar_1000_oz'],
                            US_40_Silver_Coinage_295_oz=row['US_40_Silver_Coinage_295_oz'],
                            US_90_Silver_Coinage_715_oz=row['US_90_Silver_Coinage_715_oz'],
                            Platinum_Bulk_Generic_Bullion=row['Platinum_Bulk_Generic_Bullion'],
                            Platinum_American_Eagle_1_oz=row['Platinum_American_Eagle_1_oz'],
                            Platinum_Canadian_Maple_Leaf_1_oz=row['Platinum_Canadian_Maple_Leaf_1_oz'],
                            Platinum_Bullion_Bar_1_oz=row['Platinum_Bullion_Bar_1_oz'],
                            Platinum_Bullion_Bar_10_oz=row['Platinum_Bullion_Bar_10_oz'],
                            Platinum_Bullion_Bars_50_oz=row['Platinum_Bullion_Bars_50_oz'],
                            Palladium_Bulk_Generic_Bullion=row['Palladium_Bulk_Generic_Bullion'],
                            Palladium_Canadian_Maple_Leaf_1_oz=row['Palladium_Canadian_Maple_Leaf_1_oz'],
                            Palladium_Bullion_Bars_1_oz=row['Palladium_Bullion_Bars_1_oz'],
                            Palladium_Bullion_Bars_10_oz=row['Palladium_Bullion_Bars_10_oz'],
                            Palladium_Bullion_Bars_100_oz=row['Palladium_Bullion_Bars_100_oz']
                        )
                        db.session.add(bid_instance)


                db.session.commit()
                

            for state in update_states:
                if state.feature_name == 'feature1' and state.is_enabled == 1:
                    portfolio_updates = True
                if state.feature_name == 'feature2' and state.is_enabled == 1:
                    calculation_updates = True
                

            if portfolio_updates == True:
                Updated_Portfolio.query.delete()
                sorted_portfolio = portfolio_sorting(trade_data)
                for index, row in sorted_portfolio.iterrows():
                    portfolio_entry = Updated_Portfolio(
                        TRADE_NUM=row['TRADE_NUM'],
                        TD=row['TD'],
                        TRADE_TYPE=row['TRADE_TYPE'],
                        CLIENT_NUM=row['CLIENT_NUM'],
                        TRADE_BROKER=row['TRADE_BROKER'],
                        TRADER=row['TRADER'],
                        ITEM_CODE=row['ITEM_CODE'],
                        QUANTITY=row['QUANTITY'],   
                        EXTENDED=row['EXTENDED'],
                        UNIT_PRICE=row['UNIT_PRICE']
                    )
                    db.session.add(portfolio_entry)

                db.session.commit()

            if calculation_updates == True:
                clients_data['LeadNumbers'] = 'C0' + clients_data['LeadNumbers'].astype(str)

                portfolio_calculation = ratio_trade_calculations(portfolio_data, historical_coin_ask_data, current_ratios, clients_data)
                ratio_trades = display_ratio_trades(portfolio_calculation)
                RatioTradesTable.query.delete()
                for index, row in ratio_trades.iterrows():
    
                    ratios_calc = RatioTradesTable(
                        TRADE_NUM=row['TRADE_NUM'],
                        TD=row['TD'],
                        TRADE_TYPE=row['TRADE_TYPE'],
                        CLIENT_NUM=row['CLIENT_NUM'],
                        TRADE_BROKER=row['TRADE_BROKER'],
                        TRADER=row['TRADER'],
                        ITEM_CODE=row['ITEM_CODE'],
                        QUANTITY=row['QUANTITY'],   
                        EXTENDED=row['EXTENDED'],
                        UNIT_PRICE=row['UNIT_PRICE'],
                        Gold_Bulk_Generic_Bullion=row['Gold_Bulk_Generic_Bullion'],
                        Gold_American_Eagle_1_oz=row['Gold_American_Eagle_1_oz'],
                        Gold_American_Eagle_1_2_oz=row['Gold_American_Eagle_1_2_oz'],
                        Gold_American_Eagle_1_4_oz=row['Gold_American_Eagle_1_4_oz'],
                        Gold_American_Eagle_1_10_oz=row['Gold_American_Eagle_1_10_oz'],
                        Gold_American_Buffalo_1_oz=row['Gold_American_Buffalo_1_oz'],
                        Gold_Canadian_Maple_Leaf_1_oz=row['Gold_Canadian_Maple_Leaf_1_oz'],
                        Gold_Canadian_Maple_Leaf_1_10_oz=row['Gold_Canadian_Maple_Leaf_1_10_oz'],
                        Gold_South_African_Krugerrand_1_oz=row['Gold_South_African_Krugerrand_1_oz'],
                        Gold_Australian_Kangaroo_1_oz=row['Gold_Australian_Kangaroo_1_oz'],
                        Gold_Austrian_Philharmonic_1_oz=row['Gold_Austrian_Philharmonic_1_oz'],
                        Gold_Austrian_Philharmonic_1_4_oz=row['Gold_Austrian_Philharmonic_1_4_oz'],
                        Gold_Austrian_Philharmonic_1_10_oz=row['Gold_Austrian_Philharmonic_1_10_oz'],
                        Gold_Mexican_Fifty_Peso_1_2_oz=row['Gold_Mexican_Fifty_Peso_1_2_oz'],
                        Gold_Austrian_Corona_9802_oz=row['Gold_Austrian_Corona_9802_oz'],
                        Gold_Bullion_Bar_1oz=row['Gold_Bullion_Bar_1oz'],
                        Gold_Bullion_Bar_10oz=row['Gold_Bullion_Bar_10oz'],
                        Gold_Bullion_Bar_1_kg=row['Gold_Bullion_Bar_1_kg'],
                        Gold_Bullion_Bar_100_oz=row['Gold_Bullion_Bar_100_oz'],
                        Silver_Bullion_Bar_10_oz=row['Silver_Bullion_Bar_10_oz'],
                        Silver_Bullion_Bar_1_oz=row['Silver_Bullion_Bar_1_oz'],
                        Silver_Bullion_Bar_100_oz=row['Silver_Bullion_Bar_100_oz'],
                        Silver_Bulk_Generic_Bullion=row['Silver_Bulk_Generic_Bullion'],
                        Silver_American_Eagle_Coin_1_oz=row['Silver_American_Eagle_Coin_1_oz'],
                        Silver_Canadian_Maple_Leaf_1_oz=row['Silver_Canadian_Maple_Leaf_1_oz']
                        
                    )
                    
                    db.session.add(ratios_calc)


                db.session.commit()

            
            ratios_final.drop(columns=['id'], inplace=True)
            ratios_final = ratios_final.sort_values(by='Silver_American_Eagle_Coin_1_oz', ascending=False)
            ratios_final['TD'] = ratios_final['TD'].dt.strftime('%Y-%m-%d')
            ratios_final.rename(columns=item_name_swap, inplace=True)
            # print(ratios_final)
            # print(ratios_final.columns)

            #### dataframe is the finished dataframe ungrouped
            client_data = ratios_final[ratios_final['TRADE_BROKER'] == broker_number].to_dict('records')
            all_client_data = ratios_final.to_dict('records') 
            if request.method == 'POST':
                client_number = request.form['client_number']
                if client_number in ratios_final['CLIENT_NUM'].values:
                    
                    client_data = ratios_final.loc[(ratios_final['CLIENT_NUM'] == client_number) & 
                                                (ratios_final['TRADE_BROKER'] == broker_number)].to_dict('records')
                else:
                    flash('Client Number Not Found', category='error')
            
        
            session['last_prices_call_timestamp'] = datetime.now(tz)

            return render_template('trading_tools.html', user=current_user, all_client_data=all_client_data, client_data=client_data)
        else:
            flash('Broker number not found for the current user.', category='error')
            return redirect(url_for('views.home'))
    else:
        flash('Access Denied, Contact Admin', category='error')
        return redirect(url_for('views.home'))
    
  


@auth.route('/mcalvanymwm', methods=['GET','POST'])
@login_required
def mcalvany_mwm():
    if current_user.is_authenticated and current_user.is_mwm() or current_user.is_authenticated and current_user.is_admin():
        return render_template('MWM.html', user=current_user)
    else:
        flash('Access Denied, Contact Admin', category='error')
        return redirect(url_for('views.home'))

    

@auth.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.is_authenticated and current_user.email == 'koa@mcalvany.com':
        toggle_states = {
            'feature1_enabled': ToggleState.query.filter_by(feature_name='feature1').first().is_enabled,
            'feature2_enabled': ToggleState.query.filter_by(feature_name='feature2').first().is_enabled,
            'feature3_enabled': ToggleState.query.filter_by(feature_name='feature3').first().is_enabled
            }
        if request.method == 'POST':

            if 'feature' in request.json and 'enabled' in request.json:
                
                feature_name = request.json['feature']
                is_enabled = request.json['enabled']
                # Update or create the toggle state in the database
                toggle_state = ToggleState.query.filter_by(feature_name=feature_name).first()
                if toggle_state:
                    toggle_state.is_enabled = is_enabled
                else:
                    toggle_state = ToggleState(feature_name=feature_name, is_enabled=is_enabled)
                    db.session.add(toggle_state)
                db.session.commit()
            
            


            def fix_broker_num(broker_num):
                if pd.isna(broker_num):
                    return None  # Return None for NaN values
                elif broker_num.startswith('B'):
                    return 'B00' + broker_num[1:]  # Add two leading zeros
                else:
                    return broker_num
            
            if 'file1' in request.files:
                file1 = request.files['file1']
                data_type = request.form['data_type']

                if file1.filename == '':
                    flash("No file selected for trades", category='error')
                else:
                    # Read the CSV file using pandas
                    df = pd.read_csv(file1)
                    
                    expected_columns = ['TRADE_NUM', 'TD', 'TRADE_TYPE', 'CLIENT_NUM', 'TRADE_BROKER', 'TRADER', 'ITEM_CODE', 'QUANTITY', 'EXTENDED']
                    if not all(col in df.columns for col in expected_columns):
                        flash("Incorrect File Formatt ( Column Error )", category='error')

                    else:
                        df['TD'] = pd.to_datetime(df['TD'])
                        # Define a mapping between the data_type and the corresponding model fields
                        field_mapping = {
                            'type1': ['TRADE_NUM', 'TD', 'TRADE_TYPE', 'CLIENT_NUM', 'TRADE_BROKER', 'TRADER', 'ITEM_CODE', 'QUANTITY', 'EXTENDED'],
                            # Add more mappings for other data types if needed
                        }

                        if data_type in field_mapping:
                            # Iterate over each row of the dataframe and insert into the database
                            for _, row in df.iterrows():
                                model_fields = {field: row[field] for field in field_mapping[data_type]}
                                
                                trades_data = TradesTable(**model_fields)
                                db.session.add(trades_data)

                            db.session.commit()
                            flash("File uploaded and data inserted successfully", category='success')
                        else:
                            flash("Invalid data type", category='error')
                
                # Redirect to the admin page after processing
                return redirect(url_for('auth.admin'))            
            elif 'file2' in request.files:
                file2 = request.files['file2']
                data_type = request.form['data_type']

                if file2.filename == '':
                    flash("No file selected for leads", category='error')
                else:
                    # Read the CSV file using pandas
                    df = pd.read_csv(file2)
                    
                    # Define expected columns for file type 2
                    expected_columns = ['LeadNumbers', 'BrokerName', 'BrokerNum', 'LeadSource', 'Createdate']
                    
                    if not all(col in df.columns for col in expected_columns):
                        flash("Incorrect File Format (Column Error) for leads", category='error')
                    else:
                        # Convert 'Createdate' column to datetime objects
                        df['Createdate'] = pd.to_datetime(df['Createdate'])
                        df['BrokerNum'] = df['BrokerNum'].apply(fix_broker_num)
                        
                        # Define a mapping between the data_type and the corresponding model fields
                        field_mapping = {
                            'type2': ['LeadNumbers', 'BrokerName', 'BrokerNum', 'LeadSource', 'Createdate'],
                            # Add more mappings for other data types if needed
                        }

                        if data_type in field_mapping:
                            # Iterate over each row of the dataframe and insert into the database
                            for _, row in df.iterrows():
                                model_fields = {field: row[field] for field in field_mapping[data_type]}
                                
                                leads_data = LeadsTable(**model_fields)
                                db.session.add(leads_data)

                            db.session.commit()
                            flash("File uploaded and data inserted successfully for leads", category='success')
                        else:
                            flash("Invalid data type", category='error')
            elif 'file3' in request.files:
                file3 = request.files['file3']
                data_type = request.form['data_type']

                if file3.filename == '':
                    flash("No file selected for leads", category='error')
                else:
                    # Read the CSV file using pandas
                    df = pd.read_csv(file3)
                    
                    # Define expected columns for file type 2
                    expected_columns = ['LeadNumbers', 'BrokerName', 'BrokerNum', 'LeadSource', 'Createdate']
                    
                    if not all(col in df.columns for col in expected_columns):
                        flash("Incorrect File Format (Column Error) for leads", category='error')
                    else:
                        # Convert 'Createdate' column to datetime objects
                        df['Createdate'] = pd.to_datetime(df['Createdate'])
                        df['BrokerNum'] = df['BrokerNum'].apply(fix_broker_num)
                        
                        # Define a mapping between the data_type and the corresponding model fields
                        field_mapping = {
                            'type3': ['LeadNumbers', 'BrokerName', 'BrokerNum', 'LeadSource', 'Createdate'],
                            # Add more mappings for other data types if needed
                        }

                        if data_type in field_mapping:
                            # Iterate over each row of the dataframe and insert into the database
                            for _, row in df.iterrows():
                                model_fields = {field: row[field] for field in field_mapping[data_type]}
                                
                                client_data = ClientsTable(**model_fields)
                                db.session.add(client_data)

                            db.session.commit()
                            flash("File uploaded and data inserted successfully for clients", category='success')
                        else:
                            flash("Invalid data type", category='error')
            elif 'brokerNumber' in request.json and 'groupIdentifier' in request.json:
                # Handle broker update request
                selected_broker = request.json['brokerNumber']
                selected_group = request.json['groupIdentifier']
                # Update the current user's broker information in the database
                current_user.broker_number = selected_broker
                # Update the current user's group identifier based on the selected broker
                current_user.group_identifier = selected_group
                # Commit the changes to the database
                db.session.commit()
                flash(f"Broker updated to {selected_broker} successfully", category='success')
        


        return render_template('admin.html', user=current_user, toggle_states=toggle_states)
    
    else:
        flash('Access Denied, Contact Admin', category='error')
        return redirect(url_for('views.home'))



@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif email not in verified_emails:
            flash('Access Denied, Contact Admin', category='error')
        elif email.split('@')[0] in ['tory', 'eric', 'dkuchler', 'koa', 'aburress', 'btoliver', 'cheryl', 'christian', 'cstien', 'dvmcalvany', 
                                     'gstreets', 'auagpt', 'jdobesh', 'jblaylock', 'kevinorrick', 'michael', 'mhorsey', 'miles', 'mlewis',
                                       'pwortman', 'gold101', 'robert', 'shayla', 'steve', 'rdraper']:
            
            if email.split('@')[0] in ['tory', 'eric', 'dkuchler']:
                broker_number = 'B0098126'
                group_identifier = 'grp_1_tory'

            elif email.split('@')[0] == 'michael':
                broker_number = 'B0098147'
                group_identifier = 'grp_1_arries'


            elif email.split('@')[0] in ['koa', 'dcmcalvany']:
                broker_number = 'admin'
                group_identifier = 'grp_3_admin'


            elif email.split('@')[0] in ['aburress', 'gold101']:
                broker_number = 'B0098004'
                group_identifier = 'grp_1_mclaughlin'


            elif email.split('@')[0] in ['btoliver', 'kevinorrick']:
                broker_number = 'B0098014'
                group_identifier = 'grp_1_orrick'


            elif email.split('@')[0] in ['gstreets', 'cheryl']:
                broker_number = 'B0098170'
                group_identifier = 'grp_1_streets'


            elif email.split('@')[0] in ['christian', 'robert']:
                broker_number = 'B0098123'
                group_identifier = 'grp_1_goodin'


            elif email.split('@')[0] in ['cstien', 'auagpt']:
                broker_number = 'B0098065'
                group_identifier = 'grp_1_etz'


            elif email.split('@')[0] == 'jdobesh':
                broker_number = 'B0098059'
                group_identifier = 'grp_1_dobesh'


            elif email.split('@')[0] == 'mhorsey':
                broker_number = 'B0098106'
                group_identifier = 'grp_1_horsey'


            elif email.split('@')[0] == 'miles':
                broker_number = 'B0098109'
                group_identifier = 'grp_1_miles'


            elif email.split('@')[0] in ['mlewis', 'pwortman', 'rdraper']:
                broker_number = 'mcalvanywealth'
                group_identifier = 'grp_2_mwm'


            elif email.split('@')[0] == 'jblaylock':
                broker_number = 'B0098175'
                group_identifier = 'grp_1_josh'


            elif email.split('@')[0] == 'shayla':
                broker_number = 'B0098166'
                group_identifier = 'grp_1_shayla'

            elif email.split('@')[0] == 'steve':
                broker_number = 'B0098166'
                group_identifier = 'grp_1_steve'


            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256:600000'), broker_number=broker_number, group_identifier=group_identifier)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
        else:
            flash('Access Denied, Contact Admin', category='error')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

