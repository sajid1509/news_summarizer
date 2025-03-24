import streamlit as st
import requests
import os

st.set_page_config(page_title="News Sentiment Analyzer", layout="wide")

st.title(" News Summarizer & Sentiment Analyzer")

# Input Company Name
company = st.text_input("Enter Company Name")

if st.button("Fetch News & Analyze Sentiment"):
    st.subheader(f"News Articles for {company}")
    
    try:
        news_response = requests.get(f"http://127.0.0.1:5000/get_news?company={company}")
        news_response.raise_for_status()
        articles_data = news_response.json().get("articles", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch news: {e}")
        articles_data = []

    if articles_data:
        # Display Articles
        for article in articles_data:
            st.markdown(f"### [{article['title']}]({article['url']})")
            st.write(f"published: {article['published_date']}")
            st.write(f"Summary: {article['summary'][:300]}...")
            st.divider()

        # Send for Sentiment Analysis
        try:
            analyze_response = requests.post(
                "http://127.0.0.1:5000/analyze",
                json={"company": company, "articles": articles_data}
            )
            analyze_response.raise_for_status()
            sentiment_data = analyze_response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to analyze sentiment: {e}")
            sentiment_data = {}

        if sentiment_data:
            # Display Sentiment Summary
            st.subheader("Sentiment Analysis")
            st.json(sentiment_data["Comparative Sentiment Score"])

            # Display Final Summary
            st.subheader("Final Sentiment Summary")
            st.write(sentiment_data["Final Sentiment Analysis"])

            # Play Hindi Speech
            st.subheader("Listen to Sentiment Summary in Hindi")
            audio_file_path = sentiment_data.get("Audio")
            if audio_file_path and os.path.exists(audio_file_path):
                st.audio(audio_file_path)
            else:
                st.warning("Audio file not found.")
    else:
        st.error("No news articles found. Try another company.")
