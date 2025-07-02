import requests
from . import db
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
from .keys import secert_key_intermedia, client_id_intermedia
pd.options.display.float_format = '{:,.2}'.format
pd.set_option('display.max_rows', 50)
from .models import User, InboundPerformanceData, OutboundPerformanceData




def get_access_token(client_id, client_secret, scope):
    url = 'https://login.intermedia.net/user/connect/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print('Failed to obtain access token:', response.status_code, response.text)
        return None


def get_detailed_calls(access_token, date_from, date_to, sort_column=None, descending=None, offset=None, size=None, account_id=None):
    url = 'https://api.intermedia.net/analytics/calls/call/detail'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'dateFrom': date_from,
        'dateTo': date_to,
        'sortColumn': sort_column,
        'descending': descending,
        'offset': offset,
        'size': size,
        'accountId': account_id
    }
    response = requests.post(url, headers=headers, params=params)
    return response

def intermedia_api():

    ####### ADJUST TO SCHEDULED AND NOT CURRENT TIME 
    most_recent_date_in = InboundPerformanceData.query.order_by(InboundPerformanceData.start_date.desc()).first()
    recent_date_in = most_recent_date_in.start_date
    # print(recent_date_in)
    most_recent_date_out = OutboundPerformanceData.query.order_by(OutboundPerformanceData.start_date.desc()).first()
    recent_date_out = most_recent_date_out.start_date
    # print(recent_date_out)
    
    if recent_date_in < recent_date_out:
        most_recent_date = recent_date_in
    else:
        most_recent_date = recent_date_out


    # Convert date_from string to datetime object
    current_datetime = datetime.utcnow()
    # print(current_datetime)
    if current_datetime > most_recent_date:

        client_id = client_id_intermedia
        client_secret = secert_key_intermedia
        scope = 'api.service.analytics.main'
        access_token = get_access_token(client_id, client_secret, scope)

        db_from = most_recent_date + timedelta(seconds=1)
        update_from_date = db_from.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        current_date_eod = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.999Z')
        date_from = update_from_date
        date_to = current_date_eod

        print(date_from)
        print(date_to)

        response = get_detailed_calls(access_token, date_from, date_to)

        if response.status_code == 200:
            
            call_data = response.json()
            # print(json.dumps(call_data, indent=2))

            directions = []
            durations = []
            from_numbers = []
            ring_durations = []
            start_dates = []
            to_numbers = []
            answereds = []
            user_id = []
            name = []
            name_out = []
            user_id_out = []

            for call_entry in call_data['calls']:
                direction = call_entry['direction']
                duration = call_entry['duration']
                from_number = call_entry['from']['number']
                ring_duration = call_entry['ringDuration']
                start_date = call_entry['start']
                to_number = call_entry['to']['number']
                answered = call_entry['answered']
                unique_user_id = call_entry['to'].get('userUniqueId', None)
                names = call_entry['to']['name']
                names_out = call_entry['from']['name']
                unique_user_id_out = call_entry['from'].get('userUniqueId', None)

                directions.append(direction)
                durations.append(duration)
                from_numbers.append(from_number)
                ring_durations.append(ring_duration)
                start_dates.append(start_date)
                to_numbers.append(to_number)
                answereds.append(answered)
                user_id.append(unique_user_id)
                name.append(names)
                name_out.append(names_out)
                user_id_out.append(unique_user_id_out)

            call_dataframe = pd.DataFrame({
            'Direction': directions,
            'Duration': durations,
            'From Number': from_numbers,
            'Ring Duration': ring_durations,
            'Start Date': start_dates,
            'To Number': to_numbers,
            'Answered': answereds,
            'User_id_in' : user_id,
            'Name_in' : name,
            'Name_out' : name_out,
            'User_id_out' : user_id_out
            })

            call_dataframe['Start Date'] = pd.to_datetime(call_dataframe['Start Date'])
            


        # out  & inbound dataframes
            outbound_df = call_dataframe[call_dataframe['Direction'] == 'outbound']
            inbound_df = call_dataframe[call_dataframe['Direction'] == 'inbound']
            
            # print(inbound_df)
            # print(outbound_df)

            if inbound_df.empty or outbound_df.empty:
                data_update_not_needed = 'XQ90-1'
                return data_update_not_needed


            else:
                # call drop list (outbound only)
                drop_list = ['970247','970317','970259','970335','970375','970382','970385','970403','970422','970426','970459','970508',
                    '970749','970759','970764','970769','970779','970799','970828','970844','2063314836','#','anonymous']

                
                # remove unwanted strings from numbers (inbound)
                inbound_df.loc[:, 'To Number'] = inbound_df['To Number'].str.replace(r'[+,*]', '', regex=True)
                inbound_df.loc[:, 'From Number'] = inbound_df['From Number'].str.replace(r'[+,*]', '', regex=True)
                if 'Name_out' in inbound_df.columns:
                    del inbound_df['Name_out']
                if 'User_id_out' in inbound_df.columns:
                    del inbound_df['User_id_out']
                inbound_df.reset_index(drop=True, inplace=True)

                # remove unwanted strings & phonenumbers (outbound)
                outbound_df.loc[:, 'To Number'] = outbound_df['To Number'].str.replace(r'[+,*]', '', regex=True)
                outbound_df.loc[:, 'From Number'] = outbound_df['From Number'].str.replace(r'[+,*]', '', regex=True)
                outbound_df = outbound_df[~outbound_df['To Number'].str.contains('|'.join(drop_list), na=False)]
                if 'Name_in' in outbound_df.columns:
                    del outbound_df['Name_in']
                if 'User_id_in' in outbound_df.columns:
                    del outbound_df['User_id_in']
                outbound_df.reset_index(drop=True, inplace=True)


                name_mapping_in = {
                    'grp_1_tory': ['Mzc2NDUtaHBieDAyMC50ZWxlY29tc3ZjLmNvbQ==:E', 'E3E10E5B-8F95-439F-8D39-8BD6D9301356', 'E87C1C16-29DB-48F7-B897-3DEB9F9C1BAF', 'C61324B4-BE49-487C-A55F-DD658CBE8246'],
                    'grp_1_arries': ['A814FA4F-1B63-4B70-A33A-519DBC72484A', 'Mzc2NjktaHBieDAyMC50ZWxlY29tc3ZjLmNvbQ==:E'],
                    'grp_1_dobesh': ['A2D88AD8-957E-4F1D-BB7D-49D2F1CF611D'],
                    'grp_1_etz': ['NDI1MjUtaHBieDAyMC50ZWxlY29tc3ZjLmNvbQ==:E', '7E4B7A73-E2C7-49E9-A331-05BCD9F20673'],
                    'grp_1_goodin': ['NDI1MzMtaHBieDAyMC50ZWxlY29tc3ZjLmNvbQ==:E', '246F149F-1DCE-49EF-9884-8454EDC67B27'],
                    'grp_1_miles': ['6AA15AF5-6803-4356-B6D5-BC42AEFF40FC', 'NTI4MTctaHBieDAyMC50ZWxlY29tc3ZjLmNvbQ==:E'],
                    'grp_1_horsey': ['NDE2ODMtaHBieDAyMC50ZWxlY29tc3ZjLmNvbQ==:E'],
                    'grp_1_mclaughlin': ['NDI1MzctaHBieDAyMC50ZWxlY29tc3ZjLmNvbQ==:E', 'E47EB547-3EA5-466B-B1BC-7546F9C18F5E', '1A10C4C7-0DBC-4B91-9753-8971A1F52705'],
                    'grp_1_orrick': ['35B57EA8-D5C3-4E87-A0F2-367534A14253', '5B8A5184-3079-4F61-87E3-9FA925AD6751', 'NDk4ODctaHBieDAyMC50ZWxlY29tc3ZjLmNvbQ==:E'],
                    'grp_1_streets': ['NjI2NzctaHBieDAyMC50ZWxlY29tc3ZjLmNvbQ==:E', '9A3F8379-0167-4380-A817-55C8271BFAE8'],
                    'grp_1_steve': ['E8254815-1E32-4F42-B637-01F7AC88343C'],
                    'grp_1_shayla': ['59176E19-98A5-4E37-9502-D16D9C18A490', 'Nzk0NDctaHBieDAyMC50ZWxlY29tc3ZjLmNvbQ==:E'],
                    'grp_1_josh': ['AB43FCB0-8720-4C33-9BFB-B02BD34BC90C']
                }

                name_mapping_out = {
                    'grp_1_tory': ['C61324B4-BE49-487C-A55F-DD658CBE8246', 'E3E10E5B-8F95-439F-8D39-8BD6D9301356', 'E87C1C16-29DB-48F7-B897-3DEB9F9C1BAF'],
                    'grp_1_arries': ['A814FA4F-1B63-4B70-A33A-519DBC72484A'],
                    'grp_1_dobesh': ['A2D88AD8-957E-4F1D-BB7D-49D2F1CF611D'],
                    'grp_1_etz': ['ACE9C823-ECB5-48D7-80D6-25BCAD3B5A57', '7E4B7A73-E2C7-49E9-A331-05BCD9F20673'],
                    'grp_1_goodin': ['77170DA3-9494-4F0A-8D2A-CCF38EC90011', '246F149F-1DCE-49EF-9884-8454EDC67B27'],
                    'grp_1_miles': ['6AA15AF5-6803-4356-B6D5-BC42AEFF40FC'],
                    'grp_1_horsey': ['913599D9-F3DB-49AA-959F-B7F5D29AFBBA'],
                    'grp_1_mclaughlin': ['1A10C4C7-0DBC-4B91-9753-8971A1F52705', 'E47EB547-3EA5-466B-B1BC-7546F9C18F5E'],
                    'grp_1_orrick': ['5B8A5184-3079-4F61-87E3-9FA925AD6751', '35B57EA8-D5C3-4E87-A0F2-367534A14253'],
                    'grp_1_streets': ['48C6CE13-DB71-4D20-9DB7-98A080051A1A'],
                    'grp_1_steve': ['E8254815-1E32-4F42-B637-01F7AC88343C'],
                    'grp_1_shayla': ['59176E19-98A5-4E37-9502-D16D9C18A490'],
                    'grp_1_josh': ['AB43FCB0-8720-4C33-9BFB-B02BD34BC90C']
                }


                def replace_with_name(number):
                    for name, numbers in name_mapping_in.items():
                        if number in numbers:
                            return name
                    return number

                def replace_with_name_out(number):
                    for name, numbers in name_mapping_out.items():
                        if number in numbers:
                            return name
                    return number



                inbound_df.loc[:, 'Name_in'] = inbound_df['User_id_in'].apply(replace_with_name)
                inbound_df
                outbound_df.loc[:, 'Name_out'] = outbound_df['User_id_out'].apply(replace_with_name_out)

                return inbound_df, outbound_df

        else:
            # failed response
            print('Failed to make API call:', response.status_code, response.text)
    else:
        # No need to make the API call as data is up to date
        data_update_not_needed = 'XQ90-1'
        return data_update_not_needed





