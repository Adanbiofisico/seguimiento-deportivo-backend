from flask import Blueprint, request, jsonify
import pandas as pd
from prophet import Prophet
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import xgboost as xgb
import numpy as np

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        df = pd.DataFrame(data['training_data'])

        # 1️⃣ Tendencia (Prophet)
        trend_df = df[['fecha', 'carga']].rename(columns={'fecha': 'ds', 'carga': 'y'})
        model = Prophet()
        model.fit(trend_df)
        future = model.make_future_dataframe(periods=7)
        forecast = model.predict(future)

        # 2️⃣ Fatiga (Random Forest)
        X = df[['carga', 'hrv', 'suenio_horas']]
        y = df['fatiga']
        rf = RandomForestClassifier(n_estimators=50, random_state=42)
        rf.fit(X, y)
        last_input = np.array([[df['carga'].iloc[-1], df['hrv'].iloc[-1], df['suenio_horas'].iloc[-1]]])
        fatiga_pred = int(rf.predict(last_input)[0])

        # 3️⃣ Lesión (XGBoost)
        if 'lesion' in df.columns and df['lesion'].nunique() > 1:
            Xl = df[['carga', 'hrv', 'suenio_horas', 'fatiga']]
            yl = df['lesion']
            X_train, X_test, y_train, y_test = train_test_split(Xl, yl, test_size=0.2, random_state=42)
            xgb_model = xgb.XGBClassifier(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=4,
                random_state=42,
                use_label_encoder=False,
                eval_metric="logloss"
            )
            xgb_model.fit(X_train, y_train)
            lesion_pred = int(xgb_model.predict(last_input)[0])
            lesion_acc = accuracy_score(y_test, xgb_model.predict(X_test))
        else:
            lesion_pred = 0
            lesion_acc = None

        return jsonify({
            "tendencia": forecast[['ds', 'yhat']].tail(7).to_dict(orient="records"),
            "riesgo_fatiga": fatiga_pred,
            "riesgo_lesion": lesion_pred,
            "exactitud_xgb": lesion_acc
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
