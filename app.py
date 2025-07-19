from click import style
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import *
from sqlalchemy.orm import relationship
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from flask_cors import CORS
from sqlalchemy import or_
# kutub honalar

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
DB_USER = os.getenv("DB_USER", 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', "123")
DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
DB_NAME = os.getenv('DB_NAME', 'oquv')
database_path = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_DATABASE_URI'] = database_path
app.config['SECRET_KEY'] = "shgfusgrfuysag"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# database ruhsatlar


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    email = Column(String)
    photo = Column(String)
    password = Column(String)
    year = Column(String)
    role = Column(String, default="user")
    phone = Column(String)
    created_at = Column(String)
    kurs = db.relationship('Kurs', secondary='user_kurs', backref='users')

    def adds(self):
        db.session.add(self)
        db.session.commit()
# User

class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    email = Column(String)
    photo = Column(String)
    password = Column(String)
    role = Column(String, default="teacher")
    year = Column(String)

    kurslar = relationship("Kurs", backref="teacher", order_by="Kurs.id")
# teacher

class Predment(db.Model):
    __tablename__ = 'predment'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    kurs = relationship("Kurs", backref="predment", order_by="Kurs.id")
#     kurs turi Predment


class Kurs(db.Model):
    __tablename__ = 'kurs'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    about = Column(String)
    photo = Column(String)
    price = Column(Integer)
    predment_id = Column(Integer, ForeignKey("predment.id"))
    teacher_id = Column(Integer, ForeignKey("teacher.id"))
#     kurs




class Zapis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    kurs_id = db.Column(db.Integer, db.ForeignKey('kurs.id'))
    status = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='zapislar')
    kurs = db.relationship('Kurs', backref='zapislar')
#     kurs zpisatsiyasi


user_kurs = db.Table('user_kurs',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('kurs_id', db.Integer, db.ForeignKey('kurs.id'))
                     )
# meny to meny kurs zapisatsiyasi


def online_user():
    get_user = None
    if "name" in session:
        get_user = User.query.filter(User.name == session['name']).first()
    return get_user
#   sessiyada kim login bo‘lganini aniqlaydi User


def online_tech():
    get_tech = None
    if "name" in session:
        get_tech = Teacher.query.filter(Teacher.name == session['name']).first()
    return get_tech
#  sessiyada kim login bo‘lganini aniqlaydi Teacher


@app.route('/')
def turonedu():
    current_user = online_user()
    teacher = online_tech()
    if not current_user or teacher:
        return redirect(url_for("login"))
    return render_template("main.html", current_user=current_user, teacher=teacher)
# Foydalanuvchi yoki o'qituvchi login qilmagan bo‘lsa, login sahifasiga yuboradi.


@app.route('/mainturon')
def mainturon():
    current_user = online_user()
    teacher = online_tech()
    if not current_user or teacher:
        return redirect(url_for("login"))
    return render_template("main.html", current_user=current_user, teacher=teacher)


@app.route('/hisob/<role>/<int:user_id>', methods=['GET', 'POST'])
def hisob(role, user_id):
    if role == "student" or role == "admin" or role == "user":
        current_user = User.query.get(user_id)
    elif role == "teacher":
        current_user = Teacher.query.get(user_id)
    else:
        return "Noto'g'ri rol!", 400

    if not current_user:
        return "Foydalanuvchi topilmadi!", 404
    if not current_user:
        return "Foydalanuvchi topilmadi!", 404

    return render_template("Hisob.html", current_user=current_user, user_id=user_id, role=role)
# Berilgan roldagi foydalanuvchi profilini ko‘rsatadi.


@app.route('/adminfor/vievprofil/<role>/<int:user_id>', methods=['GET', 'POST'])
def vievprofil(role, user_id):
    teacher = online_tech()
    current_user = online_user()
    students = User.query.filter(User.id == user_id).first()
    current_year = datetime.now().year
    age_user = {}

    year_obj = datetime.strptime(students.year, "%Y-%m-%d")
    age = current_year - year_obj.year
    age_user[students.id] = age
    # foydalovchi tug`ulgan sanasi  hisoblab yoshini aniqlab beraadi

    return render_template("vievprofil.html", students=students, current_user=current_user, user_id=user_id, role=role,
                           teacher=teacher, age_user=age_user)
