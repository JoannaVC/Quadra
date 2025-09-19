# se guardan todas las rutas para flask

#EJEMPLO_PRUEBA_DB
from app import app, db
from DB.models import Usuario
from flask import render_template, redirect, url_for
import os

@app.route('/add_user/<nombre>/<email>')
def add_user(nombre, email):
    usuario = Usuario(nombre=nombre, email=email)
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('usuarios'))

@app.route('/usuarios')
def usuarios():
    usuarios = Usuario.query.all()
    return render_template('auth/login.html', usuarios=usuarios)

#PRUEBA RENDER TEMPLATE
@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/login')
def login():
    return render_template('auth/login.html')

@app.route('/signup')
def signup():
    return render_template('auth/signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('main/dashboard.html')

@app.route('/mapa')
def mapa():
    api_key = os.getenv("GEOAPIFY_API_KEY", "8ba67a277ac44467b33467a772a0ca3e")
    return render_template("main/map.html", api_key=api_key)

@app.route('/foodstand')
def foodstand():
    return render_template("foodstand.html", user_is_creator=False)

@app.route('/comments')
def comments():
    return render_template("comments.html", user_is_creator=False)
