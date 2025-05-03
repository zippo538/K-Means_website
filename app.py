from io import BytesIO
from flask import render_template, request, redirect, send_file, url_for, session, jsonify, send_from_directory, flash, render_template_string
from dotenv import load_dotenv
from controller.renderer import MarkdownRenderer
import os
import pandas as pd
import numpy as np
import json
import math
import markdown
import pdfkit
import tempfile
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.decomposition import PCA
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app_factory import create_app
from services.redis_service import RedisService
from controller.api_groq import ApiGroq

load_dotenv()
app = create_app()
groq_api_key = os.getenv('GROQ_KEY')
md_renderer = MarkdownRenderer()
PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')

##error handling 
# Halaman 404 Kustom
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

# Halaman 500 Kustom
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


## route
@app.route('/')
def index():
    serialize_data = RedisService.get_data(key='data_key')
    if not session.get('file_uploaded'):
        flash('Silahkan upload file terlebih dahulu', 'error')
        return redirect(url_for('import_file')) 
    else:
        return render_template('pages/index.html', data=serialize_data,title='Data Profiling')
     
@app.route('/upload')
def upload_file():
    try : 
        file = RedisService.get_data(key='file_uploaded')['file_name']
        df= pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], file))
        name = file
                    
        # Ambil header nilai try
        data_value = df.iloc[:, 4:]          
        
        rows = len(df.index)
        header_nilai_tryout = data_value.columns.tolist()
        headers = df.axes[1].tolist()
        
        attributes = len(data_value)
        types = []
        maxs = []
        mins = []
        means = []
            
        for i in range (len(header_nilai_tryout)):
                types.append(str(df[header_nilai_tryout[i]].dtypes.name))
                if df[header_nilai_tryout[i]].dtypes != object:
                    maxs.append(float(df[header_nilai_tryout[i]].max()))
                    mins.append(float(df[header_nilai_tryout[i]].min()))
                    means.append(float(df[header_nilai_tryout[i]].mean()))
                else : 
                    maxs.append(0)
                    mins.append(0)
                    means.append(0)
                
        zipped_data = list(zip(header_nilai_tryout,types,maxs,mins,means))
        datas = df.values.tolist()
        data = {
                'header' : header_nilai_tryout,
                'headers' : headers,
                'name' : name,
                'attributes' : attributes,
                'rows' : rows,
                'zipped_data' : zipped_data,
                'df' : datas,
                'type' : types,
                'maxs' : maxs,
                'mins' : mins,
                'means' : means,
                'zip_select_col' : None,
            }
        RedisService.set_data(key='data_key',data=data)
        RedisService.set_data(data=df, key='df_key')            
        return redirect(url_for('index'))
    except Exception as e :
        app.logger.error(f'Error occurred: {e}')
        print(f'Error occurred: {e}')
        return "An error occurred", 500

###page
@app.route('/help',methods=['GET'])
def help_page():
    return render_template('pages/help.html',title='Help')
@app.route('/import_file',methods=['GET','POST'])
def import_file():
    if request.method == 'POST':
        # Proses file upload
        file = request.files['file']
        if not file.filename.endswith('.csv'):
            flash('File tidak valid. Pastikan file yang diunggah adalah file CSV.', 'error')
            return redirect(url_for('import_file'))
        if file and file.filename.endswith('.csv') :
            # Simpan status upload di session
            session['file_uploaded'] = True
            data = {
                'file_name' : file.filename,
                'file_size' : file.content_length,
                'file_type' : file.content_type
            }
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            RedisService.set_data(key='file_uploaded',data=data)
            return redirect(url_for('upload_file'))
    else : 
        # Render halaman import file
        return render_template('pages/import.html',title='Import File')

@app.route('/data',methods=['GET'])
def get_data():
    serialize_data = RedisService.get_data('data_key')
    if not session.get('select_columns'):
        flash('Silahkan pilih kolom terlebih dahulu', 'error')
        return redirect(url_for('index'))
    else:
        return render_template('pages/data.html', data=serialize_data,title='Normalization')