# Adminga foydalanuvchining profilini ko‘rsatadi, yoshi hisoblanadi.


@app.route('/register', methods=['GET', 'POST'])
def register():
    current_user = online_user()
    teacher = online_tech()
    predment = Predment.query.all()

    if current_user == "student":
        return "error code 500"
    if teacher:
        return "error code 678"
    if not current_user:
        return "error code 563"
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        year = request.form.get("year")
        photo = request.files["photo"]
        email = request.form.get('email')
        phone = request.form.get('phone')

        password = request.form.get('password')
        data = datetime.now().date()
        hashed = generate_password_hash(password=password, method="pbkdf2:sha256")
        photo_url = ''
        if photo:
            print(photo.filename)
            photo_file = secure_filename(photo.filename)
            photo_url = '/' + 'static/img/' + photo_file
            app.config['UPLOAD_FOLDER'] = 'static/img/'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file))
        add = User(
            name=name,
            surname=surname,
            email=email,
            password=hashed,
            photo=photo_url,
            year=year,
            phone=phone,
            created_at=data

        )
        add.adds()

        db.session.commit()

        return redirect(url_for('login'))
    return render_template("register.html", current_user=current_user, predment=predment)
# Yangi foydalanuvchini ro‘yxatdan o‘tkazadi. Foto yuklash, parol hash, bazaga qo‘shish.


@app.route('/login', methods=['GET', 'POST'])
def login():
    current_user = online_user()

    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        current_user = User.query.filter_by(name=name).first()
        if current_user and check_password_hash(current_user.password, password):
            session['name'] = current_user.name
            session['role'] = current_user.role
            return redirect(url_for('mainturon'))

        teacher = Teacher.query.filter_by(name=name).first()
        if teacher and check_password_hash(teacher.password, password):
            session['name'] = teacher.name
            session['role'] = teacher.role
            return redirect(url_for('mainturon'))

        return "Ism yoki parol xato!"

    return render_template('login.html', current_user=current_user)
# Foydalanuvchi yoki o'qituvchini login qiladi, session['name'] va role saqlanadi.


@app.route('/logout')
def logout():
    session["name"] = None
    return redirect(url_for("login"))
# Sessiyani tozalaydi.

@app.route('/edituser/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    current_user = User.query.get(id) or Teacher.query.get(id)

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']

        photo = request.files['photo']

        photo_url = ''
        if photo:
            photo_file = secure_filename(photo.filename)
            photo_url = '/' + 'static/img/' + photo_file
            app.config['UPLOAD_FOLDER'] = 'static/img'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file))

        current_user.name = name
        current_user.surname = surname

        current_user.photo = photo_url if photo else current_user.photo

        db.session.commit()
        return redirect(url_for('login', role=current_user.role, user_id=current_user.id))
    return render_template("edit user.html", current_user=current_user, user_id=current_user.id)
# Profilni (User yoki Teacher) tahrirlash.


@app.route('/techreg', methods=['GET', 'POST'])
def techreg():
    current_user = online_user()

    if not current_user or current_user.role == None:
        return redirect(url_for("mainturon"))

    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        year = request.form.get("year")
        email = request.form.get('email')
        password = request.form.get('password')
        photo = request.files['photo']
        print(password, name)

        hashed = generate_password_hash(password)
        photo_url = ''
        if photo:
            photo_file = secure_filename(photo.filename)
            photo_url = '/' + 'static/img/' + photo_file
            photo.save(os.path.join('static/img', photo_file))

        teacher = Teacher(
            name=name,
            surname=surname,
            email=email,
            password=hashed,
            photo=photo_url,
            year=year,
            role='teacher'
        )
        db.session.add(teacher)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("Teacher Register.html", current_user=current_user)


@app.route('/predment', methods=['GET', 'POST'])
def predment():
    current_user = online_user()
    teacher = online_tech()
    predments = Predment.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        predment = Predment(
            name=name
        )
        db.session.add(predment)
        db.session.commit()
        return redirect(url_for("turonedu"))
    if current_user.role == "stedent":
        return redirect(url_for("turonedu"))
    if teacher:
        return redirect(url_for("turonedu"))
    return render_template("predment.html", current_user=current_user, predments=predments)
