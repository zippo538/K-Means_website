from io import BytesIO
from flask import render_template, request, redirect, send_file, url_for, session, jsonify
from dotenv import load_dotenv
from controller.renderer import MarkdownRenderer
import os
import pandas as pd
import numpy as np
import json
import math
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
## route

@app.route('/')
def index():
    serialize_data = RedisService.get_data(key='data_key')
    if serialize_data:
        return render_template('pages/index.html', data=serialize_data,title='Data Profiling')
    else:
        return render_template('pages/index.html', data=None,title='Data Profiling')
     
@app.route('/upload', methods=['POST'])
def upload_file():
    try : 
        if 'csvFile' not in request.files:
            return "Tidak ada file yang diupload", 400

        file = request.files['csvFile']
        if file.filename == '':
            return "File tidak dipilih", 400

        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            df= pd.read_csv(filepath)
            name = file.filename
                        
            
            rows = len(df.index)
            header = df.axes[1].values.tolist()
            attributes = len(header)
            types = []
            maxs = []
            mins = []
            means = []
            missing_data = []
                
            for i in range (len(header)):
                    types.append(str(df[header[i]].dtypes.name))
                    missing_data.append(int(df[header[i]].isnull().sum()))
                    if df[header[i]].dtypes != object:
                        maxs.append(float(df[header[i]].max()))
                        mins.append(float(df[header[i]].min()))
                        means.append(float(df[header[i]].mean()))
                    else : 
                        maxs.append(0)
                        mins.append(0)
                        means.append(0)
                    
            zipped_data = list(zip(header,types,maxs,mins,means,missing_data))
            datas = df.values.tolist()
            data = {
                    'header' : header,
                    'headers' : json.dumps(header),
                    'name' : name,
                    'attributes' : attributes,
                    'rows' : rows,
                    'zipped_data' : zipped_data,
                    'df' : datas,
                    'type' : types,
                    'maxs' : maxs,
                    'mins' : mins,
                    'means' : means,
                    'missing_data' : missing_data,
                    'zip_select_col' : None
                }
            RedisService.set_data(key='data_key',data=data)
            
            serialized_df = RedisService.set_data(data=df, key='df_key')            
            return redirect(url_for('index'))
        else:
            return "File harus berupa CSV", 400
    except Exception as e :
        app.logger.error(f'Error occurred: {e} - Path: {request.path}')
        return "An error occurred", 500


@app.route('/data',methods=['GET'])
def get_data():
    if request.method == "GET":
        serialize_data = RedisService.get_data('data_key')
        if serialize_data or None:
            return render_template('pages/data.html', data=serialize_data,title='Normalization')
        else:
            return render_template('pages/data.html', data=None,title='Normalization')
#page result
@app.route('/result', methods=['GET', 'POST'])
def get_result():
    get_data_key = RedisService.get_data('data_key')
    
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
    
    if request.method == "GET":
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
        
    
    return redirect(url_for('get_result'))
    
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
    get_data_key = RedisService.get_data(key='data_key')
    
    if 'kmeans' in get_data_key:
        clustering_data = get_data_key['kmeans']
        
        # Buat file PDF
        pdf_file = BytesIO()
        pdf = canvas.Canvas(pdf_file, pagesize=letter)
        
        # Tambahkan judul
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(100, 750, "Clustering Result")
        
        # Tambahkan data ke PDF
        pdf.setFont("Helvetica", 12)
        y = 700
        for i, (name, cluster) in enumerate(zip(clustering_data['name'], clustering_data['cluster'])):
            pdf.drawString(100, y, f"{i+1}. {name} - Cluster {cluster}")
            y -= 20
            if y < 50:  # Jika mencapai batas bawah, buat halaman baru
                pdf.showPage()
                y = 750
        
        pdf.save()
        pdf_file.seek(0)
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='clustering_result.pdf'
        )
    else:
        return "No clustering data available", 404
      
    

#select columns 
@app.route('/select/column',methods = ['POST','GET'])
def select_columns() ->str : 
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
        return redirect(url_for('index'))
    else : 
        data = RedisService.get_data(key='data_key')
        if data : 
            return redirect(url_for('index'))

#method normalization 
@app.route('/select/method', methods=['POST'])
def select_method_normalization() -> str : 
    data = RedisService.get_data(key='data_key')
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
        return redirect(url_for("get_data"))
    else:
        return "No data found", 400
    
