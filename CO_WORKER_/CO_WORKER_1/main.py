from user_profile import UserProfile, create_db_connection, create_table
from matching_algorithm import MatchingAlgorithm
from sentiment_analysis import SentimentAnalyzer

def main():
    # Veritabanı bağlantısı oluştur
    db_conn = create_db_connection('NISA-OGUZ\\NISASQL', 'CoWorkerDB2', 'Trusted_Connection=yes;')
    create_table(db_conn)

   
    # Diğer kullanıcı profilleri de benzer şekilde yüklenebilir

    # Kullanıcıları veritabanından yükle
    users = UserProfile.load_all_from_db(db_conn)

    # Kullanıcı eşleştirme algoritmasını başlat
    matcher = MatchingAlgorithm(users)

    # Kullanıcılar için en iyi eşleşmeleri bul
    best_matches = matcher.find_best_matches(users)
    for match in best_matches:
        print(f"Match for {users.user_id}: {match[0].user_id} with score {match[1]}")

    # Duygu analizi örneği
    sentiment_analyzer = SentimentAnalyzer()
    text = "Bu projeyi gerçekten seviyorum."
    sentiment = sentiment_analyzer.analyze_sentiment(text)
    print(f"Sentiment Analysis of text: '{text}' - Polarity: {sentiment.polarity}, Subjectivity: {sentiment.subjectivity}")

if __name__ == "__main__":
    main()
    