# Admin yangi fan (predment) qo‘shadi.


@app.route('/kurs')
def kurs():
    current_user = online_user()
    kurslar = Kurs.query.all()
    teachers = Teacher.query.all()
    return render_template("kurs.html", current_user=current_user, kurslar=kurslar, teachers=teachers)
# Barcha kurslarni ko‘rsatadi.


@app.route('/delete_fro-m_kurs/<int:kurs_id>', methods=["POST"])
def delete_from_kurs(kurs_id):
    zapislar = Zapis.query.filter_by(kurs_id=kurs_id).all()
    for z in zapislar:
        db.session.delete(z)

    kurs = Kurs.query.get(kurs_id)

    if kurs:
        db.session.delete(kurs)
        db.session.commit()

    return redirect(url_for('kurs'))
# Kurs va unga bog‘langan zapislarni o‘chiradi.


@app.route('/delete_fro-m_user/<int:user_id>')
def delete_from_user(user_id):
    zapislar = Zapis.query.filter_by(user_id=user_id).all()
    for z in zapislar:
        db.session.delete(z)

    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('adminpage'))
# Foydalanuvchini va uning barcha kurs yozuvlarini o‘chiradi.


@app.route('/delete_fro-m_user/<int:teacher_id>', methods=["POST"])
def delete_from_teacher(teacher_id):
    product_to_delete = Teacher.query.get(teacher_id)

    if product_to_delete:
        db.session.delete(product_to_delete)
        db.session.commit()

    return redirect(url_for('adminpage'))
# O‘qituvchini o‘chiradi.


@app.route('/kurs/add_kurs', methods=['GET', 'POST'])
def add_kurs():
    current_user = online_user()
    teachers = online_tech()
    predment = Predment.query.all()
    teacher = Teacher.query.all()

    if request.method == 'POST':
        name = request.form.get('name')
        about = request.form.get('about')
        photo = request.files['photo']
        teacher_id = request.form.get('teacher_id')
        predment_id = request.form.get('predment')
        price = request.form.get("price")
        photo_url = ''
        if photo:
            photo_file = secure_filename(photo.filename)
            photo_url = '/' + 'static/img/' + photo_file
            photo.save(os.path.join('static/img', photo_file))

        kurs = Kurs(
            name=name,
            about=about,
            photo=photo_url,
            price=price,
            predment_id=predment_id,
            teacher_id=teacher_id
        )
        db.session.add(kurs)
        db.session.commit()
        return redirect(url_for("turonedu"))
    return render_template("add_kurs.html", current_user=current_user, teachers=teachers, predment=predment,
                           teacher=teacher)
# Admin yoki o'qituvchi yangi kurs qo‘shadi.


@app.route('/edit_kurs/<int:kurs_id>', methods=['GET', 'POST'])
def edit_kurs(kurs_id):
    current_user = online_user()
    teacher = online_tech()
    kurs = Kurs.query.get_or_404(kurs_id)
    teachers = Teacher.query.all()
    predmets = Predment.query.all()
    print(predmets)
    if request.method == 'POST':
        name = request.form.get('name')
        about = request.form.get('about')
        price = request.form.get('price')
        teacher_id = request.form.get('teacher_id')
        predment_id = request.form.get('predment_id')
        photo = request.files.get('photo')
        if photo:
            photo_file = secure_filename(photo.filename)
            photo_path = os.path.join('static/img', photo_file)
            photo.save(photo_path)
            kurs.photo = '/' + photo_path
        if kurs.name:
            kurs.name = name
        if kurs.about:
            kurs.about = about
        if kurs.price:
            kurs.price = price
        if kurs.teacher_id:
            kurs.teacher_id = teacher_id
        if kurs.predment_id:
            kurs.predment_id = predment_id
        if kurs.photo:
            kurs.photo = photo
        db.session.commit()
        return redirect(url_for('kurs'))

    return render_template('edit_kurs.html', kurs=kurs, current_user=current_user, teacher=teacher,
                           teachers=teachers, predmets=predmets)
