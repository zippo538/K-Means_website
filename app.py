from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
import csv
import pandas as pd
import json
from flask_session import Session
from io import StringIO

load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'  
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
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
        session['df'] = df.to_json()
        session['rows'] = rows
        session['header'] = header
        # print(session['rows'])
        # print(session['header'])
            
        attributes = len(header)
        types = []
        maxs = []
        mins = []
        means = []
        missing_data = []
            
        for i in range (len(header)):
                types.append(df[header[i]].dtypes.name)
                missing_data.append(df[header[i]].isnull().sum())
                if df[header[i]].dtypes != object:
                    maxs.append(df[header[i]].max())
                    mins.append(df[header[i]].min())
                    means.append(df[header[i]].mean())
                else : 
                    maxs.append(0)
                    mins.append(0)
                    means.append(0)
                
        zipped_data = zip(header,types,maxs,mins,means,missing_data)
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
        session['data'] = data
        return render_template('index.html', data=data)
    else:
        return "File harus berupa CSV", 400
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
    print(data)
    return render_template('index.html',data=data)
    

if __name__ == '__main__':
    app.run(debug=True)