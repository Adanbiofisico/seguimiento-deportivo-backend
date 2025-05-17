from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Conexión a PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db():
    if not DATABASE_URL:
        raise Exception("La URL de la base de datos no está configurada.")
    return psycopg2.connect(DATABASE_URL)

# Crear tablas (¡Todas tus tablas originales + las nuevas!)
def init_db():
    with get_db() as conn:
        with conn.cursor() as cursor:
            # --- Tablas originales (se mantienen igual) ---
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
            # --- Tabla entrenamiento MEJORADA (con RPE y carga) ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entrenamiento (
                    id SERIAL PRIMARY KEY,
                    atleta_id TEXT NOT NULL,
                    tipo_entrenamiento TEXT NOT NULL,
                    duracion INTEGER NOT NULL,
                    intensidad TEXT,
                    rpe INTEGER CHECK (rpe >= 1 AND rpe <= 10),
                    carga_entrenamiento INTEGER,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observaciones TEXT
                );
            ''')
            # --- Nueva tabla para fatiga ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fatiga_atleta (
                    id SERIAL PRIMARY KEY,
                    atleta_id TEXT NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    nivel_fatiga INTEGER,
                    riesgo_lesion BOOLEAN,
                    recomendaciones TEXT
                );
            ''')
            conn.commit()

init_db()

# -------------------- RUTAS ORIGINALES (SE MANTIENEN IGUAL) --------------------
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

@app.route('/seguimiento-medico', methods=['POST'])
def seguimiento_medico():
    data = request.get_json()
    required = ['atleta_id', 'consulta_fecha', 'diagnostico', 'tratamiento', 'observaciones']
    if not all(data.get(k) for k in required):
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO medico (atleta_id, fecha, temperatura, presion_arterial, observaciones)
                VALUES (%s, %s, %s, %s, %s);
            ''', (data['atleta_id'], data['consulta_fecha'], data.get('temperatura'), data.get('presion_arterial'), data['observaciones']))
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

# -------------------- RUTAS NUEVAS O MEJORADAS --------------------
@app.route('/entrenamiento', methods=['POST'])
def entrenamiento():
    data = request.get_json()
    required = ['atleta_id', 'tipo_entrenamiento', 'duracion']
    if not all(data.get(k) for k in required):
        return jsonify({"error": "Campos requeridos: atleta_id, tipo_entrenamiento, duracion"}), 400

    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO entrenamiento 
                    (atleta_id, tipo_entrenamiento, duracion, intensidad, observaciones)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                ''', (
                    data['atleta_id'],
                    data['tipo_entrenamiento'],
                    int(data['duracion']),
                    data.get('intensidad'),
                    data.get('observaciones')
                ))
                entrenamiento_id = cursor.fetchone()[0]
                conn.commit()

        return jsonify({
            "mensaje": "Entrenamiento base guardado. Proceda a registrar RPE.",
            "id": entrenamiento_id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/entrenamiento/rpe', methods=['POST'])
def registrar_rpe():
    data = request.get_json()
    required = ['entrenamiento_id', 'rpe']
    if not all(data.get(k) for k in required):
        return jsonify({"error": "Se requieren entrenamiento_id y rpe"}), 400

    try:
        rpe = int(data['rpe'])
        if rpe < 1 or rpe > 10:
            raise ValueError("RPE debe estar entre 1 y 10")

        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT duracion FROM entrenamiento WHERE id = %s;
                ''', (data['entrenamiento_id'],))
                result = cursor.fetchone()
                if not result:
                    return jsonify({"error": "Entrenamiento no encontrado"}), 404
                
                duracion = result[0]
                carga = duracion * rpe

                cursor.execute('''
                    UPDATE entrenamiento 
                    SET rpe = %s, carga_entrenamiento = %s
                    WHERE id = %s
                    RETURNING *;
                ''', (rpe, carga, data['entrenamiento_id']))
                entrenamiento_actualizado = cursor.fetchone()
                conn.commit()

                evaluar_fatiga(data.get('atleta_id'), carga)

        return jsonify({
            "mensaje": "RPE registrado exitosamente",
            "carga_entrenamiento": carga,
            "data": dict(zip(
                ['id', 'atleta_id', 'tipo_entrenamiento', 'duracion', 'intensidad', 'rpe', 'carga_entrenamiento', 'fecha', 'observaciones'],
                entrenamiento_actualizado
            ))
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def evaluar_fatiga(atleta_id, carga):
    if not atleta_id:
        return
    riesgo_lesion = carga > 500  # Umbral ajustable
    recomendacion = "Descanso activo" if riesgo_lesion else "Continuar plan normal"
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO fatiga_atleta 
                (atleta_id, nivel_fatiga, riesgo_lesion, recomendaciones)
                VALUES (%s, %s, %s, %s);
            ''', (
                atleta_id,
                carga // 100,
                riesgo_lesion,
                recomendacion
            ))
            conn.commit()

# -------------------- RUTAS ORIGINALES DE CONSULTA --------------------
@app.route('/evaluaciones', methods=['GET'])
def obtener_todas_evaluaciones():
    resultado = {}
    with get_db() as conn:
        with conn.cursor() as cursor:
            for tabla in ['evaluacion_psicologica', 'nutricion', 'medico', 'entrenamiento']:
                cursor.execute(f'SELECT * FROM {tabla}')
                rows = cursor.fetchall()
                columnas = [desc[0] for desc in cursor.description]
                resultado[tabla] = [dict(zip(columnas, row)) for row in rows]
    return jsonify(resultado)

@app.route('/add_evento', methods=['POST'])
def agregar_evento():
    data = request.get_json()
    evento = data.get('evento')
    return jsonify({"mensaje": "Evento agregado correctamente"})

# -------------------- NUEVAS RUTAS DE CONSULTA --------------------
@app.route('/atleta/<atleta_id>/carga-entrenamiento', methods=['GET'])
def obtener_carga_atleta(atleta_id):
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT fecha, carga_entrenamiento 
                    FROM entrenamiento 
                    WHERE atleta_id = %s 
                    AND carga_entrenamiento IS NOT NULL
                    ORDER BY fecha DESC
                    LIMIT 7;
                ''', (atleta_id,))
                datos = cursor.fetchall()
                resultados = [{"fecha": str(fecha), "carga": carga} for fecha, carga in datos]
        return jsonify(resultados), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/atleta/<atleta_id>/fatiga', methods=['GET'])
def obtener_estado_fatiga(atleta_id):
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT fecha, nivel_fatiga, riesgo_lesion, recomendaciones
                    FROM fatiga_atleta
                    WHERE atleta_id = %s
                    ORDER BY fecha DESC
                    LIMIT 1;
                ''', (atleta_id,))
                resultado = cursor.fetchone()
        if not resultado:
            return jsonify({"mensaje": "No hay datos de fatiga"}), 404
        return jsonify({
            "fecha": str(resultado[0]),
            "nivel_fatiga": resultado[1],
            "riesgo_lesion": resultado[2],
            "recomendaciones": resultado[3]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Añade este print para verificar en logs
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False en producción
