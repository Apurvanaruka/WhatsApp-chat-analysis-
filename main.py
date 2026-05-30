import logging
import pandas as pd
import streamlit as st
from preprocessor import Preprocessing
from helper import *
import matplotlib.pyplot as plt
import seaborn as sns
from config import APP_TITLE, COLORS

plt.rcParams['font.family'] = 'Segoe UI Emoji'

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(page_title=APP_TITLE, layout='wide')
st.title(APP_TITLE)

@st.cache_data
def preprocess_chat(text_data):
    return Preprocessing(text_data)

def section(header, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        logger.error('%s failed: %s', header, e)
        st.warning(f'{header} could not be loaded.')

df = pd.DataFrame()

uploaded_file = st.sidebar.file_uploader('Choose a chat file (.txt)')
if uploaded_file is not None:
    text_data = uploaded_file.getvalue().decode('utf-8')
    with st.spinner('Processing chat...'):
        df = preprocess_chat(text_data)
    logger.info('Processed %d messages from %d users', df.shape[0], df['user'].nunique())

    user_list = ['Overall']
    user_list.extend(df['user'].unique())
    selected_user = st.sidebar.selectbox('Show analysis for', options=user_list)

    if st.sidebar.button('Show Analysis'):
        # ── Top Statistics ──
        def render_top_stats():
            col1, col2, col3, col4 = st.columns(4)
            msg_cnt, word_cnt, media_cnt, link_cnt = fetch_stats(selected_user, df)
            col1.metric('Messages', msg_cnt)
            col2.metric('Words', word_cnt)
            col3.metric('Media', media_cnt)
            col4.metric('Links', link_cnt)
        st.header('Top Statistics')
        section('Top Statistics', render_top_stats)

        # ── Media vs Text + Top Domains ──
        def render_media_domains():
            media_c, text_c = get_media_text_ratio(selected_user, df)
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                ax.pie([media_c, text_c], labels=['Media', 'Text'],
                       autopct='%0.1f%%', colors=[COLORS['media'], COLORS['text']],
                       startangle=90)
                ax.set_title('Media vs Text')
                st.pyplot(fig)
            with col2:
                top_domains = get_top_domains(selected_user, df)
                if top_domains:
                    st.subheader('Top Shared Domains')
                    st.dataframe(pd.DataFrame(top_domains, columns=['Domain', 'Count']),
                                 width='stretch')
        section('Media & Domains', render_media_domains)

        # ── Activities ──
        def render_activities():
            col1, col2 = st.columns(2)
            with col1:
                month_df = get_month_timeline(selected_user, df)
                if not month_df.empty:
                    fig, ax = plt.subplots()
                    ax.plot(month_df['month_year'], month_df['messages'],
                            marker='o', color=COLORS['primary'])
                    plt.xticks(rotation=45)
                    ax.set_title('Monthly Timeline')
                    st.pyplot(fig)
            with col2:
                week_df = get_weekly_timeline(selected_user, df)
                if not week_df.empty:
                    fig, ax = plt.subplots()
                    ax.bar(week_df['date'], week_df['count'], color=COLORS['primary'])
                    plt.xticks(rotation=45)
                    ax.set_title('Weekly Timeline')
                    st.pyplot(fig)

            daily = get_daily_timeline(selected_user, df)
            if not daily.empty:
                fig, ax = plt.subplots(figsize=(10, 4))
                sns.heatmap(daily, ax=ax, cmap='YlOrRd')
                ax.set_title('Daily Activity Heatmap')
                plt.xticks(rotation=45)
                st.pyplot(fig)

            col1, col2 = st.columns(2)
            with col1:
                hourly = get_hourly_activity(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(hourly.index, hourly.values, color=COLORS['hourly'])
                plt.xticks(rotation=45)
                ax.set_title('Hourly Activity')
                st.pyplot(fig)
            with col2:
                dow = get_day_of_week_distribution(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(dow.index, dow.values, color=COLORS['dow'])
                plt.xticks(rotation=45)
                ax.set_title('Day of Week')
                st.pyplot(fig)
        st.header('📊 Activities')
        section('Activities', render_activities)

        # ── Most Busiest User + Conversation Starters ──
        if selected_user == 'Overall':
            def render_busiest():
                col1, col2 = st.columns(2)
                with col1:
                    x = get_busiest_user(df)
                    fig, ax = plt.subplots()
                    ax.bar(x.index, x.values, color=COLORS['busy'])
                    plt.xticks(rotation=45)
                    ax.set_title('Top 5 Busiest Users')
                    st.pyplot(fig)
                with col2:
                    st.subheader('User Activity %')
                    st.dataframe(get_user_percent(df), width='stretch')

                starters = get_conversation_starter(df)
                if not starters.empty:
                    st.subheader('Conversation Starters')
                    fig, ax = plt.subplots()
                    ax.barh(starters.index, starters.values, color=COLORS['starter'])
                    ax.set_xlabel('Times started conversation')
                    st.pyplot(fig)
            st.header('👥 Users')
            section('Busiest Users', render_busiest)

        # ── Word Cloud ──
        def render_wordcloud():
            wc = get_world_could(selected_user, df)
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.imshow(wc)
            ax.axis('off')
            st.pyplot(fig)
        st.header('☁️ Word Cloud')
        section('Word Cloud', render_wordcloud)

        # ── Most Common Words ──
        def render_common_words():
            x, y = get_most_comman_word(selected_user, df)
            if x:
                fig, ax = plt.subplots()
                ax.barh(x, y, color=COLORS['secondary'])
                ax.set_xlabel('Frequency')
                st.pyplot(fig)
        st.header('📝 Most Common Words')
        section('Common Words', render_common_words)

        # ── Message Length ──
        def render_msg_length():
            lengths = get_message_length_stats(selected_user, df)
            if not lengths.empty:
                fig, ax = plt.subplots()
                ax.hist(lengths, bins=20, color=COLORS['hist'], edgecolor='black')
                ax.set_xlabel('Message length (characters)')
                ax.set_ylabel('Frequency')
                st.pyplot(fig)
        st.header('📏 Message Length Distribution')
        section('Message Length', render_msg_length)

        # ── Sentiment Analysis ──
        def render_sentiment():
            overall = get_overall_sentiment(selected_user, df)
            total = sum(overall.values())
            if total == 0:
                st.info('No messages to analyze for sentiment.')
                return

            col1, col2, col3 = st.columns(3)
            col1.metric('Positive', overall['positive'],
                        f'{overall["positive"]/total*100:.0f}%')
            col2.metric('Neutral', overall['neutral'],
                        f'{overall["neutral"]/total*100:.0f}%')
            col3.metric('Negative', overall['negative'],
                        f'{overall["negative"]/total*100:.0f}%')

            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                colors = [COLORS['positive'], COLORS['neutral'], COLORS['negative']]
                ax.pie([overall['positive'], overall['neutral'], overall['negative']],
                       labels=['Positive', 'Neutral', 'Negative'],
                       autopct='%0.1f%%', colors=colors, startangle=90)
                ax.set_title('Sentiment Distribution')
                st.pyplot(fig)

            with col2:
                sent_timeline = get_sentiment_timeline(selected_user, df)
                if not sent_timeline.empty:
                    fig, ax = plt.subplots()
                    ax.plot(sent_timeline['date'].astype(str),
                            sent_timeline['sentiment_score'],
                            marker='o', color=COLORS['primary'])
                    ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
                    plt.xticks(rotation=45)
                    ax.set_title('Sentiment Over Time')
                    ax.set_ylabel('Avg Sentiment Score')
                    st.pyplot(fig)

            if selected_user == 'Overall':
                user_sent = get_user_sentiment_summary(df)
                if not user_sent.empty:
                    st.subheader('Average Sentiment by User')
                    fig, ax = plt.subplots(figsize=(8, 4))
                    colors = [COLORS['positive'] if v > 0.05
                              else COLORS['negative'] if v < -0.05
                              else COLORS['neutral']
                              for v in user_sent.values]
                    ax.barh(user_sent.index, user_sent.values, color=colors)
                    ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
                    ax.set_xlabel('Avg Sentiment Score')
                    st.pyplot(fig)

            with st.expander('View Most Positive & Negative Messages'):
                pos, neg = get_extreme_messages(selected_user, df)
                if not pos.empty:
                    st.subheader('😊 Most Positive')
                    for _, row in pos.iterrows():
                        st.markdown(f'**{row["user"]}** — {row["messages"][:120]}... '
                                    f'`({row["sentiment_score"]:.2f})`')
                if not neg.empty:
                    st.subheader('😠 Most Negative')
                    for _, row in neg.iterrows():
                        st.markdown(f'**{row["user"]}** — {row["messages"][:120]}... '
                                    f'`({row["sentiment_score"]:.2f})`')
        st.header('❤️ Sentiment Analysis')
        section('Sentiment Analysis', render_sentiment)

        # ── Emoji Analysis ──
        def render_emojis():
            emojis_df = get_emojis(selected_user, df)
            if emojis_df.empty:
                st.info('No emojis found.')
                return
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                ax.pie(emojis_df['count'].head(), labels=emojis_df['emoji'].head(),
                       autopct='%0.1f%%')
                ax.set_title('Top Emojis')
                st.pyplot(fig)
            with col2:
                st.dataframe(emojis_df, width='stretch')
        st.header('😄 Emoji Analysis')
        section('Emoji Analysis', render_emojis)

        logger.info('Analysis complete for user: %s', selected_user)
