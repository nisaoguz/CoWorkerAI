import nltk
import textblob
from textblob import TextBlob

# nltk bileşenlerini indir
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

class SentimentAnalyzer:
    @staticmethod
    def analyze_sentiment(text):
        analysis = TextBlob(text)
        return analysis.sentiment

    @staticmethod
    def classify_sentiment(sentiment):
        polarity = sentiment.polarity
        if polarity > 0:
            return "Pozitif"
        elif polarity < 0:
            return "Negatif"
        else:
            return "Nötr"

# Kullanım örneği
analyzer = SentimentAnalyzer()
text = "Bu projede çalışmak çok heyecan verici ama bazen zorlayıcı olabiliyor."
sentiment = analyzer.analyze_sentiment(text)
sentiment_classification = analyzer.classify_sentiment(sentiment)

print(f"Metin: {text}")
print(f"Duygu Durumu: {sentiment_classification} (Polarity: {sentiment.polarity}, Subjectivity: {sentiment.subjectivity})")