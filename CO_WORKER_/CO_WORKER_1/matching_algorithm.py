import pyodbc
from user_profile import UserProfile

# Veritabanı bağlantısını oluştur
def create_db_connection():
    server = 'NISA-OGUZ\\NISASQL'  # SQL Server instance adı ve bilgisayar adı
    database = 'CoWorkerDB2'  # Veritabanı adınız
    connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    return pyodbc.connect(connection_string)

# Kullanıcı profillerini veritabanından çekmek için bir fonksiyon
def get_user_profiles_from_database():
    user_profiles = []
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id,username,email ,idea,city ,district,skills ,interests, work_style FROM UserProfiles")
    
    for row in cursor.fetchall():
        user_id,username,email ,idea,city ,district, skills, interests, work_style = row
        user_profiles.append(UserProfile(user_id, username ,email ,idea.split(','), city.split(',') , district.split(','),skills.split(','), interests.split(','), work_style))
    
    conn.close()
    return user_profiles

class MatchingAlgorithm:
    def __init__(self, user_profiles):
        self.user_profiles = user_profiles

    def calculate_match_score(self, user1, user2):
        # Kullanıcılar arasındaki uyumu hesaplamak için bir skorlama sistemi
        score = 0
        score += len(set(user1.idea) & set(user2.idea)) * 2
        score += len(set(user1.skills) & set(user2.skills)) * 2  # Ortak yeteneklerin ağırlığı
        score += len(set(user1.interests) & set(user2.interests))  # Ortak ilgi alanlarının ağırlığı
        if user1.work_style == user2.work_style:
            score += 1  # Aynı çalışma tarzına sahip olmak
        return score
    
    def find_best_matches(self, user, top_n=10):
        # En iyi eşleşmeleri bulmak için
        scores = []
        for potential_match in self.user_profiles:
            if user.user_id != potential_match.user_id:  # Kendi kendisiyle eşleşme önlenir
                match_score = self.calculate_match_score(user, potential_match)
                scores.append((potential_match, match_score))

        # En yüksek skora sahip eşleşmeleri sırala ve döndür
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]

# Veritabanından kullanıcı profillerini alın
user_profiles = get_user_profiles_from_database()

# Kullanıcı profilleri listesinin boş olup olmadığını kontrol edin
if not user_profiles:
    print("Kullanıcı profilleri yüklenemedi veya boş.")
    exit()
# Kullanım Örneği
matcher = MatchingAlgorithm(user_profiles)
user_to_match = user_profiles[0]
best_matches_for_user1 = matcher.find_best_matches(user_to_match, top_n=2)


for match in best_matches_for_user1:
    print(f"Match: {match[0].user_id}, Score: {match[1]}")