#page result
@app.route('/result', methods=['GET', 'POST'])
def get_result():
    get_data_key = RedisService.get_data('data_key')
    if not session.get('correct_data') and not session.get('normalization_data'):
        # Jika session kmeans tidak ada, redirect ke halaman data
        flash('Data belum diclustering.', 'error')
        return redirect(url_for('get_data'))
    
    if request.method == "POST":
        # Ambil nilai kValue dari form
        kValue = int(request.form.get('kValue'))
        
        # Perbarui hasil clustering dengan kValue yang baru
        get_data_key['kmeans'] = kmenas_clustering(kValue)
        
        # Simpan data yang diperbarui ke Redis
        RedisService.set_data(key='data_key',data= get_data_key)
        
        # Perbarui hasil di Redis
        update_result(get_data_key)
        
        # Redirect ke halaman result untuk menampilkan hasil yang diperbarui
        return redirect(url_for('get_result'))
    
    else :
        # Ambil parameter halaman dari URL (default: halaman 1)
        page = request.args.get('page', 1, type=int)
        
        # Jumlah data per halaman
        per_page = 10
        
        
        # Ambil data clustering dari Redis
        if 'result_kmeans' in get_data_key:
            clustering_data = get_data_key['result_kmeans']
            header = clustering_data['header']
            
            # Hitung total halaman
            total_data = len(clustering_data['data'])  # Jumlah total data
            total_pages = math.ceil(total_data / per_page)
            
            # Ambil data untuk halaman yang diminta
            start = (page - 1) * per_page
            end = start + per_page
            paginated_data = clustering_data['data'][start:end]
            
            # Tambahkan informasi pagination ke data
            clustering_data['paginated_data'] = paginated_data
            clustering_data['page'] = page
            clustering_data['total_pages'] = total_pages
        else:
            clustering_data = None
        return render_template('pages/result.html', data=get_data_key, clustering_data=clustering_data, header = header,title='Result')
    
    
def update_result(data_key) :
    get_df = RedisService.get_data('df_key',as_dataframe=True)
    get_cluster = data_key['kmeans']['cluster']
    df = pd.DataFrame(get_df)
    df['cluster'] = get_cluster
    header = df.columns.tolist()
    value= df.values.tolist()
    data_key['result_kmeans'] = {
        'header' : header,
        'data' : value
    }
    return RedisService.set_data(key='data_key',data=data_key)


## render markdown 
### rekomendasi
@app.route('/rekomendasi',methods=['GET'])
def rekomendasi() : 
    if session.get('ai_called') : 
        return md_renderer.render_file('rekomendasi_guru.md')
    
    session['ai_called'] = True
    return md_renderer.render_file('rekomendasi_guru.md')
@app.route('/rekomendasi/get_data', methods=['POST'])
def get_data_rekomendasi() -> str :
    #jika tidak ada session
    if 'ai_called' not in session:
        session['ai_called'] = False
        try:
            api_groq = ApiGroq(api_key=str(groq_api_key))
            recommendation = api_groq.recomendation(
                key_redis='data_key',
                key_data='result_kmeans'
            )
            print("hello world")
            print(recommendation)
            
            session['ai_called'] = True
            return jsonify({
                "success": True,
                "message" : recommendation,
                "redirect_url": url_for('rekomendasi')
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500
                
    if session['ai_called'] : 
        return jsonify({
            "redirect": True,
            "redirect_url": url_for('rekomendasi')
        })



##Reset DB
@app.route('/reset-all')
def reset_all():
    try:
        # 1. Hapus semua data Redis
        path = RedisService.get_data(key='file_uploaded')['file_name']
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], path)
        RedisService.clearDB();
        # 2. Hapus file tertentu
        files_to_delete = [
            folder_path,
            'rekomendasi_guru.md',
        ]
        
        for file_path in files_to_delete:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # 3. Hapus session
        session.clear()
        flash('Reset berhasil! Semua data dan file telah dihapus.', 'success')
    except Exception as e:
        app.logger.error(f'Error saat reset: {str(e)}')
        flash('Gagal melakukan reset', 'danger')
    return redirect(url_for('import_file')) 


###Download

@app.route('/download/excel')
def download_excel():
    # Ambil data dari Redis
    get_data_key = RedisService.get_data(key='data_key')
    
    if 'result_kmeans' in get_data_key:
        clustering_data = get_data_key['result_kmeans']
        
        # Buat DataFrame dari data clustering
        df = pd.DataFrame(data=clustering_data['data'],columns=clustering_data['header'])
        # Simpan DataFrame ke dalam file Excel
        excel_file = BytesIO()
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Clustering Result')
        
        excel_file.seek(0)
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='clustering_result.xlsx'
        )
    else:
        return "No clustering data available", 404

