import redis
import os
from dotenv import load_dotenv

load_dotenv()

class RedisConfig:
    def __init__(self):
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = os.getenv('REDIS_PORT', 6379)
        self.db = os.getenv('REDIS_DB', 1)
        self.password = os.getenv('REDIS_PASSWORD', None)
        
    def get_connection(self):
        return redis.StrictRedis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=True
        )

# Singleton instance
redis_connection = RedisConfig().get_connection()