from urlextract import URLExtract
from wordcloud import WordCloud

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

def get_world_could(selected_user, df):
    stop_words = ''
    with open('/home/vostro/Desktop/whatsapp_chat_analysis/stop_hinglish.txt','r') as f:
        stop_words = f.read()

    temp = ""
    for words in df['messages'].str.split():
        for word in words:
            if word.lower() not in stop_words:
                temp += word+" "
    print(temp)
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return WordCloud(width=1200, height=600,
                          background_color='white',
                            stopwords=stop_words,
                          min_font_size=10).generate(temp)

