import pickle
import sqlite3

import pandas as pd
from flask import Flask, jsonify, request
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

DB_PATH = 'advertising.db'
MODEL_PATH = 'advertising.model'

# Cargamos el modelo al arrancar la app
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)


# ---------------------------------------------------------------------------
# 1. PREDICCIÓN
# ---------------------------------------------------------------------------
@app.route('/predict', methods=['POST'])
def predict():
    """
    Predice las ventas a partir de los gastos en publicidad.

    Body JSON:
        {"TV": 230.1, "radio": 37.8, "newspaper": 69.2}

    Respuesta:
        {"prediction": 22415.3}
    """
    body = request.get_json()

    required_fields = ['TV', 'radio', 'newspaper']
    missing = [field for field in required_fields if field not in body]
    if missing:
        return jsonify({'error': 'Faltan los campos: {}'.format(missing)}), 400

    data = pd.DataFrame([{'TV': body['TV'], 'radio': body['radio'], 'newspaper': body['newspaper']}])

    prediction = model.predict(data)[0]
    return jsonify({'prediction': round(float(prediction), 2)})


# ---------------------------------------------------------------------------
# 2. INGESTIÓN — añadir nuevos registros a la BD
# ---------------------------------------------------------------------------
@app.route('/ingest', methods=['POST'])
def ingest():
    """
    Añade un nuevo registro a la base de datos con los valores REALES de ventas.

    Body JSON:
        {"TV": 180.8, "radio": 10.8, "newspaper": 58.4, "sales": 12900.0}

    Respuesta:
        {"message": "Registro añadido correctamente"}
    """
    body = request.get_json()

    required_fields = ['TV', 'radio', 'newspaper', 'sales']
    missing = [field for field in required_fields if field not in body]
    if missing:
        return jsonify({'error': 'Faltan los campos: {}'.format(missing)}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO t (TV, radio, newspaper, sales) VALUES (?, ?, ?, ?)",
        (body['TV'], body['radio'], body['newspaper'], body['sales'])
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Registro añadido correctamente'}), 201


# ---------------------------------------------------------------------------
# 3. REENTRENAMIENTO
# ---------------------------------------------------------------------------
@app.route('/retrain', methods=['POST'])
def retrain():
    """
    Reentrena el modelo con todos los datos de la BD,
    guarda el modelo en disco y lo recarga en memoria.

    No requiere body.

    Respuesta:
        {"message": "Modelo reentrenado correctamente", "n_samples": 205}
    """
    global model

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM t", conn)
    conn.close()

    if df.empty:
        return jsonify({'error': 'No hay datos en la BD para reentrenar el modelo'}), 400

    X = df[['TV', 'radio', 'newspaper']]
    y = df['sales']

    new_model = LinearRegression()
    new_model.fit(X, y)

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(new_model, f)

    model = new_model

    return jsonify({'message': 'Modelo reentrenado correctamente', 'n_samples': len(df)})


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
