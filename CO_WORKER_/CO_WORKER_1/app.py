from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc
from user_profile import UserProfile
from matching_algorithm import MatchingAlgorithm
from matching_algorithm import user_profiles
from flask import Flask, request, jsonify
import openai
import os
from datetime import datetime


openai.api_key = "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"




app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'


# Türkiye'nin 81 ili
turkey_cities = [
    'Adana', 'Adıyaman', 'Afyonkarahisar', 'Ağrı', 'Amasya', 'Ankara', 'Antalya',
    'Artvin', 'Aydın', 'Balıkesir', 'Bilecik', 'Bingöl', 'Bitlis', 'Bolu',
    'Burdur', 'Bursa', 'Çanakkale', 'Çankırı', 'Çorum', 'Denizli', 'Diyarbakır',
    'Edirne', 'Elazığ', 'Erzincan', 'Erzurum', 'Eskişehir', 'Gaziantep', 'Giresun',
    'Gümüşhane', 'Hakkâri', 'Hatay', 'Isparta', 'İçel (Mersin)', 'İstanbul',
    'İzmir', 'Kars', 'Kastamonu', 'Kayseri', 'Kırklareli', 'Kırşehir', 'Kocaeli',
    'Konya', 'Kütahya', 'Malatya', 'Manisa', 'Kahramanmaraş', 'Mardin', 'Muğla',
    'Muş', 'Nevşehir', 'Niğde', 'Ordu', 'Rize', 'Sakarya', 'Samsun', 'Siirt', 'Sinop',
    'Sivas', 'Tekirdağ', 'Tokat', 'Trabzon', 'Tunceli', 'Şanlıurfa', 'Uşak', 'Van',
    'Yozgat', 'Zonguldak', 'Aksaray', 'Bayburt', 'Karaman', 'Kırıkkale', 'Batman',
    'Şırnak', 'Bartın', 'Ardahan', 'Iğdır', 'Yalova', 'Karabük', 'Kilis', 'Osmaniye', 'Düzce'
]


# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Veritabanı bağlantısını oluştur
# Veritabanı bağlantısını oluştur
def create_db_connection():
    server = 'NISA-OGUZ\\NISASQL'  # SQL Server instance adı ve bilgisayar adı
    database = 'CoWorkerDB2'  # Veritabanı adınız
    connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    connection = pyodbc.connect(connection_string)
    return connection


# Kullanıcı modeli (normalde veritabanından alınır)
# Kullanıcı modeli
class User(UserMixin):
    def __init__(self, id, username, password,email,idea,city,district, skills="", interests="", work_style=""):
        self.id = id
        self.username = username
        self.password = password
        self.email=email
        self.idea=idea
        self.city=city
        self.district=district
        self.skills = skills
        self.interests = interests
        self.work_style = work_style

# Bu örnek için basit kullanıcı listesi
users = {'user1': User('1', 'user1', 'password1','sdsddf@gmail.com','23.09.2002','fikir','ist' , 'üsküdar' 'coding,design', 'tech,art', 'remote')}

# Kullanıcı yükleyici
@login_manager.user_loader
def load_user(user_id):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password,email,idea,city,district,skills, interests, work_style FROM users WHERE id = ?", (user_id,))
    user_record = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_record:
        return User(*user_record)
    return None


# Kullanıcı Giriş Formu Sınıfı
class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    submit = SubmitField('Giriş Yap')

# Profil Düzenleme Formu Sınıfı
class ProfileForm(FlaskForm):
    email= StringField('E-Mail', validators=[DataRequired()])
    #birth = DateField('Doğum Tarihi (YYYY-MM-DD)', validators=[DataRequired()])
    idea=StringField('Fikir', validators=[DataRequired()])
    city=StringField('İl', validators=[DataRequired()])
    district=StringField('İlçe', validators=[DataRequired()])
    skills = StringField('Yetenekler', validators=[DataRequired()])
    interests = StringField('İlgi Alanları', validators=[DataRequired()])
    work_style = StringField('Çalışma Tarzı', validators=[DataRequired()])
    submit = SubmitField('Güncelle')

