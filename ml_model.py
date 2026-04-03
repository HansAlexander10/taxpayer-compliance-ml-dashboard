import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import crud

def train_and_save_model():
    crud.init_csv()
    data = crud.read_data()
    df = pd.DataFrame(data)

    numeric_cols = ['Jml_Terlambat', 'Rata_Pembayaran', 'Frekuensi_Lapor', 'Jml_Tunggakan', 'Kepatuhan']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)

    X = df[['Jml_Terlambat', 'Rata_Pembayaran', 'Frekuensi_Lapor', 'Jml_Tunggakan', 'Sektor']]
    X = pd.get_dummies(X, columns=['Sektor'], drop_first=True)
    y = df['Kepatuhan']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000),
        'Random Forest': RandomForestClassifier(random_state=42),
        'XGBoost': XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    }

    best_model = None
    best_f1 = -1

    print("=== Hasil Evaluasi Model ===")
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        print(f"{name} -> Acc: {acc:.2f} | F1: {f1:.2f}")
        
        if f1 > best_f1:
            best_f1 = f1
            best_model = model

    joblib.dump(best_model, 'model_kepatuhan.pkl')
    joblib.dump(list(X.columns), 'model_columns.pkl')

    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        fi_df = pd.DataFrame({'Feature': X.columns, 'Importance': importances})
        fi_df.to_csv('feature_importance.csv', index=False)
        print("Model dan Feature importance berhasil disimpan.")

if __name__ == '__main__':
    train_and_save_model()