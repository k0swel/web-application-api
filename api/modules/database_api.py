import mariadb
import os
from typing import Dict, Optional, Any
from datetime import datetime
from logger import logger
from modules.dataclass_db import PostInfo, CommentInfo

class SMariaDB():
    def __init__(self, database: str, user: str = os.environ['MARIADB_USER'], password: str = os.environ['MARIADB_ROOT_PASSWORD'],
                 host: str = os.environ['MARIADB_HOST'], port: int = int(os.environ['MARIADB_PORT'])):
        self.user: str = user
        self.password: str = password
        self.host: str = host
        self.port: int = port
        self.database: str = database
        self._probe_connect_to_database() # пробуем подключиться к базе данных
        
    def _probe_connect_to_database(self) -> 'SMariaDB':
        """Функция для пробного подключения к базе данных
        
        Returns:
            SMariaDB: возвращает экземпляр класса для цепочки вызовов
            
        Raises:
            mariadb.Error: пробрасывает ошибку подключения после логирования
        """
        try:
            self.mariadb_interface: mariadb.Connection = mariadb.connect(
                user=self.user, 
                password=self.password,
                host=self.host, 
                port=self.port, 
                database=self.database, 
                connect_timeout=5
            )
            logger.debug(f"Подключение к базе данных mariadb на сеть {self.host}:{self.port} произошло успешно")
                        
        except mariadb.OperationalError as err:
            logger.critical(f'Сервер MariaDB по адресу {self.host}:{self.port} недоступен')
            exit(-1)
    
    def __enter__(self):
        # подключаемся к mariadb при инициализации объекта класса SMariaDB
        try:
            self.mariadb_interface: mariadb.Connection = mariadb.connect(user=self.user, password=self.password,
                            host=self.host, port=self.port, database=self.database, connect_timeout=5)
            logger.debug(f"Подключение к базе данных mariadb на сеть {self.host}:{self.port} произошло успешно")
            return self
        except mariadb.Error as err:   
            logger.error(f'Возникла ошибка при создании объекта SMariaDB: {err}')
            raise err
            exit(1)

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
    
    def query_get_comments(self, post_id: int) -> list:
        """
        Получение всех комментариев поста с вложенными ответами
        """
        try:
            with self.mariadb_interface.cursor(dictionary=True) as cursor:
                cursor.execute('''
                    SELECT
                        id,
                        post_id,
                        parent_id,
                        author,
                        text,
                        creation_date
                    FROM comments
                    WHERE post_id = %s
                    ORDER BY parent_id ASC, creation_date ASC
                ''', (post_id,))
                rows = cursor.fetchall()

            # Строим дерево комментариев
            by_id: dict[int, CommentInfo] = {}
            roots: list[CommentInfo] = []

            for row in rows:
                comment = CommentInfo(
                    id=row['id'],
                    post_id=row['post_id'],
                    parent_id=row['parent_id'],
                    author=row['author'],
                    text=row['text'],
                    creation_date=row['creation_date'].isoformat(),
                )
                by_id[comment.id] = comment

            for comment in by_id.values():
                if comment.parent_id is None:
                    roots.append(comment)
                elif comment.parent_id in by_id:
                    by_id[comment.parent_id].replies.append(comment)

            from dataclasses import asdict
            return [asdict(c) for c in roots]
        except mariadb.Error as e:
            logger.error(f"Ошибка при получении комментариев для поста {post_id}: {e}")
            return []

    def query_add_comment(self, post_id: int, author: str, text: str, parent_id: int | None = None) -> bool:
        """
        Добавление комментария к посту
        """
        try:
            with self.mariadb_interface.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO comments (post_id, parent_id, author, text)
                    VALUES (%s, %s, %s, %s)
                ''', (post_id, parent_id, author, text))
                self.mariadb_interface.commit()
                return True
        except mariadb.Error as e:
            logger.error(f"Ошибка при добавлении комментария к посту {post_id}: {e}")
            return False

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