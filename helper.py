from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import emoji
import pandas as pd
import datetime
import re
from urllib.parse import urlparse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import SENTIMENT_THRESHOLD_POSITIVE, SENTIMENT_THRESHOLD_NEGATIVE

def convert_am_pm_to_24_hour(time_str):
    match = re.match(r'(\d+):(\d+)\s*([APap][Mm])', time_str)
    if not match:
        return time_str
    hours = int(match.group(1))
    minutes = int(match.group(2))
    period = match.group(3).lower()

    if period == 'pm' and hours != 12:
        hours += 12
    elif period == 'am' and hours == 12:
        hours = 0

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
    with open('stop_hinglish.txt','r') as f:
        stop_words = set(f.read().split())

    temp = []
    for words in df['messages'].str.split():
        for word in words:
            if word.lower() not in stop_words:
                temp.append(word)
    return ' '.join(temp)


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
    for message in df['messages']:
        for char in str(message):
            if emoji.is_emoji(char):
                emojis.append(char)
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


def get_daily_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]


    return df.pivot_table(index='day_name',columns='period',values='messages',aggfunc='count').fillna(0)


def get_weekly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['date'].dt.day_name().value_counts(sort=False).reset_index()

def get_hourly_activity(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['hour'].value_counts().sort_index()

def get_day_of_week_distribution(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    return df['day_name'].value_counts().reindex(day_order).fillna(0).astype(int)

def get_message_length_stats(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['messages'].str.len()

def get_media_text_ratio(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    media = (df['messages'] == '<Media omitted>').sum()
    total = df.shape[0]
    return media, total - media

def get_top_domains(selected_user,df):
    extractor = URLExtract()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    domains = []
    for message in df['messages']:
        for url in extractor.find_urls(message):
            domain = urlparse(url).netloc
            if domain:
                domains.append(domain)
    return Counter(domains).most_common(10)

def get_conversation_starter(df):
    return df.groupby('date').first()['user'].value_counts().head(10)

_sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    if not text or text == '<Media omitted>':
        return 'neutral', 0.0
    scores = _sia.polarity_scores(str(text))
    compound = scores['compound']
    if compound >= SENTIMENT_THRESHOLD_POSITIVE:
        label = 'positive'
    elif compound <= SENTIMENT_THRESHOLD_NEGATIVE:
        label = 'negative'
    else:
        label = 'neutral'
    return label, compound

def get_sentiment_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    labels, scores = zip(*df['messages'].apply(analyze_sentiment))
    return list(labels), list(scores)

def get_overall_sentiment(selected_user, df):
    labels, _ = get_sentiment_stats(selected_user, df)
    counts = Counter(labels)
    return {
        'positive': counts.get('positive', 0),
        'neutral': counts.get('neutral', 0),
        'negative': counts.get('negative', 0),
    }

def get_sentiment_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    labels, scores = zip(*df['messages'].apply(analyze_sentiment))
    temp = df.copy()
    temp['sentiment_score'] = scores
    return temp.groupby('date')['sentiment_score'].mean().reset_index()

def get_user_sentiment_summary(df):
    labels, scores = zip(*df['messages'].apply(analyze_sentiment))
    temp = df.copy()
    temp['sentiment_score'] = scores
    return temp.groupby('user')['sentiment_score'].mean().sort_values(ascending=False).head(15)

def get_extreme_messages(selected_user, df, n=5):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    labels, scores = zip(*df['messages'].apply(analyze_sentiment))
    temp = df.copy()
    temp['sentiment_score'] = scores
    positive = temp.nlargest(n, 'sentiment_score')[['user', 'messages', 'sentiment_score']]
    negative = temp.nsmallest(n, 'sentiment_score')[['user', 'messages', 'sentiment_score']]
    return positive, negative