# Kursni tahrirlash.

@app.route('/adminpage')
def adminpage():
    current_user = online_user()
    teacher = online_tech()
    current_users = User.query.all()
    teachers = Teacher.query.all()

    zapisi = Zapis.query.all()

    if current_user.role == "student":
        return "error code 499"
    if teacher:
        return "error code 098"

    return render_template("adminpage.html", current_users=current_users, current_user=current_user, teachers=teachers,
                           kurs=kurs, predment=predment, zapisi=zapisi)
# Admin panel bosh sahifasi: foydalanuvchilar, o‘qituvchilar, zapislar.


@app.route('/adminkurs', methods=['GET', 'POST'])
def adminkurs():
    current_user = online_user()
    teacher = online_tech()
    current_users = User.query.all()
    teachers = Teacher.query.all()
    predment = Predment.query.all()

    if current_user.role == "student":
        return "error code 499"
    if teacher:
        return "error code 098"

    if request.method == 'POST':
        if 'reset' in request.form:
            return redirect(url_for('adminkurs'))

        name = request.form.get('name')
        pred_id = request.form.get('pred_id', type=int)
        teacher_id = request.form.get('teacher_id', type=int)

        query = Kurs.query

        if name:
            query = query.filter(Kurs.name == name)

        if pred_id:
            query = query.filter(Kurs.predment_id == pred_id)

        if teacher_id:
            query = query.filter(Kurs.teacher_id == teacher_id)

        kurs = query.all()
    else:
        kurs = Kurs.query.all()

    return render_template("adminkurs.html", current_users=current_users, current_user=current_user,
                           kurs=kurs, predment=predment, teachers=teachers)
# Kurslarni filtr bilan ko‘rish: nomi, o‘qituvchisi, fani bo‘yicha.


@app.route('/adminteacher', methods=['GET', 'POST'])
def adminteacher():
    current_user = online_user()
    teacher = online_tech()

    if current_user.role == "student":
        return "error code 499"
    if teacher:
        return "error code 098"
    if request.method == 'POST':
        if 'reset' in request.form:
            return redirect(url_for('adminteacher'))

        name = request.form.get('name')
        surname = request.form.get('surname')
        year = request.form.get('year')
        query = Teacher.query.filter(Teacher.role == 'teacher')

        if name:
            query = query.filter(Teacher.name == name)
        if surname:
            query = query.filter(Teacher.surname == surname)
        if year:
            query = query.filter(Teacher.year == year)

        teachers = query.all()
    else:
        teachers = Teacher.query.filter(Teacher.role == 'teacher').all()
    teacher_student_counts = {}
    for t in teachers:
        kurslar = t.kurslar
        student_ids = set()
        for kurs in kurslar:
            zapislar = kurs.zapislar
            for zapis in zapislar:
                student_ids.add(zapis.user_id)
        teacher_student_counts[t.id] = len(student_ids)
    #     teacherning kurslariini hisoblab kursdagi oquvchiilarni hisoblaydi

    kurs = Kurs.query.all()
    return render_template("adminteacher.html", current_user=current_user, teachers=teachers, kurs=kurs,
                           teacher_stats=teacher_student_counts, predment=predment)
# O‘qituvchilarni filtrlash, o‘quvchilar soni bilan statistikasi.

