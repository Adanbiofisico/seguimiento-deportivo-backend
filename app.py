from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime


app = Flask(__name__)
CORS(app)

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
                    diagnostico TEXT,
                    tratamiento TEXT,
                    observaciones TEXT
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evento (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT,
                    fecha TEXT,
                    lugar TEXT,
                    descripcion TEXT
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
    if not data or not all(data.get(k) for k in required):
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
def guardar_nutricion():
    data = request.get_json()
    print("Datos recibidos:", data)
    
    try:
        id_atleta = int(data['id_atleta'])
        fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        tipo_de_consulta = data.get('tipo_de_consulta')
        recomendaciones = data.get('recomendaciones')
        notas = data.get('notas')
        macronutrientes = data.get('macronutrientes')
        hidratacion = int(data.get('hidratacion')) if data.get('hidratacion') else None
        frecuencia_comidas = int(data.get('frecuencia_comidas')) if data.get('frecuencia_comidas') else None

        conn = conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO nutricion (
                id_atleta, fecha, tipo_de_consulta, recomendaciones, notas,
                macronutrientes, hidratacion, frecuencia_comidas
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_atleta, fecha) DO UPDATE SET
                tipo_de_consulta = EXCLUDED.tipo_de_consulta,
                recomendaciones = EXCLUDED.recomendaciones,
                notas = EXCLUDED.notas,
                macronutrientes = EXCLUDED.macronutrientes,
                hidratacion = EXCLUDED.hidratacion,
                frecuencia_comidas = EXCLUDED.frecuencia_comidas;
        """, (
            id_atleta, fecha, tipo_de_consulta, recomendaciones, notas,
            macronutrientes, hidratacion, frecuencia_comidas
        ))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Datos de nutrición guardados correctamente"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 400

@app.route('/medico', methods=['POST'])
@app.route('/seguimiento-medico', methods=['POST'])
def seguimiento_medico():
    data = request.get_json()
    print("DATA RECIBIDA:", data)  # 👈 Añade esto

    required = ['atleta_id', 'fecha', 'diagnostico', 'tratamiento', 'observaciones']
    if not data or not all(data.get(k) for k in required):
        print("FALTAN CAMPOS:")
        for k in required:
            print(f"{k} -> {data.get(k)}")
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO medico (atleta_id, fecha, diagnostico, tratamiento, observaciones)
                VALUES (%s, %s, %s, %s, %s);
            ''', (data['atleta_id'], data['fecha'], data['diagnostico'], data['tratamiento'], data['observaciones']))
            conn.commit()

    return jsonify({"mensaje": "Datos médicos guardados correctamente"}), 200


@app.route('/entrenamiento', methods=['POST'])
def entrenamiento():
    data = request.get_json()
    required = ['atleta_id', 'tipo_entrenamiento', 'duracion', 'intensidad', 'observaciones']
    if not data or not all(data.get(k) for k in required):
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO entrenamiento (atleta_id, tipo_entrenamiento, duracion, intensidad, observaciones)
                VALUES (%s, %s, %s, %s, %s);
            ''', (data['atleta_id'], data['tipo_entrenamiento'], data['duracion'], data['intensidad'], data['observaciones']))
            conn.commit()

    return jsonify({"mensaje": "Entrenamiento guardado correctamente"}), 200


@app.route('/evaluaciones', methods=['GET'])
def obtener_todas_evaluaciones():
    resultado = {}
    with get_db() as conn:
        with conn.cursor() as cursor:
            for tabla in ['psicologia', 'nutricion', 'medico', 'entrenamiento']:
                cursor.execute(f'SELECT * FROM {tabla}')
                rows = cursor.fetchall()
                columnas = [desc[0] for desc in cursor.description]
                resultado[tabla] = [dict(zip(columnas, row)) for row in rows]
    return jsonify(resultado)


@app.route('/add_evento', methods=['POST'])
def agregar_evento():
    data = request.get_json()
    required = ['nombre', 'fecha', 'lugar', 'descripcion']
    if not data or not all(data.get(k) for k in required):
        return jsonify({"error": "Todos los campos del evento son requeridos"}), 400

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO evento (nombre, fecha, lugar, descripcion)
                VALUES (%s, %s, %s, %s);
            ''', (data['nombre'], data['fecha'], data['lugar'], data['descripcion']))
            conn.commit()

    return jsonify({"mensaje": "Evento agregado correctamente"}), 200



@app.route('/', methods=['GET'])
def home():
    return jsonify({"estado": "API corriendo"}), 200


# ------------------ MAIN ------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
