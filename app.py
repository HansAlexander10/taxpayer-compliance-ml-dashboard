from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flaskwebgui import FlaskUI  # <-- TAMBAHKAN INI
import pandas as pd
import joblib
import os
import crud

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
crud.init_csv()

@app.route('/')
def dashboard():
    tahun_filter = request.args.get('tahun')
    sektor_filter = request.args.get('sektor')
    kepatuhan_filter = request.args.get('kepatuhan')
    
    # 1. Ambil SEMUA data (tanpa filter) untuk mencari tahun apa saja yang tersedia
    all_data_unfiltered = crud.read_data()
    
    # Ekstrak tahun unik, hilangkan duplikat pakai set(), lalu urutkan
    available_years = sorted(list(set([str(wp['Tahun']) for wp in all_data_unfiltered if 'Tahun' in wp])))
    
    # 2. Ambil data yang sudah DIFILTER untuk ditampilkan di tabel dan statistik
    data_filtered = crud.read_data(tahun_filter, sektor_filter, kepatuhan_filter)
    df = pd.DataFrame(data_filtered)
    
    stats = {"total": 0, "patuh_pct": 0, "risiko_pct": 0}
    if not df.empty and 'Kepatuhan' in df.columns:
        df['Kepatuhan'] = pd.to_numeric(df['Kepatuhan'])
        total_wp = len(df)
        tidak_patuh = df['Kepatuhan'].sum()
        patuh = total_wp - tidak_patuh
        stats = {
            "total": total_wp,
            "patuh_pct": round((patuh / total_wp) * 100, 1),
            "risiko_pct": round((tidak_patuh / total_wp) * 100, 1)
        }

    fi_labels, fi_data = [], []
    if os.path.exists('feature_importance.csv'):
        fi_df = pd.read_csv('feature_importance.csv').head(5)
        fi_labels, fi_data = fi_df['Feature'].tolist(), fi_df['Importance'].tolist()

    # Prioritas Penanganan: ambil yang Risiko Tinggi (1) dari data yang difilter
    wp_bermasalah = [wp for wp in data_filtered if str(wp.get('Kepatuhan', 0)) == '1']
    wp_bermasalah_sorted = sorted(
        wp_bermasalah, 
        key=lambda x: (int(x.get('Jml_Tunggakan', 0)), int(x.get('Jml_Terlambat', 0))), 
        reverse=True
    )

    return render_template(
        'index.html', stats=stats, fi_labels=fi_labels, fi_data=fi_data, 
        all_data=data_filtered, wp_bermasalah=wp_bermasalah_sorted,
        current_tahun=tahun_filter, current_sektor=sektor_filter, current_kepatuhan=kepatuhan_filter,
        available_years=available_years # <-- Kirim daftar tahun dinamis ke HTML
    )

@app.route('/add', methods=['POST'])
def add():
    crud.add_data(request.form.to_dict())
    return redirect(url_for('dashboard'))

@app.route('/edit/<id_wp>', methods=['POST'])
def edit(id_wp):
    crud.update_data(id_wp, request.form.to_dict())
    return redirect(url_for('dashboard'))

@app.route('/delete/<id_wp>')
def delete(id_wp):
    crud.delete_data(id_wp)
    return redirect(url_for('dashboard'))

@app.route('/export')
def export_csv():
    return send_file('data_wp.csv', as_attachment=True, download_name='Dataset_Wajib_Pajak.csv')

@app.route('/import', methods=['POST'])
def import_csv():
    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        crud.import_csv_file(filepath)
        os.remove(filepath)
    return redirect(url_for('dashboard'))

@app.route('/predict', methods=['POST'])
def predict():
    try:
        model = joblib.load('model_kepatuhan.pkl')
        model_columns = joblib.load('model_columns.pkl')
        
        input_data = {
            'Jml_Terlambat': float(request.form['terlambat']), 'Rata_Pembayaran': float(request.form['pembayaran']),
            'Frekuensi_Lapor': float(request.form['lapor']), 'Jml_Tunggakan': float(request.form['tunggakan']),
            'Sektor': request.form['sektor']
        }
        
        df_input = pd.DataFrame([input_data])
        df_input = pd.get_dummies(df_input, columns=['Sektor'])
        df_input = df_input.reindex(columns=model_columns, fill_value=0)
        
        pred = model.predict(df_input)[0]
        prob = model.predict_proba(df_input)[0][1]
        
        risiko = "Tinggi (Tidak Patuh)" if pred == 1 else "Rendah (Patuh)"
        warna = "danger" if pred == 1 else "success"
        
        return jsonify({"status": "success", "risiko": risiko, "warna": warna, "probabilitas": f"{prob*100:.1f}%"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    # Hapus app.run() yang lama, ganti dengan ini:
    FlaskUI(app=app, server="flask", port=5000, width=1200, height=800).run()