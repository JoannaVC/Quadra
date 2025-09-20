# se guardan todas las rutas para flask
#EJEMPLO_PRUEBA_DB
from app import app, db
from DB.models import Usuario, Puesto
from flask import request, session, flash, render_template, redirect, url_for, jsonify, abort
import os
from apis.mapas import get_address_from_coords


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

@app.route('/comments/<int:id>', methods=['GET'])
def comments(id):
    puesto = Puesto.query.get_or_404(id)
    comentarios = puesto.reseñas
    user_is_creator = 'user_id' in session and puesto.creador_id == session['user_id']
    return render_template(
        "comments.html",
        puesto=puesto,
        comentarios=comentarios,
        user_is_creator=user_is_creator
    )

# Ruta para agregar un nuevo comentario (solo usuarios no creadores)
@app.route('/comments/<int:id>/nuevo', methods=['POST'])
def nuevo_comentario(id):
    puesto = Puesto.query.get_or_404(id)
    if 'user_id' not in session or puesto.creador_id == session['user_id']:
        abort(403)
    from DB.models import Reseña
    usuario_id = session['user_id']
    # Verifica si ya existe una reseña de este usuario para este puesto
    existente = Reseña.query.filter_by(usuario_id=usuario_id, puesto_id=puesto.id).first()
    if existente:
        # Ya existe, no crear otra
        return redirect(url_for('comments', id=puesto.id))
    comentario = request.form['comentario']
    calificacion = int(request.form['calificacion'])
    nueva_reseña = Reseña(usuario_id=usuario_id, puesto_id=puesto.id, comentario=comentario, calificacion=calificacion)
    db.session.add(nueva_reseña)
    # Actualiza cal_promedio
    reseñas = puesto.reseñas + [nueva_reseña]
    puesto.cal_promedio = sum(r.calificacion for r in reseñas) / len(reseñas)
    db.session.commit()
    return redirect(url_for('comments', id=puesto.id))

@app.route('/foodstand/<int:id>')
def foodstand(id):
    puesto = Puesto.query.get_or_404(id)
    user_is_creator = 'user_id' in session and puesto.creador_id == session['user_id']
    lat, lng = map(float, puesto.ubicacion.split(','))
    api_key = os.getenv("GEOAPIFY_API_KEY", "8ba67a277ac44467b33467a772a0ca3e")
    direccion = get_address_from_coords(lat, lng, api_key)
    first = request.args.get('first') == 'true'
    # Busca si el creador ya dejó reseña
    tiene_reseña = any(r.usuario_id == puesto.creador_id for r in puesto.reseñas)
    return render_template("foodstand.html", puesto=puesto, user_is_creator=user_is_creator, direccion=direccion, first=first, tiene_reseña=tiene_reseña)

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
    return jsonify({'success': True, 'id': nuevo_puesto.id})

@app.route('/get_places')
def get_places():
    puestos = Puesto.query.all()
    lugares = []
    for puesto in puestos:
        lat, lng = map(float, puesto.ubicacion.split(','))
        lugares.append({
            'id': puesto.id,  # <-- agrega el id
            'nombre': puesto.nombre,
            'lat': lat,
            'lng': lng
        })
    return jsonify(lugares)

@app.route('/foodstand/<int:id>/completar', methods=['POST'])
def completar_puesto(id):
    puesto = Puesto.query.get_or_404(id)
    if 'user_id' not in session or puesto.creador_id != session['user_id']:
        abort(403)
    # Guardar foto
    foto = request.files['foto']
    if foto:
        # Asegura que la carpeta exista y usa ruta absoluta
        images_folder = os.path.join(app.root_path, 'static', 'images')
        os.makedirs(images_folder, exist_ok=True)
        filename = f"puesto_{puesto.id}.jpg"
        path = os.path.join(images_folder, filename)
        foto.save(path)
        puesto.foto = f"/static/images/{filename}"
    # Guardar reseña
    comentario = request.form['comentario']
    calificacion = int(request.form['calificacion'])
    from DB.models import Reseña
    nueva_reseña = Reseña(usuario_id=puesto.creador_id, puesto_id=puesto.id, comentario=comentario, calificacion=calificacion)
    db.session.add(nueva_reseña)
    # Actualiza cal_promedio
    reseñas = puesto.reseñas + [nueva_reseña]
    puesto.cal_promedio = sum(r.calificacion for r in reseñas) / len(reseñas)
    db.session.commit()
    return redirect(url_for('foodstand', id=puesto.id))

