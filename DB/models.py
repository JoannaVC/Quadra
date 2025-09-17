# creacion de tablas para la base de datos
from app import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nom_usuario = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    foto = db.Column(db.String(200))
    correo = db.Column(db.String(120), unique=True, nullable=False)
    contraseña = db.Column(db.String(128), nullable=False)  # por ahora texto plano

    puestos = db.relationship('Puesto', backref='creador', lazy=True)
    reseñas = db.relationship('Reseña', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.nom_usuario}>'

class Puesto(db.Model):
    __tablename__ = 'puestos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(50), nullable=False)  # por ahora string; después GEOGRAPHY
    foto = db.Column(db.String(200))
    creador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    cal_promedio = db.Column(db.Float, default=0.0)

    reseñas = db.relationship('Reseña', backref='puesto', lazy=True)

    def __repr__(self):
        return f'<Puesto {self.nombre}>'

class Etiqueta(db.Model):
    __tablename__ = 'etiquetas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Etiqueta {self.nombre}>'

class Reseña(db.Model):
    __tablename__ = 'reseñas'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    puesto_id = db.Column(db.Integer, db.ForeignKey('puestos.id'), nullable=False)
    comentario = db.Column(db.Text, nullable=False)
    calificacion = db.Column(db.Integer)
    fecha = db.Column(db.DateTime, server_default=db.func.now())

    etiquetas = db.relationship(
        'Etiqueta',
        secondary='reseñas_etiquetas',
        backref=db.backref('reseñas', lazy='dynamic')
    )

    def __repr__(self):
        return f'<Reseña {self.id} usuario {self.usuario_id}>'

reseñas_etiquetas = db.Table(
    'reseñas_etiquetas',
    db.Column('reseña_id', db.Integer, db.ForeignKey('reseñas.id'), primary_key=True),
    db.Column('etiqueta_id', db.Integer, db.ForeignKey('etiquetas.id'), primary_key=True)
)
