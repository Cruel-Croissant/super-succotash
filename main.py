from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
#-->
from flask_login import UserMixin, current_user, LoginManager, login_required, login_user,logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
login_manager = LoginManager()
login_manager.init_app(app)
# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE IN DB
class User(UserMixin,db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).where(User.id==user_id)).scalar()

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html",logged_in=current_user.is_authenticated)


@app.route('/register',methods=["GET","POST"])
def register():
    if request.method == "POST":
        data = request.form
        email = data["email"]
        user = db.session.execute(db.select(User).where(User.email==email)).scalar()
        if user:
            flash("Already signed up with this email,log in to proceed")
            return redirect(url_for('login'))
        pw = generate_password_hash(password=data["password"], method="pbkdf2:sha256", salt_length=8)
        new_user = User(
            name=data["name"],
            password=pw,
            email=data["email"]
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)#<--
        return redirect(url_for('secrets'))
    return render_template("register.html",logged_in=current_user.is_authenticated)


@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="POST":
        data = request.form
        email = data["email"]
        password = data["password"]
        user = db.session.execute(db.select(User).where(User.email==email)).scalar()
        print(user)
        if user:
            if check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for('secrets'))
            else:
                flash("incorrect password")
                return redirect(url_for('login'))
        else:
            flash("check email again")
            return redirect(url_for('login'))
    return render_template("login.html",logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    print(current_user.name)
    return render_template("secrets.html",username=current_user.name,logged_in=True)#<--


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory('static',"files/cheat_sheet.pdf",as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
#ddd