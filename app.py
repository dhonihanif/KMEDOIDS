# from crypt import methods
from flask import Flask, render_template
import matplotlib.pyplot as plt
import pandas as pd
#%matplotlib inline
import numpy as np
import os
import array
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.cluster import KMeans
from sklearn_extra.cluster import KMedoids
from sklearn.preprocessing import OneHotEncoder
from flask import Flask, render_template, request, url_for, redirect, jsonify
#from flask_mysqldb import MySQL
from sqlalchemy import null

app = Flask(__name__)

#######################################################
#loading excel file ke dalam 1 variabel 'df'
df = pd.read_excel ("./data/default.xlsx", sheet_name='UKM Kerajinan')
df_cleaning = df
data = df_cleaning.iloc[:,[7,18,27,29,30,31,32,33,34,35,36,37]]
data.columns = ['pendidikan','tanggal_pendirian_usaha','kegiatan_usaha', 'tujuan_pemasaran', 'kepemilikan_tanah', 'sarana_media_elektronik', 'modal_bantuan_pemerintah', 'pinjaman', 'omset_pertahun', 'asuransi', 'tenaga_kerja_laki', 'tenaga_kerja_perempuan']
data_cluster = data
data = data.dropna()

df_transformasi = df_cleaning
df_transformed = df_cleaning
#######################################################



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/hasilupload',methods=['GET', 'POST'])
def hasilupload():
    global df
    global data

    if request.method == 'POST':
        load = request.files['file']
        load.save(os.path.join('data','Data UKM Pendataan Verifikasi Periode II 2021-2022_Dinas PKU.xlsx'))
        df = pd.read_excel ("./data/Data UKM Pendataan Verifikasi Periode II 2021-2022_Dinas PKU.xlsx", sheet_name='UKM Kerajinan')

    return render_template('hasilupload.html', raw = [df.to_html(classes="table table-bordered hover", table_id="clean")])

@app.route('/cleaning',methods=['GET', 'POST'])
def cleaning():
    global df
    global df_cleaning
    global data_cluster

    if request.method == 'POST':
        load = request.files['file']
        load.save(os.path.join('data','Data UKM Pendataan Verifikasi Periode II 2021-2022_Dinas PKU.xlsx'))
        
        # PREPROCESSING DATA 
        # CLEANING DATA
        df = pd.read_excel(r'data\Data UKM Pendataan Verifikasi Periode II 2021-2022_Dinas PKU.xlsx', sheet_name='UKM Kerajinan')
        df_cleaning = df.copy()
        df_cleaning.dropna(inplace=True)
        
        # TAHAPAN SELEKSI DATA
        data_cluster = df_cleaning.iloc[:,[1,15,7,18,27,29,30,31,32,33,34,35,36,37]]
        data_cluster.columns = ['ref_oss','nama_usaha','pendidikan','tanggal_pendirian_usaha','kegiatan_usaha', 'tujuan_pemasaran', 'kepemilikan_tanah', 'sarana_media_elektronik', 'modal_bantuan_pemerintah', 'pinjaman', 'omset_pertahun', 'asuransi', 'tenaga_kerja_laki', 'tenaga_kerja_perempuan']
        
        data = df_cleaning.iloc[:,[7,18,27,29,30,31,32,33,34,35,36,37]]
        data.columns = ['pendidikan','tanggal_pendirian_usaha','kegiatan_usaha', 'tujuan_pemasaran', 'kepemilikan_tanah', 'sarana_media_elektronik', 'modal_bantuan_pemerintah', 'pinjaman', 'omset_pertahun', 'asuransi', 'tenaga_kerja_laki', 'tenaga_kerja_perempuan']
        print(data,df,df_cleaning,data_cluster)
    return render_template('cleaning.html',data_tabel=[data_cluster.to_html(classes="table table-bordered hover",table_id="cleannn")], raw = [df.to_html(classes="table table-bordered hover",table_id="clean")])