@app.route('/download/pdf')
def download_pdf():
    # Ambil data dari Redis
    if not session.get('ai_called'):
        flash('Silahkan pilih rekomendasi AI terlebih dahulu', 'error')
        return redirect(url_for('result'))
    
    try:
        #path markdown
        markdown_path = os.path.join(app.root_path,'rekomendasi_guru.md')
        base_html_markdown = os.path.join(app.root_path,'templates','pages','download_pdf.html')
        
        # Baca konten markdown
        with open(markdown_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        # baca konten template html
        with open(base_html_markdown, 'r', encoding='utf-8') as file:
            template_content = file.read()

        
        # Konversi markdown ke HTML
        html_content = markdown.markdown(markdown_content,extensions=['tables', 'fenced_code'])
        
        #render ke template html
        full_html = render_template('pages/download_pdf.html', content=html_content)
        
        # Opsi untuk pdfkit
        options = {
            'enable-local-file-access': None,
            'margin-top': '15mm',
            'margin-right': '15mm',
            'margin-bottom': '15mm',
            'margin-left': '15mm',
            'encoding': "UTF-8",
            'quiet': '',
            'no-stop-slow-scripts': '',
            'javascript-delay': '1000'  # Beri waktu untuk JS dijalankan
        }
        
        # Buat file PDF sementara
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            pdfkit.from_string(
                full_html, 
                temp_pdf.name, 
                configuration=PDFKIT_CONFIG,
                options=options
                )
            temp_pdf_path = temp_pdf.name
        
        # Kirim file PDF sebagai response
        return send_file(
            temp_pdf_path,
            as_attachment=True,
            download_name="Rekomendasi Guru.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        flash('Gagal mengunduh PDF', 'error')
        app.logger.error(f'Error saat mengunduh PDF: {str(e)}')
        redirect(url_for('result'))
    
    finally:
        # Pastikan file temporary dihapus setelah dikirim
        if 'temp_pdf_path' in locals() and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
      

@app.route('/download/download-template')
def download_template():
    # Pastikan file template ada di folder 'static/templates'
    template_path = os.path.join(app.root_path, 'static', 'templates', 'file.csv')
    
    if not os.path.exists(template_path):
        return "Template tidak ditemukan", 404
    
    return send_from_directory(
        directory=os.path.join(app.root_path, 'static', 'templates'),
        path='file.csv',
        as_attachment=True,
        download_name='file.csv'
    )

#select columns 
@app.route('/select/column',methods = ['POST','GET'])
def select_columns() ->str :
    if request.form.getlist('columns_to_delete') == []:
        flash('Silahkan pilih kolom terlebih dahulu', 'error')
        return redirect(url_for('index')) 
    
    if request.method == 'POST':
        RedisService.delete_key(key='sel_col_key')
        columns = request.form.getlist('columns_to_delete')
        data = RedisService.get_data(key='data_key')
        df = RedisService.get_data(key='df_key',as_dataframe=True)
        df_select_col = df.loc[:,columns]
        header = df_select_col.columns.tolist()
        sel_col = {}
        for col in header:
            sel_col[col]= df[col].tolist()
        
        data['zip_select_col'] = list(zip(header,sel_col.values()))
    
        RedisService.set_data(key='data_key',data=data)
        session['select_columns'] = True
        return redirect(url_for('get_data'))
    

#method normalization 
@app.route('/select/method', methods=['POST'])
def select_method_normalization() -> str : 
    data = RedisService.get_data(key='data_key')
    if not session.get('correct_data') : 
        flash('Silahkan pilih Replace with Mean terlebih dahulu', 'error')
        return redirect(url_for('get_data'))
    if data:
        # Ensure 'zip_select_col' key exists in the JSON data
        if 'zip_select_col' not in data:
            return "Key 'zip_select_col' not found in data", 400
        
        # Convert 'zip_select_col' to DataFrame
        zip_select_col = data['zip_select_col']
        df = pd.DataFrame({col: values for col, values in zip_select_col})
        
        # select_method = request.form.get('select_method')
        # if select_method == 'minmax':
        #     scaler = MinMaxScaler()
        # elif select_method == 'standard':
        #     scaler = StandardScaler()
        # else:
        #     return "Invalid normalization method", 400
        scaler = MinMaxScaler()
        
        normalized_data = scaler.fit_transform(df.values)
        
        # Simpan data yang dinormalisasi ke Redis
        print(df.columns.tolist())
        data['zip_select_col'] = list(zip(df.columns.tolist(), normalized_data.T.tolist()))
        normalized_data_json = {
            'header': df.columns.tolist(),
            'data': normalized_data.tolist()    
        }
        RedisService.set_data(key='normalized_key', data= normalized_data_json)
        RedisService.set_data(key='data_key', data= data)
        session['normalization_data'] = True
        session['kmeans'] = False
        return redirect(url_for("get_data"))
    else:
        return "No data found", 400
    
#correct data
@app.route('/select/correct_data', methods=['POST'])
def select_correct_data() -> redirect:
    try:
        data_key = RedisService.get_data(key='data_key')
        zip_normalized = data_key['zip_select_col']    
        select_method = request.form.get('select_correct_data')
        df = pd.DataFrame({col: values for col, values in zip_normalized})
        # if select_method == 'delete':
        #     df_zip_normalized= delete_specific_values(df)
        #     print('sesudah di delete',df_zip_normalized.T.values.tolist())
        #     normalized_data_json = {
        #         'header': df.columns.tolist(),
        #         'data': df_zip_normalized.values.tolist()
        #     }
        #     data_key['zip_select_col'] = list(zip(df.columns.tolist(), df_zip_normalized.T.values.tolist()))
        #     set_data_to_redis('data_key',data_key)
        #     set_data_to_redis('normalized_key',normalized_data_json)
        #     return redirect(url_for('get_data'))        
        # elif select_method == 'replace':
        arr_df = np.array(df.values)
        df_zip_normalized = fill_zeros_with_last(arr_df)
        print(df_zip_normalized.T.tolist())
        normalized_data_json = {
            'header': df.columns.tolist(),
            'data': df_zip_normalized.T.tolist()
        }
        data_key['zip_select_col'] = list(zip(df.columns.tolist(), df_zip_normalized.T.tolist()))
        RedisService.set_data(key='data_key',data=data_key)
        RedisService.set_data(key='normalized_key',data=normalized_data_json)
        session['correct_data'] = True
        return redirect(url_for('get_data'))
    except Exception as e:
        app.logger.error(f'Error occurred: {e}')
        print(f'Error occurred: {e}')
        return "An error occurred", 500       
        
    

def delete_specific_values(df, value_to_delete=[0,np.nan]) -> pd.DataFrame:
    df.replace(value_to_delete, pd.NA, inplace=True)
    df.dropna(inplace=True)
    return df

def fill_zeros_with_last(arr) -> np.ndarray:
      for row_idx in range(arr.shape[0]):
        # Create a 1D view of the current row
        row = arr[row_idx, :]
        # Hitung rata-rata dari elemen yang bukan 0 di baris tersebut
        non_zero_non_nan_mean = row[(row != 0) & (~np.isnan(row))].mean() if np.count_nonzero(row) != 0 else 0
        # Gantikan nilai 0 dengan rata-rata
        print(non_zero_non_nan_mean)
        row[row == 0] = non_zero_non_nan_mean
        row[np.isnan(row)] = non_zero_non_nan_mean
      return arr

## K-means clustering

def elbow_method () -> str:
    normalized_key = RedisService.get_data(key='normalized_key')
    if session.get('normalization_data') and session.get('correct_data') : 
        data_key = RedisService.get_data(key='data_key')
        df = pd.DataFrame(data=normalized_key['data'], columns=normalized_key['header'])
        distortions = []
        K = list(range(1, 10))
        for k in K:
            kmeanModel = KMeans(n_clusters=k,max_iter=100, init='k-means++', random_state=34)
            kmeanModel.fit(df)
            distortions.append(kmeanModel.inertia_)
        data_json = {
            'K': K,
            'distortions': distortions
        }
        data_key['elbow_method'] = list(zip(K,distortions))
        RedisService.set_data(key='data_key',data= data_key)
        session['elbow_method'] = True
        return data_json
    else :
        normalized_data = {
                'header': None,
                'data' : None
        } 
        return RedisService.set_data(key='normalized_key',data=normalized_data)
        

def kmenas_clustering(k : int) -> str:
    normalized_key = RedisService.get_data(key='normalized_key')
    print(f"clustering with {k}")
    if session.get('file_uploaded') and normalized_key['data'] : 
        data_key = RedisService.get_data(key='data_key')
        name_data = data_key['df']
        # Mengurangi dimensi data menggunakan PCA 
        data = normalized_key['data']
        # Mengunakan K-Means pada data yang telah direduksi
        kmeans = KMeans(n_clusters=k,max_iter=100, init='k-means++', random_state=34)
        kmeans.fit(data)
        
        
        # Mengambil nama siswa    
        name = []
        for i in range(len(name_data)):
            name.append(name_data[i][2])
        
        # Mengambil cluster label dan centroid
        cluster = kmeans.labels_.tolist()
        cluster_centers = kmeans.cluster_centers_.tolist()
    
        silhouette_score_val = silhouette_score(data, kmeans.labels_)
        sample_silhouette_values = silhouette_samples(data, kmeans.labels_)
        silhouette_per_cluster = []
        for i in range(k):
            ith_cluster_silhouette_values = \
                sample_silhouette_values[kmeans.labels_ == i]
            ith_cluster_silhouette_values.sort()
            silhouette_per_cluster.append(ith_cluster_silhouette_values.tolist())
    
        data_key =  {
            'data' : data,
            'cluster' : cluster,
            'cluster_centers' : cluster_centers,
            'name' : name,
            'silhouette_scor_avg' : silhouette_score_val,
            'silhouette_per_cluster' : silhouette_per_cluster
            
            }
        session['kmeans'] = True
        return data_key     
   

##api

def get_null_or_missing_value ()->str : 
    df = RedisService.get_data(key='df_key',as_dataframe=True)
    df_int = []
    for col_name, col_type in df.dtypes.items():  # Iterate through column names and types
        if col_type != 'object':
            df_int.append(col_name)
    sel_col = df[df_int]
    zero_value_columns = sel_col.columns[(sel_col == 0).any()]
    zero_count = (sel_col == 0).sum()[zero_value_columns]
    zero_counts_json = {'labels' : zero_count.index.tolist(), 'values' : zero_count.tolist()}
    return zero_counts_json


    
def top_students_with_zero() ->str :
    df = RedisService.get_data(key='df_key',as_dataframe=True)
    value_columns = df.columns[2:]  # Mengambil semua kolom kecuali 'No' dan 'id user'

    # 2. Hitung jumlah nilai 0 untuk setiap siswa
    df['zero_count'] = df[value_columns].apply(lambda row: (row == 0).sum(), axis=1)

    # 3. Urutkan DataFrame berdasarkan jumlah nilai 0
    sorted_df = df.sort_values(by='zero_count', ascending=False)

    # 4. Ambil siswa dengan jumlah nilai 0 terbanyak
    # top_students_with_zero = sorted_df[['Nama \npanggilan', 'zero_count']].head(10).tolist()
    # Ambil 10 siswa teratas
    data_top_students_with_zero = {
        'labels' : sorted_df['Nama panggilan'].head(10).values.tolist(),
        'values' : sorted_df['zero_count'].head(10).values.tolist()
        }
    # Tampilkan hasil
    return data_top_students_with_zero
def get_data_from_dataframe() -> str:
    if os.path.exists('uploads/data.csv'):
        df = pd.read_csv('uploads/data.csv')
        return df.values.tolist()
    else:
        return "Data not found"

@app.route('/api/data/visualization')
def api() -> str:    
    data = {
            'missing_value': get_null_or_missing_value(),
            'top_student_with_zero_': top_students_with_zero(),
            }
    return data

@app.route('/api/data/boxplot')
def api_dataframe() -> str: 
    df = RedisService.get_data(key='df_key',as_dataframe=True)
    data = df.iloc[:, 4:].values.tolist()
    header = df.columns[4:].tolist()
    return {'data': data, 'header': header}

@app.route('/api/data/kmeans')
def api_kmeans() :    
    get_data = RedisService.get_data(key='data_key')
    if 'kmeans' in get_data : 
        get_kmeans = get_data['kmeans']
        data = {'kmeans' : get_kmeans}
        return data
    
@app.route('/api/data/elbowMethod')
def api_eblowMethod() : 
    data = {'elbow_method': elbow_method()}
    return data
    


if __name__ == '__main__':
    app.run(debug=True,port=8080)