# Kayıt Ol Formu
class RegistrationForm(FlaskForm):
    username = StringField('Kullanıcı Adı')
    password = PasswordField('Şifre', validators=[DataRequired()])
    email=StringField('E-Mail', validators=[DataRequired()])
    #birth = DateField('Doğum Tarihi (YYYY-MM-DD)', format='%Y-%m-%d')
    idea=StringField('Fikir')
    city=StringField('İl')
    district=StringField('İlçe')
    skills = StringField('Yetenekler')
    interests = StringField('İlgi Alanları')
    work_style = StringField('Çalışma Tarzı')
    submit = SubmitField('Kayıt Ol')


# Veritabanına kullanıcı eklemek için fonksiyon
# Veritabanına kullanıcı eklemek için güncellenmiş fonksiyon
def insert_user_to_db(username, password, email, idea, city, district, skills, interests, work_style):
    conn = create_db_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)

    try:
        # users tablosuna kullanıcıyı ekleyin
        cursor.execute("""
            INSERT INTO users (username, password, email, idea, city, district, skills, interests, work_style)
            VALUES (?, ?, ?,  ?, ?, ?, ?, ?, ?);
        """, (username, hashed_password, email, idea, city, district, skills, interests, work_style))

        # Son eklenen kullanıcının ID'sini alın
        cursor.execute("SELECT SCOPE_IDENTITY();")
        user_id = cursor.fetchone()[0]

        # UserProfiles tablosuna kullanıcıyı ekleyin
        cursor.execute("""
            INSERT INTO UserProfiles ( username, email,  idea, city, district, skills, interests, work_style)
            VALUES ( ?, ?,  ?, ?, ?, ?, ?, ?);
        """, (username, email,  idea, city, district, skills, interests, work_style))

        conn.commit()
    except pyodbc.DatabaseError as e:
        # Hata durumunda kullanıcıya bilgi vermek ve commit işlemini geri almak için
        flash('Veritabanı hatası: ' + str(e))
        conn.rollback()
    finally:
        # İşlem tamamlandıktan sonra imleci ve bağlantıyı kapat
        cursor.close()
        conn.close()


# Kullanıcı kayıt sayfası
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        conn = create_db_connection()
        cursor = conn.cursor()

        # Kullanıcı adının zaten var olup olmadığını kontrol et
        cursor.execute("SELECT id FROM users WHERE email = ?", (form.email.data,))
        if cursor.fetchone():
            flash('Bu E-Mail  zaten kullanımda. Lütfen başka bir E-Mail deneyin.')
            return render_template('register.html', form=form)

        # Kullanıcıyı veritabanına ekle
        # Kullanıcıyı her iki tabloya da ekleyin
        insert_user_to_db(form.username.data, form.password.data, form.email.data ,form.idea.data, form.city.data,form.district.data, form.skills.data, form.interests.data, form.work_style.data)
        flash('Başarıyla kayıt oldunuz!')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

# Giriş Yap sayfası
@app.route('/login', methods=['GET', 'POST'])

def login():

    form = LoginForm()
    if form.validate_on_submit():
        # Veritabanı bağlantısı ve kullanıcı doğrulaması
        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password,email,idea,city,skills,district, interests, work_style FROM users WHERE email = ?", (form.email.data,))
        user_record = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_record and check_password_hash(user_record[2], form.password.data):
            user = User(*user_record)
            login_user(user)

            return redirect(url_for('login'))

        else:
            flash('Geçersiz email veya şifre.')
            return redirect(url_for('home'))  # Giriş başarısız olduğunda "home.html" sayfasında kal

    return render_template('login.html', form=form)


