from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)  # Permite el acceso desde cualquier origen

# Conexión a la base de datos PostgreSQL usando la variable de entorno DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL')

# Función para obtener la conexión a la base de datos PostgreSQL
def get_db():
    if DATABASE_URL is None:
        raise Exception("La URL de la base de datos no está configurada correctamente.")
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Crear la tabla si no existe
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

# Inicializar la base de datos al inicio de la aplicación
init_db()

# Ruta para guardar los datos de Psicología
@app.route('/psicologia', methods=['POST'])
def psicologia():
    data = request.get_json()  # Obtener datos en formato JSON
    atleta_id = data.get('atleta_id')
    estado_emocional = data.get('estado_emocional')
    motivacion = data.get('motivacion')
    estres = data.get('estres')

    if not atleta_id or not estado_emocional or not motivacion or not estres:
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    # Guardar los datos en la base de datos
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO psicologia (atleta_id, estado_emocional, motivacion, estres)
                VALUES (%s, %s, %s, %s);
            ''', (atleta_id, estado_emocional, motivacion, estres))
            conn.commit()

    return jsonify({"mensaje": "Datos de psicología guardados correctamente"}), 200

# Ruta para guardar los datos de Nutrición
@app.route('/nutricion', methods=['POST'])
def nutricion():
    data = request.get_json()
    atleta_id = data.get('atleta_id')
    fecha = data.get('fecha')
    peso = data.get('peso')
    altura = data.get('altura')
    imc = data.get('imc')
    observaciones = data.get('observaciones')

    if not atleta_id or not fecha or not peso or not altura or not imc or not observaciones:
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    # Guardar los datos en la base de datos
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO nutricion (atleta_id, fecha, peso, altura, imc, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s);
            ''', (atleta_id, fecha, peso, altura, imc, observaciones))
            conn.commit()

    return jsonify({"mensaje": "Datos de nutrición guardados correctamente"}), 200

# Ruta para guardar los datos Médicos
@app.route('/medico', methods=['POST'])
def medico():
    data = request.get_json()
    atleta_id = data.get('atleta_id')
    fecha = data.get('fecha')
    temperatura = data.get('temperatura')
    presion_arterial = data.get('presion_arterial')
    observaciones = data.get('observaciones')

    if not atleta_id or not fecha or not temperatura or not presion_arterial or not observaciones:
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    # Guardar los datos en la base de datos
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO medico (atleta_id, fecha, temperatura, presion_arterial, observaciones)
                VALUES (%s, %s, %s, %s, %s);
            ''', (atleta_id, fecha, temperatura, presion_arterial, observaciones))
            conn.commit()

    return jsonify({"mensaje": "Datos médicos guardados correctamente"}), 200

# Ruta para guardar los datos de Evaluación Psicológica
@app.route('/evaluacion-psicologica', methods=['POST'])
def evaluacion_psicologica():
    data = request.get_json()
    atleta_id = data.get('atleta_id')
    estado_emocional = data.get('estado_emocional')
    motivacion = data.get('motivacion')
    estres = data.get('estres')

    if not atleta_id or not estado_emocional or not motivacion or not estres:
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    # Guardar los datos en la base de datos
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO evaluacion_psicologica (atleta_id, estado_emocional, motivacion, estres)
                VALUES (%s, %s, %s, %s);
            ''', (atleta_id, estado_emocional, motivacion, estres))
            conn.commit()

    return jsonify({"mensaje": "Evaluación psicológica guardada correctamente"}), 200

# Configura el puerto y corre la app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
