import pandas as pd
import re
from helper import  convert_am_pm_to_24_hour


def Preprocessing(text_data):
    pattern = "(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}\s?[APMapm]+) - (\S+ \S+): (.+)"
    text_list = re.findall(pattern,text_data)
    df = pd.DataFrame(text_list, columns=['date','time','user','messages'])
    df['date'] = pd.to_datetime(df['date'],format="%m/%d/%y")
    df['time'] = [convert_am_pm_to_24_hour(time_str) for time_str in df['time']]
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['hour'] = [time_str.split(":")[0] for time_str in df['time']]
    df['minutes'] = [time_str.split(":")[1] for time_str in df['time']]
    df = df.drop('date',axis=1)
    df = df.drop('time',axis=1)
    return df

