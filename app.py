from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import re
import os
import redis
import pandas as pd
import numpy as np
import json
from flask_session import Session
from io import StringIO
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'redis'  
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url('redis://127.0.0.1:6379')
# Configure Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=1)
# redis_client.set('normalized_key', None)

Session(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


## route

@app.route('/')
def index():
    serialize_data = redis_client.get('data_key')
    if serialize_data:
        data = json.loads(serialize_data)
        return render_template('index.html', data=data)
    else:
        return render_template('index.html', data=None)
def serialize_df_to_json(df):
    return df.to_json(orient='split')
def retrive_df_from_redis(key : str) -> pd.DataFrame:
    retrive_data =  redis_client.get(key)
    json_string = retrive_data.decode('utf-8')
    df = pd.read_json(json_string,orient='split')
    return df
def retrive_data_from_redis(key: str) -> str:
    retrive_data = redis_client.get(key)
    json_data = json.loads(retrive_data.decode('utf-8'))
    return json_data
def set_data_to_redis(key: str, data) -> str: 
    data_json = json.dumps(data)
    set_data =redis_client.set(key,data_json)
    return set_data

def remove_html_tags(text) -> str:
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def convert_df_to_json_and_remove_html(df) -> str:
    df_json = df.to_json(orient='split')
    df_json_no_html = remove_html_tags(df_json)
    parsed_json = json.loads(df_json_no_html)
    clean_json = json.dumps(parsed_json, ensure_ascii=False)
    return clean_json

     

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
            rename =  'data.csv'
            file_path_rename =  os.path.join(app.config['UPLOAD_FOLDER'], rename)
            file.save(filepath)
            os.rename(filepath, file_path_rename)
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
            
            set_data_to_redis('data_key',data)
            serialized_df = serialize_df_to_json(df)            
            redis_client.set('df_key',serialized_df)
            return render_template('index.html', data=data)
        else:
            return "File harus berupa CSV", 400
    except Exception as e :
        app.logger.error(f'Error occurred: {e} - Path: {request.path}')
        return "An error occurred", 500


@app.route('/data',methods=['GET'])
def get_data():
    if request.method == "GET":
        serialize_data = redis_client.get('data_key')
        if serialize_data or None:
            data = json.loads(serialize_data)
            return render_template('data.html', data=data)
        else:
            return render_template('data.html', data=None)

@app.route('/result',methods=['GET'])
def get_result():
    if request.method == "GET":
        serialize_data = redis_client.get('data_key')
        if serialize_data or None:
            data = json.loads(serialize_data)
            return render_template('result.html', data=data)
        else:
            return render_template('result.html', data=None)




#select columns 
@app.route('/select/column',methods = ['POST','GET'])
def select_columns() ->str : 
    if request.method == 'POST':
        redis_client.delete('sel_col_key')
        columns = request.form.getlist('columns_to_delete')
        data = redis_client.get('data_key')
        data = json.loads(data.decode('utf-8'))
        df = retrive_df_from_redis('df_key')
        df_select_col = df.loc[:,columns]
        header = df_select_col.columns.tolist()
        sel_col = {}
        for col in header:
            sel_col[col]= df[col].tolist()
        
        data['zip_select_col'] = list(zip(header,sel_col.values()))
    
        set_data_to_redis('data_key',data)
        return redirect(url_for('get_data'))
    else : 
        data = redis_client.get('data_key').decode('utf-8')
        if data : 
            data = json.loads(data)
        return render_template('data.html',data=data)

#method normalization 
@app.route('/select/method', methods=['POST'])
def select_method_normalization() -> str : 
    data = redis_client.get('data_key')
    if data:
        json_string = data.decode('utf-8')
        json_data = json.loads(json_string)
        
        # Ensure 'zip_select_col' key exists in the JSON data
        if 'zip_select_col' not in json_data:
            return "Key 'zip_select_col' not found in data", 400
        
        # Convert 'zip_select_col' to DataFrame
        zip_select_col = json_data['zip_select_col']
        df = pd.DataFrame({col: values for col, values in zip_select_col})
        
        select_method = request.form.get('select_method')
        if select_method == 'minmax':
            scaler = MinMaxScaler()
        elif select_method == 'standard':
            scaler = StandardScaler()
        else:
            return "Invalid normalization method", 400
        normalized_data = scaler.fit_transform(df.values)
        
        # Simpan data yang dinormalisasi ke Redis
        print(df.columns.tolist())
        json_data['zip_select_col'] = list(zip(df.columns.tolist(), normalized_data.T.tolist()))
        normalized_data_json = {
            'header': df.columns.tolist(),
            'data': normalized_data.tolist()    
        }
        set_data_to_redis('normalized_key', normalized_data_json)
        set_data_to_redis('data_key', json_data)
        return redirect(url_for("get_data"))
    else:
        return "No data found", 400
    
#correct data
@app.route('/select/correct_data', methods=['POST'])
def select_correct_data() -> redirect:
    data_key = retrive_data_from_redis('data_key')
    zip_normalized = data_key['zip_select_col']    
    select_method = request.form.get('select_correct_data')
    df = pd.DataFrame({col: values for col, values in zip_normalized})
    print(df)
    if select_method == 'delete':
        df_zip_normalized= delete_specific_values(df)
        print('sesudah di delete',df_zip_normalized.T.values.tolist())
        normalized_data_json = {
            'header': df.columns.tolist(),
            'data': df_zip_normalized.values.tolist()
        }
        data_key['zip_select_col'] = list(zip(df.columns.tolist(), df_zip_normalized.T.values.tolist()))
        set_data_to_redis('data_key',data_key)
        set_data_to_redis('normalized_key',normalized_data_json)
        return redirect(url_for('get_data'))        
    elif select_method == 'replace':
        arr_df = np.array(df.values)
        df_zip_normalized = fill_zeros_with_last(arr_df)
        normalized_data_json = {
            'header': df.columns.tolist(),
            'data': df_zip_normalized.T.tolist()
        }
        data_key['zip_select_col'] = list(zip(df.columns.tolist(), df_zip_normalized.T.tolist()))
        set_data_to_redis('data_key',data_key)
        set_data_to_redis('normalized_key',normalized_data_json)
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
    normalized_key = retrive_data_from_redis('normalized_key')
    data_key = retrive_data_from_redis('data_key')
    df = pd.DataFrame(normalized_key['data'], columns=normalized_key['header'])
    distortions = []
    K = list(range(1, 10))
    for k in K:
        kmeanModel = KMeans(n_clusters=k)
        kmeanModel.fit(df)
        distortions.append(kmeanModel.inertia_)
    data_json = {
        'K': K,
        'distortions': distortions
    }
    data_key['elbow_method'] = list(zip(K,distortions))
    set_data_to_redis('data_key', data_key)
    return data_json

def kmenas_clustering(k : int) -> str:
    normalized_key = retrive_data_from_redis('normalized_key')
    data_key = retrive_data_from_redis('data_key')
    df = pd.DataFrame(normalized_key['data'], columns=normalized_key['header'])
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(df)
    data_key['kmeans'] = kmeans.labels_.tolist()
    set_data_to_redis('data_key', data_key)
    return kmeans.labels_.tolist()

##api

def get_null_or_missing_value ()->str : 
    df = retrive_df_from_redis('df_key')
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
    df = retrive_df_from_redis('df_key')
    sum_status= df['Status'].value_counts().tolist()
    data_sum_status = {
        'labels' : df['Status'].unique().tolist(),
        'values' : sum_status
    }
    return data_sum_status
    
def top_students_with_zero() ->str :
    df = retrive_df_from_redis('df_key')
    value_columns = df.columns[2:]  # Mengambil semua kolom kecuali 'No' dan 'id user'

    # 2. Hitung jumlah nilai 0 untuk setiap siswa
    df['zero_count'] = df[value_columns].apply(lambda row: (row == 0).sum(), axis=1)

    # 3. Urutkan DataFrame berdasarkan jumlah nilai 0
    sorted_df = df.sort_values(by='zero_count', ascending=False)

    # 4. Ambil siswa dengan jumlah nilai 0 terbanyak
    # top_students_with_zero = sorted_df[['Nama \npanggilan', 'zero_count']].head(10).tolist()
    # Ambil 10 siswa teratas
    data_top_students_with_zero = {
        'labels' : sorted_df['Nama \npanggilan'].head(10).values.tolist(),
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
    data= {
        'missing_value' : get_null_or_missing_value(),
        'sum_status'    : sum_status(),
        'top_student_with_zero_' : top_students_with_zero(),
        'elbow_method' : elbow_method(),
        'kmeans' : kmenas_clustering(3),
    }
    return data

@app.route('/api/data/boxplot')
def api_dataframe() -> str: 
    df = retrive_df_from_redis('df_key')
    data = df.iloc[:, 4:]
    delete_col = ['Status','Gel','Jumlah absen \n TWK']
    data = data.drop(delete_col, axis=1)
    data = data.values.tolist()
    header = df.columns[4:].tolist()
    return {'data': data, 'header': header}
    

if __name__ == '__main__':
    app.run(debug=True)