# Profil Düzenleme sayfası
@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)
    if request.method == 'POST' and form.validate():
        conn = create_db_connection()
        cursor = conn.cursor()
        #birth = datetime.strptime(form.birth.data, '%Y-%m-%d').date()
        # Formdan gelen bilgilerle mevcut kullanıcı bilgilerini güncelle
        # Users tablosunu güncelle
        cursor.execute("UPDATE users SET email=?,idea=?,city=?,district=?, skills = ?, interests = ?, work_style = ? WHERE id = ?", 
               (form.email.data, form.idea.data, form.city.data, form.district.data, form.skills.data, form.interests.data, form.work_style.data, current_user.id))

        # UserProfiles tablosunu güncelle
        cursor.execute("UPDATE UserProfiles SET email=?,idea=?,city=?,district=?, skills = ?, interests = ?, work_style = ? WHERE user_id = ?", 
               (form.email.data, form.idea.data, form.city.data, form.district.data, form.skills.data, form.interests.data, form.work_style.data, current_user.id))
        conn.commit()
        cursor.close()
        conn.close()


        flash('Profiliniz başarıyla güncellendi.')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', form=form)


# Profil sayfası
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


# Eşleştirme fonksiyonu
def find_matches(current_user, all_users):
    matches = []
    for user in all_users:
        if user.id == current_user.id:
            continue
        idea_score=len(set(current_user.idea.split(',')) & set(user.idea.split(',')))
        skills_score = len(set(current_user.skills.split(',')) & set(user.skills.split(',')))
        interests_score = len(set(current_user.interests.split(',')) & set(user.interests.split(',')))
        total_score = skills_score + interests_score + idea_score
        if total_score > 0:
            matches.append((user, total_score))

    matches.sort(key=lambda x: x[1], reverse=True)
    return matches



# Eşleşme sayfası
@app.route('/matches')
@login_required
def show_matches():
    # Kullanıcı profillerini veritabanından yükleyin
    user_profiles = UserProfile.load_all_from_db(create_db_connection())

    # Giriş yapmış kullanıcının profili
    current_user_profile = next((profile for profile in user_profiles if profile.user_id == current_user.id), None)

    # Eşleşme algoritmasını çalıştırın ve eşleşmeleri alın
    if current_user_profile:
        matcher = MatchingAlgorithm(user_profiles)
        best_matches = matcher.find_best_matches(current_user_profile)
    else:
        best_matches = []

    # Eşleşmeleri şablona gönderin
    return render_template('matches.html', matches=best_matches)




# Çıkış yap
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/', methods=['GET', 'POST'])
def home():
    login_form = LoginForm()
    register_form = RegistrationForm()
    login_manager.login_view = 'home'

    # Giriş yapma işlemi
    if login_form.validate_on_submit() and 'login' in request.form:
        user = users.get(login_form.email.data)
        if user and user.password == login_form.password.data:
            login_user(user)
            return redirect(url_for('show_matches'))  # İş ortaklarını birleştirme sayfasına yönlendir

    # Kayıt olma işlemi
    if register_form.validate_on_submit() and 'register' in request.form:
        # Veritabanına kaydetme işlemleri
        username = register_form.username.data
        password = register_form.password.data  # Şifreyi hash'lemeyi unutmayın!
        email=register_form.email.data
        idea=register_form.idea.data
        city=register_form.city
        district=register_form.district
        skills = register_form.skills.data
        interests = register_form.interests.data
        work_style = register_form.work_style.data

        # Burada kullanıcıyı veritabanına ekleyin
        # Örnek: insert_user_to_db(username, password, skills, interests, work_style)

        flash('Başarıyla kayıt oldunuz! Şimdi giriş yapabilirsiniz.')
        return redirect(url_for('home'))  # Ana sayfaya yönlendir

    return render_template('home.html', login_form=login_form, register_form=register_form)





@app.route('/api/sor', methods=['POST'])
@login_required
def api_soru_sor():
    data = request.json
    question = data.get("question")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Bu bir yazılım projesi fikirleri üreten chatbot'tur."},
            {"role": "user", "content": question}
        ]
    )

    return jsonify({'cevap': response.choices[0].message['content']})


@app.route('/chat')
@login_required
def chat_page():
    return render_template('chat.html')



if __name__ == '__main__':
    app.run(debug=True , port=8000)








