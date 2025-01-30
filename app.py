from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
from dotenv import load_dotenv
import csv
import os 
import json
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'uploads'

# Route to render the homepage
@app.route('/')
def start():
    return render_template('index.html')

# Route for uploading and processing data
@app.route('/home', methods=['POST','GET'])
def home():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and file.filename.endswith('.csv'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        rename_file = 'data.csv'
        
        new_file_path = os.path.join(app.config['UPLOAD_FOLDER'], rename_file)
        
        file.save(file_path)
        os.rename(file_path, new_file_path)
        
        # Baca isi file CSV
        name = rename_file
        df = pd.read_csv(new_file_path)
        dataframe = df.to_json()
                
        session['df'] = dataframe
        
        rows = len(df.index)
        session['rows'] = rows
        header = df.axes[1].values.tolist()
        session['header'] = header
        
        attributes = len(header)
        types = []
        maxs = []
        mins = []
        means = []
        
        for i in range (len(header)):
            types.append(df[header[i]].dtypes.name)
            if df[header[i]].dtypes != object:
                maxs.append(df[header[i]].max())
                mins.append(df[header[i]].min())
                means.append(df[header[i]].mean())
            else : 
                maxs.append(0)
                mins.append(0)
                means.append(0)
            
        zipped_data = zip(header,types,maxs,mins,means)
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
        }
        #session['data'] = data
        return render_template('table.html', data=data)
    else:
        flash('File must be in CSV format')
        return render_template('index.html')

# Route for clustering
@app.route('/cluster', methods=['POST'])
def cluster():
    try:
        data = request.json
        df = pd.read_json(data['data'])
        features = data['features']
        k = data['k']

        # Scale the features
        scaler = MinMaxScaler()
        x_scaled = scaler.fit_transform(df[features])

        # Apply K-Means clustering
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(x_scaled)
        
        # Add cluster labels to the DataFrame
        df['cluster'] = kmeans.labels_
        
        # Calculate cluster centers
        centers = kmeans.cluster_centers_.tolist()

        return jsonify({
            "clusters": df['cluster'].value_counts().to_dict(),
            "centers": centers,
            "data_with_clusters": df.to_json()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/viewdata')
def viewdata() : 
    data = session.get('rows,{}')
    return render_template('test.html',data=data)
@app.route('/back')
def go_back():
    return redirect(request.referrer or url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)
