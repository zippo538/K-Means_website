from flask import Flask
from flask_session import Session
from config.session_config import session_config
from config.redis_config import RedisConfig
import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv()
def create_app():
    app = Flask(__name__)
    
    # Konfigurasi dasar
    app.secret_key = os.getenv('SECRET_KEY')
    
    # Konfigurasi session
    app.config.from_object(session_config)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # Inisialisasi Flask-Session
    Session(app)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    return app