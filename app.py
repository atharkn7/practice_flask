from flask import Flask, render_template, redirect, flash, request
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email
from datetime import datetime

# Importing helpers
from helpers import format_date

# Configure app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey' #wtforms CSRF Token
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' #sqlite3 configuration

# Initializing the db
db = SQLAlchemy()
db.init_app(app)

# Creating a users model
class Users(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    date_added: Mapped[datetime] = mapped_column(default=datetime.now())

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"

# Create form classes
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        name = form.name.data.strip()
        email = form.email.data.strip()

        # Add to db
        user = Users.query.filter_by(email=email).first()
        if user is None:
            user = Users(name=name, email=email)
            db.session.add(user)
            db.session.commit()
        
        # Clearing form
        form.name.data = ''
        form.email.data = ''

        flash(f'{name.title()}, you are Registered!')
        return redirect('/register')
      
    # Showing table incase of GET
    registered_users = db.session.execute(db.select(Users).order_by(Users.id)).scalars().all()

    # Formatting date 
    format_date(registered_users)

    return render_template('register.html', form=form, registered_users=registered_users)


# All registered users route
@app.route('/users')
def users():
    # Querying for all users
    registered_users = db.session.execute(db.select(Users).order_by(Users.id)).scalars().all()
    # Formatting date 
    format_date(registered_users)

    return render_template('users.html', registered_users=registered_users)

# Update selected user
@app.route("/update/<user_id>", methods=["GET", "POST"])
def update(user_id):
    # Form object to create a form
    form = RegisterForm()

    # Querying db for selected user_id
    user = db.get_or_404(Users, user_id)

    if request.method == "POST":
        # Updating user
        if form.validate_on_submit():
            # Updating values
            user.name = form.name.data.strip()
            user.email = form.email.data.strip()
            # Updating db
            db.session.commit()

        # Deleting user
        delete = request.form.get('delete')
        if delete:
            db.session.delete(user)
            db.session.commit()

        return redirect("/users")

    return render_template('update.html', user=user, form=form)

# Error handling routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404