@app.route('/transformasi')
def transformasi():
    # DATA TRANSFORMASI
    global df_transformed

    df_transformasi = data
    le = LabelEncoder()
    ##Tranformasi kolom Pendidikan
    pendidikan_transformed = df_transformasi.pendidikan
    
    for i in range(len(pendidikan_transformed)):
        
        if pendidikan_transformed.iloc[i] == "-":
            pendidikan_transformed.iloc[i] = 0
        elif pendidikan_transformed.iloc[i] == "SD":
            pendidikan_transformed.iloc[i] = 1
        elif pendidikan_transformed.iloc[i] == "SMP" or pendidikan_transformed.iloc[i] == "SLTP/Sederajat":
            pendidikan_transformed.iloc[i] = 2
        elif pendidikan_transformed.iloc[i] == "SMA" or pendidikan_transformed.iloc[i] == "SLTA/SEDERAJAT" or pendidikan_transformed.iloc[i] == "SMK":
            pendidikan_transformed.iloc[i] = 3
        elif pendidikan_transformed.iloc[i] == "D1":
            pendidikan_transformed.iloc[i] = 4
        elif pendidikan_transformed.iloc[i] == "D2":
            pendidikan_transformed.iloc[i] = 5
        elif pendidikan_transformed.iloc[i] == "D3" or pendidikan_transformed.iloc[i] == "AKADEMI/DIPLOMA III/SARJANA MUDA":
            pendidikan_transformed.iloc[i] = 6
        elif pendidikan_transformed.iloc[i] == "D4" or pendidikan_transformed.iloc[i] == "DIPLOMA IV/STRATA I":
            pendidikan_transformed.iloc[i] = 7
        elif pendidikan_transformed.iloc[i] == "S1":
            pendidikan_transformed.iloc[i] = 8
        elif pendidikan_transformed.iloc[i] == "S2":
            pendidikan_transformed.iloc[i] = 9
        elif pendidikan_transformed.iloc[i] == "S3":
            pendidikan_transformed.iloc[i] = 10

    ##Penghitungan Umur Usaha   
    for index, row in df_transformasi.iterrows():
        df_transformasi.loc[index, 'umur_usaha'] = datetime.now().year - int ( row['tanggal_pendirian_usaha'][-4:])
    df_umur_usaha = df_transformasi['umur_usaha']

    ##Tranformasi kolom kegiatan usaha
    kegiatan_usaha_transformed = df_transformasi['kegiatan_usaha']
    for i in range(len(kegiatan_usaha_transformed)):
        if kegiatan_usaha_transformed.iloc[i] == "Produksi" or kegiatan_usaha_transformed.iloc[i] == "Penjualan":
            kegiatan_usaha_transformed.iloc[i] = 1
        else:
            kegiatan_usaha_transformed.iloc[i] = 2
            
    ##Tranformasi kolom tujuan pemasaran
    tujuan_pemasaran_transformed = df_transformasi['tujuan_pemasaran']
    for i in range(len(tujuan_pemasaran_transformed)):
        a = str(tujuan_pemasaran_transformed.iloc[i]).split(", ")
        tujuan_pemasaran_transformed.iloc[i] = len(a)
        
    #transformasi kolom kepemilikan tanah
    kepemilikan_tanah_transformed = df_transformasi['kepemilikan_tanah']
    le.fit(kepemilikan_tanah_transformed)
    for i in range(len(kepemilikan_tanah_transformed)):
        if kepemilikan_tanah_transformed.iloc[i] == "-":
            kepemilikan_tanah_transformed.iloc[i] = 0
        else:
            kepemilikan_tanah_transformed.iloc[i] = le.transform([kepemilikan_tanah_transformed.iloc[i]])[0]
    
    #transformasi kolom sarana media elektronik
    sarana_media_elektronik_transfromed = df_transformasi['sarana_media_elektronik']
    for i in range(len(sarana_media_elektronik_transfromed)):
        a = str(sarana_media_elektronik_transfromed.iloc[i]).split(", ")
        if a[0] == "-":
            sarana_media_elektronik_transfromed.iloc[i] = 0
        else:
            sarana_media_elektronik_transfromed.iloc[i] = len(a)

    #transformasi kolom modal bantuan pemerintah
    modal_bantuan_pemerintah_transformed = df_transformasi.modal_bantuan_pemerintah
    le.fit(modal_bantuan_pemerintah_transformed)
    for i in range(len(modal_bantuan_pemerintah_transformed)):
        if modal_bantuan_pemerintah_transformed.iloc[i] == "-":
            modal_bantuan_pemerintah_transformed.iloc[i] = 0
        else:
            modal_bantuan_pemerintah_transformed.iloc[i] = le.transform([modal_bantuan_pemerintah_transformed.iloc[i]])[0]    

    #transformasi kolom pinjaman
    pinjaman_transfromed = df_transformasi['pinjaman']
    le.fit(pinjaman_transfromed)
    for i in range(len(pinjaman_transfromed)):
        if pinjaman_transfromed.iloc[i] == "-":
            pinjaman_transfromed.iloc[i] = 0
        else:
            pinjaman_transfromed.iloc[i] = le.transform([pinjaman_transfromed.iloc[i]])[0]

    #transformasi kolom omset pertahun
    omset_pertahun_transformed = df_transformasi.omset_pertahun
    for i in range(len(omset_pertahun_transformed)):
        if omset_pertahun_transformed.iloc[i] == "Kurang dari 10 juta":
            omset_pertahun_transformed.iloc[i] = 1
        elif omset_pertahun_transformed.iloc[i] == "10 juta s/d 25 juta":
            omset_pertahun_transformed.iloc[i] = 2
        elif omset_pertahun_transformed.iloc[i] == "25 juta s/d 40 juta":
            omset_pertahun_transformed.iloc[i] = 3
        elif omset_pertahun_transformed.iloc[i] == "40 juta s/d 55 juta":
            omset_pertahun_transformed.iloc[i] = 4
        elif omset_pertahun_transformed.iloc[i] == "55 juta s/d 70 juta":
            omset_pertahun_transformed.iloc[i] = 5
        elif omset_pertahun_transformed.iloc[i] == "70 juta s/d 85 juta":
            omset_pertahun_transformed.iloc[i] = 6
        elif omset_pertahun_transformed.iloc[i] == "85 juta s/d 100 juta":
            omset_pertahun_transformed.iloc[i] = 7
        elif omset_pertahun_transformed.iloc[i] == "100 juta s/d 120 juta":
            omset_pertahun_transformed.iloc[i] = 8
        elif omset_pertahun_transformed.iloc[i] == "120 juta s/d 150 juta":
            omset_pertahun_transformed.iloc[i] = 9
        elif omset_pertahun_transformed.iloc[i] == "Lebih dari 150 juta":
            omset_pertahun_transformed.iloc[i] = 10
    #transformasi kolom asuransi
    asuransi_transformed = df_transformasi['asuransi']
    le.fit(asuransi_transformed)
    for i in range(len(asuransi_transformed)):
        if asuransi_transformed.iloc[i] == "-":
            asuransi_transformed.iloc[i] = 0
        else:
            asuransi_transformed.iloc[i] = le.transform([asuransi_transformed.iloc[i]])[0]

    #memasukkan kolom ke variabel untuk digabungkan
    df_tenagakerja_laki = df_transformasi['tenaga_kerja_laki']
    df_tenagakerja_perempuan = df_transformasi['tenaga_kerja_perempuan']

    #proses penyatuan hasil transformasi untuk di transformasi
    df_transform = pd.concat([pendidikan_transformed,df_umur_usaha,kegiatan_usaha_transformed,tujuan_pemasaran_transformed, kepemilikan_tanah_transformed,sarana_media_elektronik_transfromed,modal_bantuan_pemerintah_transformed,pinjaman_transfromed,omset_pertahun_transformed,asuransi_transformed,df_tenagakerja_laki,df_tenagakerja_perempuan], axis='columns')
    df_transformed = df_transform
    return render_template('transformasi.html',data_transfomasi=[df_transformed.to_html(classes="table table-bordered hover",table_id="data")])