@app.route('/adminuser', methods=['GET', 'POST'])
def adminuser():
    current_user = online_user()
    teacher = online_tech()
    teachers = Teacher.query.all()
    kurs = Kurs.query.all()
    predment = Predment.query.all()
    current_year = datetime.now().year

    if current_user.role == "student":
        return "error code 499"
    if teacher:
        return "error code 098"
    if request.method == 'POST':
        if 'reset' in request.form:
            return redirect(url_for('adminuser'))

        name = request.form.get('name')

        surname = request.form.get('surname')
        pred_id = request.form.getlist('predment')
        age = request.form.get('age')

        query = User.query.filter(User.role == 'student')
        if age == "0" or age == str:
            return redirect(url_for("adminuser"))
        if name:
            query = query.filter(User.name == name)
        elif age:
            age_current = int(age)
            birthday = current_year - age_current
            user_p = User.query.all()
            for user in user_p:
                if user.year:
                    year_obj = datetime.strptime(user.year, "%Y-%m-%d")
                    if year_obj.year == birthday:
                        print(year_obj.year)
                        query = query.filter(User.year == user.year)
        #                 asosiy yosh hisoblash
        if surname:
            query = query.filter(User.surname == surname)
        if pred_id:
            pred_ids = [int(pid) for pid in pred_id if pid.isdigit()]
            if pred_ids:
                query = query.join(User.kurs).filter(Kurs.id.in_(pred_ids))
        #         predment filter

        student = query.all()
        print(pred_id)
    else:
        student = User.query.filter(User.role == 'student').all()

    age_user = {}
    for students in student:
        year_obj = datetime.strptime(students.year, "%Y-%m-%d")
        age = current_year - year_obj.year
        age_user[students.id] = age
        # foydalovchi tug`ulgan sanasi  hisoblab yoshini aniqlab beraadi

    return render_template("adminuser.html", students=student, current_user=current_user, teachers=teachers,
                           kurs=kurs, predment=predment, age_user=age_user)
# Foydalanuvchilarni (student) filtrlash: fan, ism, yosh, familya.

@app.route('/admin_new_user', methods=['GET', 'POST'])
def admin_new_user():
    current_user = online_user()
    teacher = online_tech()
    teachers = Teacher.query.all()
    kurs = Kurs.query.all()
    predment = Predment.query.all()
    current_year = datetime.now().year

    if current_user.role == "student":
        return "error code 499"
    if teacher:
        return "error code 098"
    if request.method == 'POST':
        if 'reset' in request.form:
            return redirect(url_for('adminuser'))

        name = request.form.get('name')

        surname = request.form.get('surname')
        age = request.form.get('age')

        query = User.query.filter(User.role == 'user')
        if age == "0" or age == str:
            return redirect(url_for("adminuser"))
        if name:
            query = query.filter(User.name == name)
        elif age:
            age_current = int(age)
            birthday = current_year - age_current
            user_p = User.query.all()
            for user in user_p:
                if user.year:
                    year_obj = datetime.strptime(user.year, "%Y-%m-%d")
                    if year_obj.year == birthday:
                        print(year_obj.year)
                        query = query.filter(User.year == user.year)
        #                 filter
        if surname:
            query = query.filter(User.surname == surname)

        student = query.all()


    else:
        student = User.query.filter(User.role == 'user').all()
    age_user = {}
    for students in student:
        year_obj = datetime.strptime(students.year, "%Y-%m-%d")
        age = current_year - year_obj.year
        age_user[students.id] = age
        # foydalovchi tug`ulgan sanasi  hisoblab yoshini aniqlab beraadi
    return render_template("new user.html", students=student, current_user=current_user, teachers=teachers,
                           kurs=kurs, predment=predment, age_user=age_user)
# Oddiy foydalanuvchilarni (user) ko‘rish va tahlil qilish.


@app.route('/zapisi/<int:kurs_id>')
def Zapisi(kurs_id):
    current_user = online_user()
    teachers = Teacher.query.all()
    kurs = Kurs.query.get_or_404(kurs_id)
    zapisi = Zapis.query.filter_by(kurs_id=kurs.id).all()
    return render_template("kursviwer.html", kurs=kurs, zapisi=zapisi, current_user=current_user, teachers=teachers)
# Kursga yozilganlar ro‘yxatini ko‘rsatadi.


@app.route('/list_of_student/<int:kurs_id>')
def list_of_student(kurs_id):
    current_user = online_user()
    return render_template("listofstudent.html", kurs_id=kurs_id, current_user=current_user)
#    kursga qo‘shilmaganlar ro‘yxati.


@app.route('/api/list_of_del_stu/<int:kurs_id>')
def list_of_studentdel(kurs_id):
    current_user = online_user()
    return render_template("listofdelstu.html", kurs_id=kurs_id, current_user=current_user)


