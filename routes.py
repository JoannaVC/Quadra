# se guardan todas las rutas para flask

#EJEMPLO_PRUEBA_DB
from app import app, db
from DB.models import Usuario
from flask import render_template, redirect, url_for

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