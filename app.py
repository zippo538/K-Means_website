from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import json

app = Flask(__name__)

# Route to render the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route for uploading and processing data
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Read uploaded file into a DataFrame
        df = pd.read_csv(file)
        
        # Store the DataFrame in JSON format for session-like usage
        request_data = {
            "columns": df.columns.tolist(),
            "data": df.to_json()
        }

        return jsonify(request_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

if __name__ == '__main__':
    app.run(debug=True)
