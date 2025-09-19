# se guardan todas las rutas para flask

#EJEMPLO_PRUEBA_DB
from app import app, db
from DB.models import Usuario, Puesto
from flask import request, session, flash, abort, render_template, redirect, url_for, jsonify
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

@app.route('/map')
def mapa():
    api_key = os.getenv("GEOAPIFY_API_KEY", "8ba67a277ac44467b33467a772a0ca3e")
    return render_template("main/map.html", api_key=api_key)

@app.route('/add_place', methods=['POST'])
def add_place():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    data = request.get_json()
    nombre = data.get('nombre')
    lat = data.get('lat')
    lng = data.get('lng')
    ubicacion = f"{lat},{lng}"
    creador_id = session['user_id']
    nuevo_puesto = Puesto(nombre=nombre, ubicacion=ubicacion, creador_id=creador_id)
    db.session.add(nuevo_puesto)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/foodstand')
def foodstand():
    return render_template("foodstand.html", user_is_creator=False)

@app.route('/comments')
def comments():
    return render_template("comments.html", user_is_creator=False)
