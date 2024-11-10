import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Directly set your API keys here
NEWS_API_KEY = "w2p7cXIWXqRa2pfUdul7mWU9KIPcXS5Q7Z6pUr26pBq_yqpT"  # Replace with your actual News API key
GEMINI_API_KEY = "AIzaSyCE52Pl_IaeNWeirttmYnbc9vzsSJ7nR7U"  # Replace with your actual Gemini API key
genai.configure(api_key=GEMINI_API_KEY)

NEWS_API_ENDPOINT = 'https://api.currentsapi.services/v1/latest-news'

def fetch_news(country):
    headers = {
        'Authorization': NEWS_API_KEY
    }
    params = {
        'country': country
    }
    response = requests.get(NEWS_API_ENDPOINT, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        custom_error_message(f"Error fetching news: {response.status_code}")
        return None

def fetch_article_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        article_content = ' '.join([para.get_text() for para in paragraphs])
        return article_content
    else:
        custom_error_message(f"Error while fetching article content from {url}")
        return None

def summarize_article(content):
    prompt = f"Summarize the following article: {content}, if harmful content found then just return 'Contains harmful content'"
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        response = model.generate_content(prompt)
        if hasattr(response, 'text') and response.text:
            return response.text
        else:
            return "Summary not available"
    except Exception:
        return "Error generating summary"

def analyze_sentiment(content):
    prompt = f"Analyze the sentiment of the following article and classify it as Positive, Negative, or Neutral: {content}"
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        response = model.generate_content(prompt)
        if hasattr(response, 'text') and response.text:
            sentiment = response.text.strip().lower()
            return 'Positive' if 'positive' in sentiment else 'Negative' if 'negative' in sentiment else 'Neutral'
        else:
            return 'Error in analyzing sentiment.'
    except Exception:
        return 'Error in analyzing sentiment.'

def detect_bias(content):
    prompt = f"Detect and describe any biases in this article. Consider selection, framing, omission, and source biases: {content}"
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        response = model.generate_content(prompt)
        if hasattr(response, 'text') and response.text:
            return response.text
        else:
            return "Bias detection could not be completed."
    except Exception:
        return "Error in detecting bias."

# Custom error message styling
st.markdown(
    """
    <style>
        .custom-error {
            color: #ffffff;
            font-size: 1em;
            padding: 15px;
            background: rgba(0, 0, 0, 0.7);
            border-radius: 10px;
            margin: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1504711434969-e33886168f5c?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8bmV3c3xlbnwwfHwwfHx8MA%3D%3D");
            background-attachment: fixed;
            background-size: cover;
            font-family: Arial, sans-serif;
            color: #f4f4f4;
        }
        .title {
            color: black;
            text-align: center;
            font-weight: bold;
            font-size: 3em;
        }
        .news-container {
            padding: 15px;
            background: rgba(0, 0, 0, 0.7);
            border-radius: 10px;
            margin: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        .news-title {
            color: #ffffff;
            font-weight: bold;
            font-size: 1.5em;
            margin-bottom: 5px;
        }
        .news-url {
            color: #89CFF0;
            font-size: 1em;
            font-style: italic;
            text-decoration: none;
        }
        .news-url:hover {
            color: #f4f4f4;
            text-decoration: underline;
        }
        .summary, .sentiment, .bias {
            color: #ffffff;
            font-size: 1em;
            padding: 15px;
            background: rgba(0, 0, 0, 0.7);
            border-radius: 10px;
            margin: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        
    </style>
    """,
    unsafe_allow_html=True
)

# Display custom error message
def custom_error_message(message):
    st.markdown(f'<div class="custom-error">{message}</div>', unsafe_allow_html=True)

st.markdown('<h1 class="title">📰 News Aggregator</h1>', unsafe_allow_html=True)

st.sidebar.header("Filter Options")
countries = ['US', 'GB', 'IN', 'CA', 'AU', 'FR', 'DE', 'JP', 'CN', 'RU', 'BR', 'MX', 'IT', 'ES', 'KR']
selected_country = st.sidebar.selectbox('Select a country', countries)

# Fetch news based on selected country
news = fetch_news(selected_country)

if news and 'news' in news:
    for article in news['news']:
        st.markdown(f"""
            <div class="news-container">
                <div class="news-title">{article['title']}</div>
                <a href="{article['url']}" class="news-url" target="_blank">Read more</a>
            </div>
        """, unsafe_allow_html=True)

        # Fetch and summarize the article content
        summary = summarize_article(article['url'])
        if summary:
            st.markdown(f'<div class="summary">Summary:<br>{summary}</div>', unsafe_allow_html=True)
            
            # Analyze sentiment of the article
            sentiment = analyze_sentiment(summary)
            st.markdown(f'<div class="sentiment">Sentiment: {sentiment}</div>', unsafe_allow_html=True)
            
            # Detect bias in the article
            bias = detect_bias(summary)
            st.markdown(f'<div class="bias">Bias Analysis:<br>{bias}</div>', unsafe_allow_html=True)
else:
    custom_error_message("No news articles found or an error occurred.")
