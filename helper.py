from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import emoji
import pandas as pd
import datetime

def convert_am_pm_to_24_hour(time_str):
    # Split the time string into hours, minutes, AM/PM
    time_parts = time_str.split(':')
    hours = int(time_parts[0])
    minutes = int(time_parts[1][:2])  # Extract only the first two characters for minutes
    period = time_parts[1][2:].strip()

    # Convert to 24-hour format
    if period.lower() == 'pm' and hours != 12:
        hours += 12
    elif period.lower() == 'am' and hours == 12:
        hours = 0

    # Format the result
    return f"{hours:02d}:{minutes:02d}"


def fetch_stats(selected_user, df):
    extractor = URLExtract()
    if selected_user != 'Overall':
         df = df[df['user'] == selected_user]
    word = []
    media_count = 0
    Links = []

    for message in df['messages']:
        word.extend(message.split())
        if message == "<Media omitted>":
            media_count += 1
        Links.extend(extractor.find_urls(message))
    return df.shape[0],len(word),media_count,len(Links)


def get_busiest_user(df):
    return df['user'].value_counts().head()

def get_user_percent(df):
    return round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'count':'percent'})

def remove_stopwords(df):
    stop_words = ''
    with open('/home/vostro/Desktop/whatsapp_chat_analysis/stop_hinglish.txt','r') as f:
        stop_words = f.read()

    temp = ""
    for words in df['messages'].str.split():
        for word in words:
            if word.lower() not in stop_words:
                temp += word+" "
    return temp


def get_world_could(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return WordCloud(width=1200, height=600,
                          background_color='white',
                          min_font_size=10).generate(remove_stopwords(df))

def get_most_comman_word(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    text = remove_stopwords(df).split()
    word =  Counter(text).most_common(20)
    x = []
    y = []
    for i in word:
        x.append(i[0])
        y.append(i[1])
    return x,y

def get_emojis(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for word in df['messages'].str.split(''):   
        for i in word:
            if emoji.is_emoji(i):
                emojis.extend(i)
    return pd.DataFrame(Counter(emojis).most_common(),columns=['emoji','count'])


def get_month_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    month_timeline_df = df.groupby(['year','month']).count()['messages'].reset_index()
    month_timeline_df
    month_year = []
    for i in range(month_timeline_df.shape[0]):
        month_datetime = datetime.date(month_timeline_df['year'][i], month_timeline_df['month'][i],1)
        month_name = month_datetime.strftime("%B")
        month_year.append(month_name +"-"+str(month_timeline_df['year'][i]))

    month_timeline_df['month_year'] = month_year
    return month_timeline_df.drop(['year','month'],axis=1)


def get_day_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df.groupby(['hour']).count()['messages'].reset_index()
