from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime
import logging

# ——— Configuración básica ———
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL no configurada")
    return psycopg2.connect(DATABASE_URL)

# ——— Creación / migración de tablas ———
def init_db():
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Psicología
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS psicologia (
                    id SERIAL PRIMARY KEY,
                    atleta_id INTEGER NOT NULL,
                    estado_emocional TEXT,
                    motivacion TEXT,
                    estres INTEGER,
                    observaciones TEXT
                );
            """)
            # Nutrición
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nutricion (
                    id SERIAL PRIMARY KEY,
                    id_atleta INTEGER NOT NULL,
                    fecha DATE NOT NULL,
                    peso REAL,
                    altura REAL,
                    imc REAL,
                    observaciones TEXT,
                    UNIQUE (id_atleta, fecha)
                );
            """)
            # Médico
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medico (
                    id SERIAL PRIMARY KEY,
                    atleta_id INTEGER NOT NULL,
                    fecha DATE NOT NULL,
                    temperatura REAL,
                    presion_arterial TEXT,
                    diagnostico TEXT,
                    tratamiento TEXT,
                    observaciones TEXT
                );
            """)
            # Entrenamiento
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entrenamiento (
                    id SERIAL PRIMARY KEY,
                    id_atleta INTEGER NOT NULL,
                    tipo_entrenamiento TEXT,
                    duracion INTEGER,
                    intensidad TEXT,
                    observaciones TEXT
                );
            """)
            # Evento
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evento (
                    id SERIAL PRIMARY KEY,
                    id_atleta INTEGER,
                    nombre TEXT,
                    fecha DATE,
                    lugar TEXT,
                    descripcion TEXT
                );
            """)
            # Autoseguimiento
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS autoseguimiento (
                    id SERIAL PRIMARY KEY,
                    atleta_id INTEGER NOT NULL,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    calidad_sueno INTEGER,
                    horas_sueno REAL,
                    fatiga INTEGER,
                    dolor_muscular INTEGER,
                    estres INTEGER,
                    estado_animo INTEGER,
                    comentarios TEXT
                );
            """)
            # Consentimientos de tutores
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Consentimientos_Tutores (
                    id SERIAL PRIMARY KEY,
                    nombre_menor TEXT NOT NULL,
                    edad_menor INTEGER NOT NULL,
                    nombre_tutor TEXT NOT NULL,
                    relacion_tutor TEXT,
                    contacto_tutor TEXT NOT NULL,
                    aceptado BOOLEAN DEFAULT TRUE,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()

init_db()

# ——— RUTAS ———

@app.route('/', methods=['GET'])
def home():
    return jsonify({"estado": "API corriendo"}), 200

@app.route("/get_atleta", methods=["POST"])
def get_atleta():
    data = request.get_json()
    nombre = data.get("nombre")

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id_atleta FROM atletas WHERE nombre = %s", (nombre,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            return jsonify({"id_atleta": result[0]})
        else:
            return jsonify({"error": "Atleta no encontrado"}), 404

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Error en servidor"}), 500



# ——— Psicología ———
@app.route('/psicologia', methods=['POST'])
def psicologia():
    data = request.get_json() or {}
    for k in ('atleta_id','estado_emocional','motivacion','estres'):
        if k not in data:
            return jsonify({"error": f"{k} es obligatorio"}), 400
    observaciones = data.get('observaciones', '')

    try:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO psicologia (atleta_id, estado_emocional, motivacion, estres, observaciones)
                    VALUES (%s, %s, %s, %s, %s);
                """, (
                    int(data['atleta_id']),
                    data['estado_emocional'],
                    data['motivacion'],
                    int(data['estres']),
                    observaciones
                ))
            conn.commit()
        return jsonify({"mensaje":"Psicología registrada"}), 200
    except Exception as e:
        logging.exception("Error en /psicologia")
        return jsonify({"error":"Error interno"}), 500

# ——— Nutrición ———
@app.route('/nutricion', methods=['POST'])
def nutricion():
    data = request.get_json() or {}
    for k in ('id_atleta','fecha','peso','altura','imc','observaciones'):
        if k not in data:
            return jsonify({"error": f"{k} es obligatorio"}), 400
    try:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO nutricion (id_atleta, fecha, peso, altura, imc, observaciones)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (id_atleta, fecha) DO UPDATE SET
                      peso = EXCLUDED.peso,
                      altura = EXCLUDED.altura,
                      imc = EXCLUDED.imc,
                      observaciones = EXCLUDED.observaciones;
                """, (
                    int(data['id_atleta']),
                    datetime.strptime(data['fecha'],'%Y-%m-%d').date(),
                    float(data['peso']),
                    float(data['altura']),
                    float(data['imc']),
                    data['observaciones']
                ))
            conn.commit()
        return jsonify({"mensaje":"Nutrición registrada"}), 200
    except Exception as e:
        logging.exception("Error en /nutricion")
        return jsonify({"error":"Error interno"}), 500