@app.route('/api/date_of_student/<int:kurs_id>', methods=['GET'])
def date_of_student(kurs_id):
    students = User.query.filter(
        or_(
            User.role == 'student',
            User.role == 'user'
        )
    ).all()
    # role user va studentligini oladi

    data_of_userstudent = []
    for student in students:

        zapis = Zapis.query.filter_by(user_id=student.id, kurs_id=kurs_id).first()
        if not zapis:
            data_of_userstudent.append({
                "id": student.id,
                "name": student.name,
                "surname": student.surname,
                "email": student.email,
                "phone": student.phone
            })

    return jsonify(data_of_userstudent), 200
# Kursga yozilmagan foydalanuvchilarni qaytaradi.


@app.route('/api/date_of_student_v2/<int:kurs_id>', methods=['GET'])
def date_of_student_v2(kurs_id):
    students = User.query.filter(
        or_(
            User.role == 'student',
            User.role == 'user'
        )
    ).all()
    # role user va studentligini oladi
    data_of_userstudent = []

    for student in students:
        zapis = Zapis.query.filter_by(user_id=student.id, kurs_id=kurs_id).first()
        if zapis:
            data_of_userstudent.append({
                "id": student.id,
                "name": student.name,
                "surname": student.surname,
                "email": student.email,
                "phone": student.phone
            })

    return jsonify(data_of_userstudent), 200
# Kursga yozilgan foydalanuvchilarni qaytaradi.

