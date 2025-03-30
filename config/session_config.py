from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class SessionConfig:
    def __init__(self):
        self.SESSION_TYPE = 'redis'
        self.SESSION_PERMANENT = True
        self.SESSION_USE_SIGNER = True
        self.SESSION_PERMANENT= timedelta(hours=1)
        self.SESSION_REDIS = self._get_redis_connection()
        
    def _get_redis_connection(self):
        import redis
        return redis.StrictRedis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_SESSION_DB', 0)),  # Gunakan DB berbeda dari data utama
            password=os.getenv('REDIS_PASSWORD', None)
        )

# Ekspor konfigurasi
session_config = SessionConfig()