@app.route('/foodstand/<int:id>/editar', methods=['GET', 'POST'])
def editar_puesto(id):
    puesto = Puesto.query.get_or_404(id)
    if 'user_id' not in session or puesto.creador_id != session['user_id']:
        abort(403)
    from DB.models import Reseña
    reseña = Reseña.query.filter_by(usuario_id=puesto.creador_id, puesto_id=puesto.id).first()
    if request.method == 'POST':
        # Actualizar foto si se sube una nueva
        foto = request.files.get('foto')
        if foto and foto.filename:
            images_folder = os.path.join(app.root_path, 'static', 'images')
            os.makedirs(images_folder, exist_ok=True)
            filename = f"puesto_{puesto.id}.jpg"
            path = os.path.join(images_folder, filename)
            foto.save(path)
            puesto.foto = f"/static/images/{filename}"
        # Actualizar reseña y calificación
        comentario = request.form['comentario']
        calificacion = int(request.form['calificacion'])
        if reseña:
            reseña.comentario = comentario
            reseña.calificacion = calificacion
        else:
            reseña = Reseña(usuario_id=puesto.creador_id, puesto_id=puesto.id, comentario=comentario, calificacion=calificacion)
            db.session.add(reseña)
        # Actualizar cal_promedio
        todas = puesto.reseñas
        puesto.cal_promedio = sum(r.calificacion for r in todas) / len(todas) if todas else calificacion
        db.session.commit()
        return redirect(url_for('foodstand', id=puesto.id))
    return render_template('editar_puesto.html', puesto=puesto, reseña=reseña)

@app.route('/comments/<int:puesto_id>/editar/<int:id>', methods=['GET', 'POST'])
def editar_comentario(puesto_id, id):
    from DB.models import Reseña
    reseña = Reseña.query.get_or_404(id)
    puesto = Puesto.query.get_or_404(puesto_id)
    if 'user_id' not in session or reseña.usuario_id != session['user_id'] or puesto.creador_id == session['user_id']:
        abort(403)
    if request.method == 'POST':
        reseña.comentario = request.form['comentario']
        reseña.calificacion = int(request.form['calificacion'])
        # Actualiza cal_promedio
        todas = puesto.reseñas
        puesto.cal_promedio = sum(r.calificacion for r in todas) / len(todas) if todas else reseña.calificacion
        db.session.commit()
        return redirect(url_for('comments', id=puesto.id))
    return render_template('editar_comentario.html', puesto=puesto, reseña=reseña)

@app.route('/comments/<int:puesto_id>/eliminar/<int:id>', methods=['POST'])
def eliminar_comentario(puesto_id, id):
    from DB.models import Reseña
    reseña = Reseña.query.get_or_404(id)
    puesto = Puesto.query.get_or_404(puesto_id)
    # Solo el creador del puesto puede eliminar comentarios
    if 'user_id' not in session or puesto.creador_id != session['user_id']:
        abort(403)
    db.session.delete(reseña)
    # Actualiza cal_promedio
    todas = [r for r in puesto.reseñas if r.id != id]
    if todas:
        puesto.cal_promedio = sum(r.calificacion for r in todas) / len(todas)
    else:
        puesto.cal_promedio = 0
    db.session.commit()
    return redirect(url_for('comments', id=puesto.id))