@app.route('/api/get_of_stu/<int:kurs_id>', methods=['POST'])
def get_of_stu(kurs_id):
    try:
        data = request.get_json()
        student_ids = data.get('buttom_set', [])
        print("Kelgan student_idlar:", student_ids)
        # jsonda malumotni olib mssive qilib oladi

        kurs = Kurs.query.get(kurs_id)
        if not kurs:
            return jsonify({"error": "Kurs topilmadi"}), 404

        for student_id in student_ids:
            student = User.query.get(int(student_id))
            if student:
                if student not in kurs.users:
                    kurs.users.append(student)

                if student.role == 'user':
                    student.role = 'student'

                zapis = Zapis.query.filter_by(user_id=student.id, kurs_id=kurs.id).first()
                if not zapis:
                    new_zapis = Zapis(user_id=student.id, kurs_id=kurs.id, status=True)
                    db.session.add(new_zapis)

        db.session.commit()
        return jsonify({"success": True, "added": student_ids}), 200

    except Exception as e:
        import traceback
        print("XATO:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
#     JSON orqali kursga bir nechta foydalanuvchini qo‘shadi (status=True).


@app.route('/api/remove_student_from_course/<int:kurs_id>', methods=['POST'])
def remove_student_from_course(kurs_id):
    try:
        data = request.get_json()
        student_ids = data.get('buttom_set', [])
        print("Kelgan student_idlar:", student_ids)
        # jsonda malumotni olib mssive qilib oladi

        kurs = Kurs.query.get(kurs_id)
        if not kurs:
            return jsonify({"error": "Kurs topilmadi"}), 404

        for student_id in student_ids:
            student = User.query.get(int(student_id))
            if student:

                if student in kurs.users:
                    kurs.users.remove(student)

                zapis = Zapis.query.filter_by(user_id=student.id, kurs_id=kurs.id).first()
                if zapis:
                    db.session.delete(zapis)

        db.session.commit()
        return jsonify({"success": True, "removed": student_ids}), 200

    except Exception as e:
        import traceback
        print("XATO:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
#     Kursdan bir nechta foydalanuvchini o‘chiradi.


@app.route('/selectrOI')
def selectrOI():
    current_user = online_user()
    kurses = Kurs.query.all()
    return render_template("sentuserkurs.html", current_user=current_user, kurses=kurses)
# Kurs tanlash sahifasi.


@app.route('/api/StudentList')
def StudentList():
    students = User.query.filter(
        or_(
            User.role == 'student',
            User.role == 'user'
        )
    ).all()


    data_of_userstudents = []

    for student in students:
        data_of_userstudents.append({
            "id": student.id,
            "name": student.name,
            "surname": student.surname,
            "email": student.email,
            "phone": student.phone
        })

    return jsonify(data_of_userstudents)
# Hammasi (student va user) JSON shaklida qaytariladi.

@app.route('/add_students_json/<int:kurs_id>', methods=['POST'])
def add_students_json(kurs_id):
    data = request.get_json()
    student_ids = data.get('student_ids', [])
    added = 0
    for student_id in student_ids:
        Zapis.query.filter_by(user_id=student_id, status=False).delete()
        zapis = Zapis(user_id=student_id, status=True, kurs_id=kurs_id)
        student = User.query.get(student_id)
        if student:
            student.role = 'student'
        db.session.add(zapis)
        added += 1
    db.session.commit()
    return jsonify({
        'status': 'success',
        'added': added,
        'message': f'{added} o‘quvchi qo‘shildi'
    })
# JSON orqali tanlangan talabalarni kursga qo‘shadi.

@app.route('/subscribe/<int:kurs_id>')
def subscribe(kurs_id):
    user = online_user()
    kurs = Kurs.query.get_or_404(kurs_id)

    if not user:
        return redirect(url_for("login"))

    existing = Zapis.query.filter_by(user_id=user.id, kurs_id=kurs.id).first()
    if not existing:
        ariza = Zapis(user_id=user.id, kurs_id=kurs.id, status=False)
        db.session.add(ariza)
        db.session.commit()

    return redirect(url_for("Zapisi", kurs_id=kurs.id))
# Oddiy foydalanuvchilarni (user) ko‘rish va tahlil qilish.


@app.route('/galochka/<int:user_id>/<int:kurs_id>')
def galochka(user_id, kurs_id):
    zapi = Zapis.query.filter_by(user_id=user_id, kurs_id=kurs_id).first()
    user = User.query.get_or_404(user_id)
    kurs = Kurs.query.get_or_404(kurs_id)
    if zapi and not zapi.status:
        zapi.status = True

        if kurs not in user.kurs:
            user.kurs.append(kurs)
            if user.role == "user":
                user.role = "student"

        db.session.commit()
    return redirect(url_for('adminpage', kurs_id=kurs.id))
# Admin yoki teacher kursga yozilgan talabani tasdiqlaydi (status=True).


@app.route('/bekor_qilish/<int:user_id>/<int:kurs_id>')
def bekor_qilish(user_id, kurs_id):
    zapi = Zapis.query.filter_by(user_id=user_id, kurs_id=kurs_id).first()
    user = User.query.get(user_id)
    kurs = Kurs.query.get(kurs_id)

    if zapi:
        db.session.delete(zapi)

    if kurs in user.kurs:
        user.kurs.remove(kurs)

    db.session.commit()
    return redirect(url_for('adminpage', kurs_id=kurs_id))
# Talabaning yozuvini va aloqani bekor qiladi.

@app.route('/adminfor/edituserforadmin/<int:id>', methods=['GET', 'POST'])
def edituserforadmin(id):
    current_user = online_user()
    predment = Predment.query.all()
    student = User.query.get(id) or Teacher.query.get(id)
    kurs_list = Kurs.query.all()

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        year = request.form.get("year")
        kurs_id = request.form.get("kurs_id")
        email = request.form['email']
        password = request.form['password']
        photo = request.files['photo']

        photo_url = ''
        if photo:
            photo_file = secure_filename(photo.filename)
            photo_url = '/' + 'static/img/' + photo_file
            app.config['UPLOAD_FOLDER'] = 'static/img'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file))

        if password:
            password = generate_password_hash(password)

        student.name = name
        student.surname = surname
        student.year = year
        student.email = email
        student.password = password if password else student.password
        student.photo = photo_url if photo else student.photo
        if kurs_id:
            kurs = Kurs.query.get(kurs_id)
            if kurs:
                student.kurs.clear()
                student.kurs.append(kurs)
                if student.role == 'user':
                    student.role = 'student'
                Zapis.query.filter_by(user_id=id).delete()
                new_zapis = Zapis(user_id=id, kurs_id=kurs_id, status=True)
                db.session.add(new_zapis)
        db.session.commit()
        # edit qilganda userning predmentini o`zgartiradi
        return redirect(url_for("adminuser"))
    return render_template("edit user for admin.html", id=id, current_user=current_user, predment=predment,
                           kurs=kurs_list,
                           student=student)
# Admin tomonidan foydalanuvchi ma’lumotlarini o‘zgartirish.


if __name__ == '__main__':
    app.run()
