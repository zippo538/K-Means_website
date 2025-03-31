from config.redis_config import redis_connection
import pandas as pd
import json
from io import StringIO

class RedisService:
    @staticmethod
    def set_data(key: str, data, expire: int = None) -> bool:
        """
        Menyimpan data ke Redis
        :param key: Kunci unik untuk data
        :param data: Data yang akan disimpan (dict, list, str, dll)
        :param expire: Waktu kedaluwarsa dalam detik (opsional)
        :return: Boolean apakah operasi berhasil
        """
        try:
            if isinstance(data, pd.DataFrame):
                data = data.to_json(orient='split')
            elif isinstance(data, (dict, list)):
                data = json.dumps(data)
            
            redis_connection.set(key, data)
            if expire:
                redis_connection.expire(key, expire)
            return True
        except Exception as e:
            print(f"Error setting Redis data: {e}")
            return False

    @staticmethod
    def get_data(key: str, as_dataframe: bool = False):
        """
        Mengambil data dari Redis
        :param key: Kunci data
        :param as_dataframe: Konversi ke DataFrame jika True
        :return: Data yang diminta atau None jika tidak ada
        """
        try:
            data = redis_connection.get(key)
            if not data:
                return None
                
            if as_dataframe:
                # json_string = data.decode('utf-8')
                return pd.read_json(StringIO(data), orient='split')
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        except Exception as e:
            print(f"Error getting Redis data: {e}")
            return None

    @staticmethod
    def delete_key(key: str) -> bool:
        """Menghapus key dari Redis"""
        try:
            return redis_connection.delete(key) > 0
        except Exception as e:
            print(f"Error deleting Redis key: {e}")
            return False

    @staticmethod
    def check_key_exists(key: str) -> bool:
        """Memeriksa apakah key ada di Redis"""
        try:
            return redis_connection.exists(key) == 1
        except Exception as e:
            print(f"Error checking Redis key: {e}")
            return False
    @staticmethod
    def clearDB():
        """Menghapus semua data di Redis"""
        try:
            redis_connection.flushall()
            return True
        except Exception as e:
            print(f"Error clearing Redis DB: {e}")
            return False
