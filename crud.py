import csv
import os
import random

FILE_NAME = 'data_wp.csv'
HEADERS = ['ID_WP', 'Tahun', 'Sektor', 'Jml_Terlambat', 'Rata_Pembayaran', 'Frekuensi_Lapor', 'Jml_Tunggakan', 'Kepatuhan']

def init_csv():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(HEADERS)
        _generate_dummy_data()

def _generate_dummy_data():
    sektor_list = ['Perdagangan', 'Jasa', 'Manufaktur', 'Properti']
    for i in range(1, 201):
        sektor = random.choice(sektor_list)
        tahun = random.choice([2024, 2025])
        
        # 75% Patuh (0), 25% Risiko Tinggi (1)
        kepatuhan = random.choices([0, 1], weights=[75, 25])[0]
        
        if kepatuhan == 0:
            jml_terlambat = random.randint(0, 1)
            jml_tunggakan = 0
            rata_pembayaran = random.randint(15000000, 100000000)
            frekuensi_lapor = random.randint(10, 12)
        else:
            jml_terlambat = random.randint(3, 8)
            jml_tunggakan = random.randint(1, 4)
            rata_pembayaran = random.randint(1000000, 20000000)
            frekuensi_lapor = random.randint(1, 7)
            
        add_data({
            'ID_WP': f'WP{i:03d}', 'Tahun': tahun, 'Sektor': sektor, 
            'Jml_Terlambat': jml_terlambat, 'Rata_Pembayaran': rata_pembayaran, 
            'Frekuensi_Lapor': frekuensi_lapor, 'Jml_Tunggakan': jml_tunggakan, 
            'Kepatuhan': kepatuhan
        })

def read_data(tahun_filter=None, sektor_filter=None):
    data = []
    if not os.path.exists(FILE_NAME): return data
    with open(FILE_NAME, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if tahun_filter and str(row['Tahun']) != str(tahun_filter): continue
            if sektor_filter and row['Sektor'] != sektor_filter: continue
            data.append(row)
    return data

def add_data(row_dict):
    with open(FILE_NAME, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writerow(row_dict)

def update_data(id_wp, new_data):
    data = read_data()
    with open(FILE_NAME, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()
        for row in data:
            if row['ID_WP'] == id_wp:
                row.update(new_data)
            writer.writerow(row)

def delete_data(id_wp):
    data = read_data()
    with open(FILE_NAME, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()
        for row in data:
            if row['ID_WP'] != id_wp:
                writer.writerow(row)

def import_csv_file(filepath):
    with open(filepath, mode='r') as file:
        reader = csv.DictReader(file)
        with open(FILE_NAME, mode='a', newline='') as out_file:
            writer = csv.DictWriter(out_file, fieldnames=HEADERS)
            for row in reader:
                writer.writerow(row)

def read_data(tahun_filter=None, sektor_filter=None, kepatuhan_filter=None):
    data = []
    if not os.path.exists(FILE_NAME): return data
    with open(FILE_NAME, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if tahun_filter and str(row['Tahun']) != str(tahun_filter): continue
            if sektor_filter and row['Sektor'] != sektor_filter: continue
            if kepatuhan_filter and str(row['Kepatuhan']) != str(kepatuhan_filter): continue
            data.append(row)
    return data