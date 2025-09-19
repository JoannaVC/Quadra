# se guardan todas las rutas para flask

#EJEMPLO_PRUEBA_DB
from app import app, db
from DB.models import Usuario
from flask import request
from flask import session, flash
from flask import render_template, redirect, url_for
import os

#PRUEBA RENDER TEMPLATE
@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Usa los nombres de columna correctos
        usuario = Usuario.query.filter_by(correo=email, contraseña=password).first()

        if usuario:
            session['user_id'] = usuario.id
            session['user_name'] = usuario.nom_usuario
            return redirect(url_for('dashboard'))
        else:
            flash("Correo o contraseña incorrectos")
            return redirect(url_for('login'))

    return render_template('auth/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        #Agregar a la DB
        usuario = Usuario(nom_usuario=nombre, correo=email, contraseña=password)
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('dashboard'))

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
