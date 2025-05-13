from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)  # Permitir CORS

# URL de conexión a PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')

# Función para conectar con la base de datos
def get_db():
    if not DATABASE_URL:
        raise Exception("La URL de la base de datos no está configurada.")
    return psycopg2.connect(DATABASE_URL)

# Crear tablas si no existen
def init_db():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS psicologia (
                    id SERIAL PRIMARY KEY,
                    atleta_id TEXT,
                    estado_emocional TEXT,
                    motivacion TEXT,
                    estres TEXT
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nutricion (
                    id SERIAL PRIMARY KEY,
                    atleta_id TEXT,
                    fecha TEXT,
                    peso REAL,
                    altura REAL,
                    imc REAL,
                    observaciones TEXT
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medico (
                    id SERIAL PRIMARY KEY,
                    atleta_id TEXT,
                    fecha TEXT,
                    temperatura REAL,
                    presion_arterial TEXT,
                    observaciones TEXT
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evaluacion_psicologica (
                    id SERIAL PRIMARY KEY,
                    atleta_id TEXT,
                    estado_emocional TEXT,
                    motivacion TEXT,
                    estres TEXT
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entrenamiento (
                    id SERIAL PRIMARY KEY,
                    atleta_id TEXT,
                    tipo_entrenamiento TEXT,
                    duracion INTEGER,
                    intensidad TEXT,
                    observaciones TEXT
                );
            ''')
            conn.commit()

# Inicializar base de datos
init_db()

# ------------------ RUTAS ------------------

@app.route('/psicologia', methods=['POST'])
def psicologia():
    data = request.get_json()
    required = ['atleta_id', 'estado_emocional', 'motivacion', 'estres']
    if not all(data.get(k) for k in required):
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO psicologia (atleta_id, estado_emocional, motivacion, estres)
                VALUES (%s, %s, %s, %s);
            ''', (data['atleta_id'], data['estado_emocional'], data['motivacion'], data['estres']))
            conn.commit()

    return jsonify({"mensaje": "Datos de psicología guardados correctamente"}), 200


@app.route('/nutricion', methods=['POST'])
def nutricion():
    data = request.get_json()
    required = ['atleta_id', 'fecha', 'peso', 'altura', 'imc', 'observaciones']
    if not all(data.get(k) for k in required):
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO nutricion (atleta_id, fecha, peso, altura, imc, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s);
            ''', (data['atleta_id'], data['fecha'], data['peso'], data['altura'], data['imc'], data['observaciones']))
            conn.commit()

    return jsonify({"mensaje": "Datos de nutrición guardados correctamente"}), 200


@app.route('/medico', methods=['POST'])
def medico():
    data = request.get_json()
    required = ['atleta_id', 'fecha', 'temperatura', 'presion_arterial', 'observaciones']
    if not all(data.get(k) for k in required):
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO medico (atleta_id, fecha, temperatura, presion_arterial, observaciones)
                VALUES (%s, %s, %s, %s, %s);
            ''', (data['atleta_id'], data['fecha'], data['temperatura'], data['presion_arterial'], data['observaciones']))
            conn.commit()

    return jsonify({"mensaje": "Datos médicos guardados correctamente"}), 200


@app.route('/evaluacion-psicologica', methods=['POST'])
def evaluacion_psicologica():
    data = request.get_json()
    required = ['atleta_id', 'estado_emocional', 'motivacion', 'estres']
    if not all(data.get(k) for k in required):
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO evaluacion_psicologica (atleta_id, estado_emocional, motivacion, estres)
                VALUES (%s, %s, %s, %s);
            ''', (data['atleta_id'], data['estado_emocional'], data['motivacion'], data['estres']))
            conn.commit()

    return jsonify({"mensaje": "Evaluación psicológica guardada correctamente"}), 200


@app.route('/entrenamiento', methods=['POST'])
def entrenamiento():
    data = request.get_json()
    required = ['atleta_id', 'tipo_entrenamiento', 'duracion', 'intensidad', 'observaciones']
    if not all(data.get(k) for k in required):
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO entrenamiento (atleta_id, tipo_entrenamiento, duracion, intensidad, observaciones)
                VALUES (%s, %s, %s, %s, %s);
            ''', (data['atleta_id'], data['tipo_entrenamiento'], data['duracion'], data['intensidad'], data['observaciones']))
            conn.commit()

    return jsonify({"mensaje": "Entrenamiento guardado correctamente"}), 200

# ------------------ MAIN ------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