# ——— Médico ———
@app.route('/medico', methods=['POST'])
def medico():
    data = request.get_json() or {}
    for k in ('id_atleta','fecha','temperatura','presion_arterial','diagnostico','tratamiento','observaciones'):
        if k not in data:
            return jsonify({"error": f"{k} es obligatorio"}), 400
    try:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO medico (atleta_id, fecha, temperatura, presion_arterial, diagnostico, tratamiento, observaciones)
                    VALUES (%s,%s,%s,%s,%s,%s,%s);
                """, (
                    int(data['id_atleta']),
                    datetime.strptime(data['fecha'],'%Y-%m-%d').date(),
                    float(data['temperatura']),
                    data['presion_arterial'],
                    data['diagnostico'],
                    data['tratamiento'],
                    data['observaciones']
                ))
            conn.commit()
        return jsonify({"mensaje":"Médico registrado"}), 200
    except Exception as e:
        logging.exception("Error en /medico")
        return jsonify({"error":"Error interno"}), 500

# ——— Entrenamiento ———
@app.route('/entrenamiento', methods=['POST'])
def entrenamiento():
    data = request.get_json() or {}
    for k in ('atleta_id', 'tipo_entrenamiento', 'duracion', 'intensidad', 'observaciones'):
        if k not in data:
            return jsonify({"error": f"{k} es obligatorio"}), 400
    try:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO entrenamiento (atleta_id, tipo_entrenamiento, duracion, intensidad, observaciones)
                    VALUES (%s,%s,%s,%s,%s);
                """, (
                    data['atleta_id'],
                    data['tipo_entrenamiento'],
                    int(data['duracion']),
                    data['intensidad'],
                    data['observaciones']
                ))
            conn.commit()
        return jsonify({"mensaje": "Entrenamiento registrado"}), 200
    except Exception as e:
        logging.exception("Error en /entrenamiento")
        return jsonify({"error": "Error interno"}), 500

# ——— Eventos ———
@app.route('/add_evento', methods=['POST'])
def agregar_evento():
    data = request.get_json() or {}
    for k in ('id_atleta','nombre','fecha','lugar','descripcion'):
        if k not in data:
            return jsonify({"error": f"{k} es obligatorio"}), 400
    try:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO evento (id_atleta, nombre, fecha, lugar, descripcion)
                    VALUES (%s,%s,%s,%s,%s);
                """, (
                    int(data['id_atleta']),
                    data['nombre'],
                    datetime.strptime(data['fecha'],'%Y-%m-%d').date(),
                    data['lugar'],
                    data['descripcion']
                ))
            conn.commit()
        return jsonify({"mensaje":"Evento registrado"}), 200
    except Exception as e:
        logging.exception("Error en /add_evento")
        return jsonify({"error":"Error interno"}), 500

# ——— Autoseguimiento ———
@app.route('/add_autoseguimiento', methods=['POST'])
def agregar_autoseguimiento():
    data = request.get_json() or {}
    if 'id_atleta' not in data:
        return jsonify({"error":"id_atleta es obligatorio"}), 400

    try:
        id_atleta     = int(data['id_atleta'])
        calidad       = int(data.get('calidad_sueno'))    if data.get('calidad_sueno') else None
        horas         = float(data.get('horas_sueno'))    if data.get('horas_sueno') else None
        fat           = int(data.get('fatiga'))           if data.get('fatiga') else None
        dolor         = int(data.get('dolor_muscular'))   if data.get('dolor_muscular') else None
        est           = int(data.get('estres'))           if data.get('estres') else None
        animo         = int(data.get('estado_animo'))     if data.get('estado_animo') else None
        comentarios   = data.get('comentarios')
    except ValueError:
        return jsonify({"error":"Formato numérico inválido"}), 400

    try:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO autoseguimiento
                      (id_atleta, calidad_sueno, horas_sueno, fatiga, dolor_muscular, estres, estado_animo, comentarios)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s);
                """, (
                    id_atleta, calidad, horas,
                    fat, dolor, est, animo, comentarios
                ))
            conn.commit()
        return jsonify({"mensaje":"Autoseguimiento registrado"}), 200
    except Exception as e:
        logging.exception("Error en /add_autoseguimiento")
        return jsonify({"error":"Error interno"}), 500

# ——— Consentimiento de tutores (GET y POST en una sola ruta) ———
@app.route('/consentimiento_tutor', methods=['GET', 'POST'])
def consentimiento_tutor():
    if request.method == 'GET':
        return app.send_static_file('legal/consentimiento_tutor.html')

    data = request.get_json() or {}
    for campo in ('nombre_menor', 'edad_menor', 'nombre_tutor', 'contacto_tutor'):
        if campo not in data:
            return jsonify({"error": f"{campo} es obligatorio"}), 400

    try:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO Consentimientos_Tutores
                    (nombre_menor, edad_menor, nombre_tutor, relacion_tutor, contacto_tutor, aceptado)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (
                    data['nombre_menor'],
                    int(data['edad_menor']),
                    data['nombre_tutor'],
                    data.get('relacion_tutor', None),
                    data['contacto_tutor'],
                    True
                ))
            conn.commit()
        return jsonify({"mensaje": "Consentimiento de tutor registrado correctamente"}), 200
    except Exception as e:
        logging.exception("Error en /consentimiento_tutor")
        return jsonify({"error": "Error interno"}), 500


# ——— HRV ———
@app.route('/add_hrv', methods=['POST'])
def add_hrv():
    data = request.json

    try:
        atleta_id = data.get("ID_Atleta")
        fecha = data.get("Fecha")
        hrv = data.get("HRV")

        if not all([atleta_id, fecha, hrv]):
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO hrv (id_atleta, fecha, hrv)
            VALUES (%s, %s, %s)
        """, (atleta_id, fecha, hrv))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "HRV agregado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ——— Arranque ———
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
