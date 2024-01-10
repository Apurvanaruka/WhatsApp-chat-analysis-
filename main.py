import pandas as pd
import streamlit as st
from preprocessor import Preprocessing
from helper import *
import matplotlib.pyplot as plt

st.sidebar.title('whatsapp chat analysis')
df = pd.DataFrame()

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    text_data = uploaded_file.getvalue().decode('utf-8')
    df = Preprocessing(text_data)
    st.dataframe(df)

    user_list = ['Overall']
    user_list.extend(df['user'].unique())
    selected_user = st.sidebar.selectbox(label='show Analysis wrt ',options=user_list)

    if st.sidebar.button("Show analysis"):
        # satats of the group
        st.title('Top statas')
        col1, col2, col3, col4 = st.columns(4)
        message_count, word_count, media_count,Links_count = fetch_stats(selected_user, df)
        with col1:
            st.header('Messages Count')
            st.title(message_count)

        with col2:
            st.header("words Count")
            st.title(word_count)
        with col3:
            st.header('Media Count')
            st.title(media_count)
        with col4:
            st.header('Links Count')
            st.title(Links_count)

        col1 , col2 = st.columns(2)
        
        with col1:
            month_timeline_df = get_month_timeline(selected_user,df)
            # st.dataframe(month_timeline_df)
            fig, ax = plt.subplots()
            ax.plot(month_timeline_df['month_year'],month_timeline_df['messages'])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            day_timeline = get_day_timeline(selected_user,df)
            fig, ax = plt.subplots()
            ax.plot(day_timeline['hour'],day_timeline['messages'])
            st.pyplot(fig)


        # Most Busiest person in the group
        if selected_user == 'Overall':
            st.title('Most Busiest User')
            col1, col2 = st.columns(2)

            with col1:
                x = get_busiest_user(df)
                fig , ax = plt.subplots()
                plt.title('Top 5 users')
                plt.xticks(rotation='vertical')
                ax.bar(x.index, x.values,color='red')
                st.pyplot(fig)
            with col2:
                x = get_user_percent(df)
                st.dataframe(x)

        # word cloud 
        wordcloud = get_world_could(selected_user,df)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud)
        plt.axis("off")
        st.pyplot(fig)

        # find most occurance word in the chat
        st.title('most comman words')
        x,y = get_most_comman_word(selected_user,df)    
        fig, ax = plt.subplots()
        ax.barh(x,y)
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        st.title('Emojis Analysis')
        col1,col2 = st.columns(2)
        emojis = get_emojis(selected_user,df)

        with col1:
            fig, ax = plt.subplots()
            ax.pie(emojis['count'].head(), labels=emojis['emoji'].head(),autopct='%0.2f')
            st.pyplot(fig)

        with col2:
            st.dataframe(emojis)

        
