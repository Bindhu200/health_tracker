from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health.db'
db = SQLAlchemy(app)

# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    bmi = db.Column(db.Float)
    bp = db.Column(db.String(20), nullable=True)
    date = db.Column(db.String(20))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!')
            return redirect(url_for('register'))
        
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            records = Record.query.filter_by(user_id=user.id).order_by(Record.date.desc()).limit(7).all()
            return render_template('dashboard.html', user=user, records=records)
        flash('Wrong email or password!')
    return render_template('login.html')

@app.route('/save', methods=['POST'])
def save():
    user_id = request.form['user_id']
    weight = float(request.form['weight'])
    height = float(request.form['height']) / 100
    bmi = round(weight / (height * height), 2)
    bp = request.form.get('bp', '')

    new_record = Record(user_id=user_id, weight=weight, height=height*100, bmi=bmi, bp=bp, date=datetime.now().strftime("%d-%m-%Y"))
    db.session.add(new_record)
    db.session.commit()
    
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
