import mariadb
import os
from typing import Dict, Optional, Any
from datetime import datetime
from logger import logger
from modules.dataclass_db import PostInfo

class SMariaDB():
    def __init__(self, database: str, user: str = os.environ['MARIADB_USER'], password: str = os.environ['MARIADB_ROOT_PASSWORD'],
                 host: str = os.environ['MARIADB_HOST'], port: int = int(os.environ['MARIADB_PORT'])):
        self.user: str = user
        self.password: str = password
        self.host: str = host
        self.port: int = port
        self.database: str = database

    def __enter__(self):
        # подключаемся к mariadb при инициализации объекта класса SMariaDB
        try:
            self.mariadb_interface: mariadb.Connection = mariadb.connect(user=self.user, password=self.password,
                            host=self.host, port=self.port, database=self.database, connect_timeout=5)
            return self
        except mariadb.Error as err:   
            logger.error(f'Возникла ошибка при создании объекта SMariaDB: {err}')
            raise err

    def __exit__(self, exc_type, exc, tb):
        try:
            if hasattr(self, 'mariadb_interface') and self.mariadb_interface:
                self.mariadb_interface.close() # закрываем соединение с mariadb при уничтожении объекта класса
        except Exception as error:
            logger.error(f'Возникла ошибка при удалении объекта SMariaDB {error}')
            return False

    def query_get_post(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Получение поста с изображениями по ID
        """
        try:
            with self.mariadb_interface.cursor(dictionary=True) as cursor:
                cursor.execute('''
                    SELECT 
                        p.id, 
                        p.title, 
                        p.creation_date, 
                        p.text,
                        p.author, 
                        i.id AS image_id,
                        i.url
                    FROM posts p 
                    LEFT JOIN posts_images pi ON p.id = pi.post_id 
                    LEFT JOIN images i ON pi.image_id = i.id 
                    WHERE p.id = %s
                ''', (id,))  
                
                rows = cursor.fetchall() # возвращает одна запись. Поскольку у одной записи может быть несколько фотографий, то возвращается массив с идентичными поля p,id , p.tittle , p.creation_date и.т.п , но с разным i.binary_data
                if len(rows) == 0:
                    return False # нет такого поста
                return PostInfo(id=rows[0]['id'], title=rows[0]['title'], creation_date=rows[0]['creation_date'].isoformat(),
                        text=rows[0]['text'], author=rows[0]['author'], images=[{'id': row['image_id'], 'image': row['url']} for row in rows])
        except mariadb.Error as e:
            logger.error(f"Ошибка при выполнении запроса для ID {id}: {e}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            return None
    
    def query_get_post_ids(self):
        """
        Получение ID всех постов в БД
        """
        try:
            with self.mariadb_interface.cursor(dictionary=True) as cursor:
                cursor.execute('''
                    SELECT 
                        p.id
                    FROM posts p 
                ''')  
                dict().items()
                rows = cursor.fetchall() # возвращаются идентификаторы постов из базы данных
                return [row.get('id') for row in rows] # возвращаем идентификаторы всех постов
        except mariadb.Error as e:
            logger.error(f"Ошибка при выполнении запроса для ID {id}: {e}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            return None