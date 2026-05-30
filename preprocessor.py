import pandas as pd
import re
from helper import  convert_am_pm_to_24_hour
import streamlit as st

def Preprocessing(text_data):
    lines = text_data.split('\n')
    joined_lines = []
    for line in lines:
        if re.match(r'\d+/\d+/\d+,', line):
            joined_lines.append(line)
        else:
            if joined_lines:
                joined_lines[-1] += ' ' + line.strip()
            else:
                joined_lines.append(line)
    text_data = '\n'.join(joined_lines)

    pattern = r'(\d+/\d+/\d+),\s*(\d+:\d+\s*[APap][Mm])\s*-\s*([^:\n]+):\s*(.+)'
    text_list = re.findall(pattern, text_data)
    df = pd.DataFrame(text_list, columns=['date','time','user','messages'])
    df['date'] = pd.to_datetime(df['date'],format="%d/%m/%y")
    df['time'] = [convert_am_pm_to_24_hour(time_str) for time_str in df['time']]
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['hour'] = [time_str.split(":")[0] for time_str in df['time']]
    df['minutes'] = [time_str.split(":")[1] for time_str in df['time']]
    df = df.drop('time',axis=1)
    period = []
    for hour in df['hour']:
        h = int(hour)
        next_h = (h + 1) % 24
        period.append(f"{h:02d}-{next_h:02d}")
    df['period'] = period
    df['day_name'] = df['date'].dt.day_name()
    return df


