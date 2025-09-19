# inicializa Flask, DB 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from DB.config import Config

app = Flask(__name__) #instancia de flask
app.config.from_object(Config) #carga de configuracion
app.secret_key = 'W)31ZhFicMf1JkV-8Zb-^yy#[!d*u' #Clave secreta para sesiones y seguridad
db = SQLAlchemy(app) #Inicializa SQLAlchemy y ata a la app

from routes import *

with app.app_context():     
    # Inicializamos la DB     
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 