@app.route('/cluster', methods=['GET', 'POST'])
def cluster():
    var_cluster = request.form.get('titik_pusat')
    global data_cluster

    # ##CLUSTERING
    kmedoids = KMedoids(n_clusters=int(var_cluster), random_state=0).fit(df_transformed)
    df_transformed.shape
    labels = kmedoids.predict(df_transformed)
    kmedoids.cluster_centers_
    df_transformed['cluster'] = labels
    
    silh_avg_score_ = silhouette_score(df_transformed, labels)
    data_print_cluster = data_cluster
    data_print_cluster["cluster"] = labels

    new_X = data_print_cluster

    new_Y = pd.DataFrame(new_X)
    clust = []
    label = kmedoids.n_clusters
    for i in range(label):
        clust.append(new_Y.apply(lambda x: True if x['cluster'] == i else False , axis=1))

    jumlah = []
    nama_clust = []
    for i in range(len(clust)):
        jumlah.append(len(clust[i][clust[i] == True].index))
        nama_clust.append(f"cluster {i}")

    Data = {'Chart': jumlah}
    diagram_pie = pd.DataFrame(Data,columns=['Chart'],index = nama_clust)

    diagram_pie.plot.pie(y='Chart',figsize=(8,8),autopct='%1.2f%%', startangle=70)
    plt.savefig('static/img/chart.png', format='png', bbox_inches='tight')



    return render_template('cluster.html',data_hasil=[data_print_cluster.to_html(classes="table table-bordered hover",table_id="data")],cluster_count=var_cluster,slh=silh_avg_score_)


if __name__ == '__main__':
    app.run(debug=True)