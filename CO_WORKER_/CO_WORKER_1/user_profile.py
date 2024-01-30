import pyodbc
from werkzeug.security import generate_password_hash

# Veritabanı bağlantısını oluştur
def create_db_connection():
    server = 'NISA-OGUZ\\NISASQL'  # SQL Server instance adı ve bilgisayar adı
    database = 'CoWorkerDB2'  # Veritabanı adınız
    connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    return pyodbc.connect(connection_string)

# Kullanıcı profili sınıfını tanımla
class UserProfile:
    def __init__(self, user_id, username, email,idea, city, district, skills, interests, work_style):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.idea=idea
        self.city = city
        self.district = district
        self.skills = skills
        self.interests = interests
        self.work_style = work_style

    def save_to_db(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM UserProfiles WHERE user_id = ?", (self.user_id,))
        cursor.execute("INSERT INTO UserProfiles (user_id, username, email,idea, city, district, skills, interests, work_style) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (self.user_id, self.username, self.email,",".join(self.idea), self.city, self.district, ",".join(self.skills), ",".join(self.interests), self.work_style))
        db_conn.commit()


    @staticmethod
    
    def load_all_from_db(db_conn):
        cursor = db_conn.cursor()
        cursor.execute("SELECT user_id, username, email,idea, city, district, skills, interests, work_style FROM UserProfiles")
        users = []
        for row in cursor.fetchall():
            user_id, username, email,idea, city, district, skills, interests, work_style = row
            users.append(UserProfile(user_id, username, email,idea.split(','), city, district, skills.split(','), interests.split(','), work_style))
        return users



class MatchingAlgorithm:
    def __init__(self, users):
        self.users = users

    def calculate_similarity(self, user1, user2):
        idea_intersection=set(user1.idea.split(',')) & set(user2.idea.split(','))
        skills_intersection = set(user1.skills.split(',')) & set(user2.skills.split(','))
        interests_intersection = set(user1.interests.split(',')) & set(user2.interests.split(','))
        return len(skills_intersection) + len(interests_intersection) + len(idea_intersection)

    def find_best_matches(self, current_user):
        best_matches = []
        for user in self.users:
            if user.user_id != current_user.user_id:
                similarity_score = self.calculate_similarity(current_user, user)
                best_matches.append((user, similarity_score))
        best_matches.sort(key=lambda match: match[1], reverse=True)
        return best_matches

def create_table(db_conn):
    cursor = db_conn.cursor()
    # UserProfiles tablosunun varlığını kontrol et
    cursor.execute("SELECT * FROM sys.tables WHERE name = 'UserProfiles'")
    result = cursor.fetchone()

    # Eğer tablo yoksa, oluştur
    if not result:
        cursor.execute('''
        CREATE TABLE UserProfiles (
            user_id NVARCHAR(50) PRIMARY KEY,
            username NVARCHAR(50),
            email NVARCHAR(255),
            idea NVARCHAR(MAX),
            city NVARCHAR(50),
            district NVARCHAR(50),
            skills NVARCHAR(MAX),
            interests NVARCHAR(MAX),
            work_style NVARCHAR(50)
    )
    ''')
    db_conn.commit()
    cursor.close()


def main():
    db_conn = create_db_connection()
    users = UserProfile.load_all_from_db(db_conn)

# Eşleşme algoritmasını çalıştır
    matcher = MatchingAlgorithm(users)
    best_matches = matcher.find_best_matches(users[0])
    for match in best_matches:
        print(f"Match: {match[0].user_id} with score {match[1]}")

if __name__ == "__main__":
    main()



