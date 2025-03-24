from flask import Flask, request, jsonify
from utils import scrape_news  # Import the scraping function
from transformers import pipeline
from gtts import gTTS
from googletrans import Translator

app = Flask(__name__)

# Load sentiment analysis model
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(text):
    result = sentiment_pipeline(text)[0]["label"]
    if result == "POSITIVE":
        return "Positive"
    elif result == "NEGATIVE":
        return "Negative"
    else:
        return "Neutral"

import yake
def extract_topics(summary):
    kw_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=5)
    keywords = kw_extractor.extract_keywords(summary)
    return [keyword[0] for keyword in keywords]

def compare_articles(articles, company):
    sentiments = []
    topic_lists = []
    structured_articles = []
    for article in articles:
        sentiment = analyze_sentiment(article["summary"])
        topics = extract_topics(article["summary"])
        
        structured_articles.append({
            "Title": article["title"],
            "Summary": article["summary"],
            "Sentiment": sentiment,
            "Topics": topics
        })
        sentiments.append(sentiment)
        topic_lists.append(topics)
    # Count sentiment occurrences
    sentiment_counts = {
        "Positive": sentiments.count("Positive"),
        "Negative": sentiments.count("Negative"),
        "Neutral": sentiments.count("Neutral"),
    }
    # Generate coverage comparison
    coverage_differences = []
    if len(structured_articles) > 1:
        for i in range(len(structured_articles) - 1):
            comparison_text = (
                f"Article {i+1} focuses on {structured_articles[i]['Topics']}, "
                f"while Article {i+2} discusses {structured_articles[i+1]['Topics']}."
            )
            impact_text = (
                "The first article highlights positive aspects, whereas the second "
                "raises concerns about risks or regulatory issues."
            )
            coverage_differences.append({"Comparison": comparison_text, "Impact": impact_text})
    # Compute topic overlap
    common_topics = list(set(topic_lists[0]).intersection(*topic_lists)) if topic_lists else []
    unique_topics = [
        {"Unique Topics in Article {}".format(i+1): list(set(topics) - set(common_topics))}
        for i, topics in enumerate(topic_lists)
    ]
    # Generate final sentiment summary
    if sentiment_counts["Positive"] > sentiment_counts["Negative"]:
        overall_sentiment = "mostly positive. Potential stock growth expected."
    elif sentiment_counts["Negative"] > sentiment_counts["Positive"]:
        overall_sentiment = "mostly negative. Investors should be cautious."
    else:
        overall_sentiment = "neutral. No significant market impact is expected."

    final_summary = f"{company}'s latest news coverage is {overall_sentiment}"
    return structured_articles, sentiment_counts, coverage_differences, common_topics, unique_topics, final_summary
def text_to_speech_hindi(text):
    """Converts English input text into Hindi speech."""
    translator = Translator()
    translated_text = translator.translate(text, dest="hi").text
    tts = gTTS(text=translated_text, lang="hi", slow=False)
    filename = "translated_speech.mp3"
    tts.save(filename)
    return filename
@app.route("/get_news", methods=["GET"])
def get_news():
    """API endpoint to scrape news articles."""
    company = request.args.get("company")
    articles_data = scrape_news(company)
    return jsonify({"articles": articles_data})
@app.route("/analyze", methods=["POST"])
@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyzes sentiment and generates a comparative summary."""
    data = request.json
    company = data["company"]  # Extract company name separately
    articles = data["articles"]
    structured_articles, sentiment_counts, coverage_differences, common_topics, unique_topics, final_summary = compare_articles(articles, company)
    # Convert final summary to Hindi speech
    audio_file = text_to_speech_hindi(final_summary)
    return jsonify({
        "Company": company,
        "Articles": structured_articles,
        "Comparative Sentiment Score": {
            "Sentiment Distribution": sentiment_counts,
            "Coverage Differences": coverage_differences,
            "Topic Overlap": {
                "Common Topics": common_topics,
                **{key: value for d in unique_topics for key, value in d.items()}
            }
        },
        "Final Sentiment Analysis": final_summary,
        "Audio": audio_file
    })
   

if __name__ == "__main__":
    app.run(debug=False)
