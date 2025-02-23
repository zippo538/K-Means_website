from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
import redis
import pandas as pd
import json
from flask_session import Session
from io import StringIO
from sklearn.preprocessing import MinMaxScaler, StandardScaler

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

Session(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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
def retrive_df_from_redis(key : str) :
    retrive_data =  redis_client.get(key)
    json_string = retrive_data.decode('utf-8')
    df = pd.read_json(json_string,orient='split')
    return df
     
    
    

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
            # session['df'] = df.to_json()
            # session['rows'] = rows
            # session['header'] = header
            # print(session['rows'])
            # print(session['header'])
                
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
                    'missing_data' : missing_data
                }
            serialized_data = json.dumps(data)
            serialized_df = serialize_df_to_json(df)
            redis_client.set('data_key', serialized_data)
            redis_client.set('df_key',serialized_df)
            return render_template('index.html', data=data)
        else:
            return "File harus berupa CSV", 400
    except Exception as e :
        app.logger.error(f'Error occurred: {e} - Path: {request.path}')
        return "An error occurred", 500
@app.route('/get_ovewview_data', )
def bar_chart_preview_data():
    df = pd.read_csv('uploads/data.csv')
    
    data_chart = {}
    return data_chart

@app.route('/delete',methods=['POST'])
def delete():
    # Get the selected columns to delete
    columns_to_delete = request.form.getlist('columns_to_delete')
    print(columns_to_delete)

    # Load the DataFrame from the session
    import_df = StringIO(session['df'])
    df = pd.read_json(import_df)

    # Drop the selected columns
    df = df.drop(columns=columns_to_delete,errors='ignore')

    # Save the updated DataFrame back to the session
    session['df'] = df.to_json()
    session['header'] = df.columns.tolist()
    session['rows'] = len(df.index)
    # Render the updated DataFrame
    # print(session['new_df'])
    print(session['header'])
    # print(session['rows'])
    data = {
        'header' : session['header'],
        'df' : session['df'],
        'rows' : session['rows']
    }
    data = session['data']
    return render_template('index.html',data=data)
    
@app.route('/data',methods=['GET'])
def get_data():
    if request.method == "GET":
        
        return render_template('data.html')

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

#select columns 
@app.route('/select/column',methods = ['POST'])
def select_columns() ->str : 
    columns = request.form.getlist('columns')
    df = retrive_df_from_redis('df_key')
    df_select_col = df.loc[:,columns]
    header = df_select_col.columns.tolist()
    data = {}
    for col in header:
        data[col] = df[col].tolist()
    serialized_col = json.dumps(data)
    redis_client.set('sel_col_key',serialized_col)
    return data

@app.route('/select/method')
def df_normalization () -> str : 
    data = redis_client.get('sel_col_key').decode('utf-8')
    df = pd.read_json(data,orient='split')
    select_methods = request.form.getlist('select_method')
    if select_methods == 'minmax' : 
        scaler = MinMaxScaler()
    elif select_methods == 'standard' : 
        scaler = StandardScaler()
    
    normalized_data = scaler.fit_transform(df)
    serialized_normalized = json.dumps(normalized_data)
    redis_client.set('normalized_key',serialized_normalized)
    return normalized_data 



@app.route('/api/data/visualization')
def api() :
    data= {
        'missing_value' : get_null_or_missing_value(),
        'sum_status'    : sum_status(),
        'top_student_with_zero_' : top_students_with_zero(),
        'select_columns' : select_columns()
    }
    return data

if __name__ == '__main__':
    app.run(debug=True)