#correct data
@app.route('/select/correct_data', methods=['POST'])
def select_correct_data() -> redirect:
    data_key = RedisService.get_data(key='data_key')
    zip_normalized = data_key['zip_select_col']    
    select_method = request.form.get('select_correct_data')
    df = pd.DataFrame({col: values for col, values in zip_normalized})
    print(df)
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
    normalized_data_json = {
        'header': df.columns.tolist(),
        'data': df_zip_normalized.T.tolist()
    }
    data_key['zip_select_col'] = list(zip(df.columns.tolist(), df_zip_normalized.T.tolist()))
    RedisService.set_data(key='data_key',data=data_key)
    RedisService.set_data(key='normalized_key',data=normalized_data_json)
    return redirect(url_for('get_data'))        
        
    

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
        row[row == 0] = non_zero_non_nan_mean
        row[np.isnan(row)] = non_zero_non_nan_mean
      return arr

## K-means clustering

def elbow_method () -> str:
    normalized_key = RedisService.get_data(key='normalized_key')
    if normalized_key['data']: 
        data_key = RedisService.get_data(key='data_key')
        df = pd.DataFrame(normalized_key['data'], columns=normalized_key['header'])
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
    if normalized_key['data'] : 
        data_key = RedisService.get_data(key='data_key')
        name_data = data_key['df']
        # Mengurangi dimensi data menggunakan PCA 
        pca = PCA(n_components=2)
        reduced_data = pca.fit_transform(normalized_key['data'])
        # Mengunakan K-Means pada data yang telah direduksi
        kmeans = KMeans(n_clusters=k,max_iter=100, init='k-means++', random_state=34)
        kmeans.fit(reduced_data)
        
        data_to_json = reduced_data.tolist()
        # Mengambil nama siswa    
        name = []
        for i in range(len(name_data)):
            name.append(name_data[i][2])
        
        # Mengambil cluster label dan centroid
        cluster = kmeans.labels_.tolist()
        cluster_centers = kmeans.cluster_centers_.tolist()
    
        silhouette_score_val = silhouette_score(reduced_data, kmeans.labels_)
        sample_silhouette_values = silhouette_samples(reduced_data, kmeans.labels_)
        silhouette_per_cluster = []
        for i in range(k):
            ith_cluster_silhouette_values = \
                sample_silhouette_values[kmeans.labels_ == i]
            ith_cluster_silhouette_values.sort()
            silhouette_per_cluster.append(ith_cluster_silhouette_values.tolist())
    
        data_key =  {
            'data' : data_to_json,
            'cluster' : cluster,
            'cluster_centers' : cluster_centers,
            'name' : name,
            'silhouette_scor_avg' : silhouette_score_val,
            'silhouette_per_cluster' : silhouette_per_cluster
            
            }
        return data_key     
    

## render markdown
@app.route('/rekomendasi',methods=['GET'])
def rekomendasi() : 
    md_renderer = MarkdownRenderer()
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
    # Proses rekomendasi AI

def can_call_ai():
    """
    Cek apakah user boleh memanggil AI
    Return: Tuple (bool, str) 
    - True jika boleh, False jika sudah digunakan
    - Pesan status
    """
    if 'ai_called' not in session:
        session['ai_called'] = False
        return True, "AI call available"
    elif session['ai_called'] == False:
        return True, "AI call available"
    else:
        return False, "AI already used this session"    
    
@app.route('/rekomendasi/reset', methods=['POST'])
def reset_ai_call():
    """Reset status panggilan (untuk testing/demo)"""
    session['ai_called'] = False
    return jsonify({"success": True, "message": "AI call counter reset"})

@app.route('/rekomendasi/check-ai-call')
def check_ai_call():
    return jsonify({
        'ai_called': session.get('ai_called', False)
    })
    

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

def sum_status()->str:
    # Example implementation
    df = RedisService.get_data('df_key',as_dataframe=True)
    sum_status= df['Status'].value_counts().tolist()
    data_sum_status = {
        'labels' : df['Status'].unique().tolist(),
        'values' : sum_status
    }
    return data_sum_status
    
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
            'sum_status': sum_status(),
            'top_student_with_zero_': top_students_with_zero(),
            }
    return data

@app.route('/api/data/boxplot')
def api_dataframe() -> str: 
    df = RedisService.get_data(key='df_key',as_dataframe=True)
    data = df.iloc[:, 4:]
    delete_col = ['Status','Gel','Jumlah absen TWK','Jumlah absen TIU','Jumlah absen TKP']
    data = data.drop(delete_col, axis=1)
    data = data.values.tolist()
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