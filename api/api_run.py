from dotenv import load_dotenv
load_dotenv('./.env')

from flask import Flask, make_response , request , jsonify
from http import HTTPStatus
from modules import database_api
from modules import dataclass_db
from dataclasses import asdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from logger import logger, log_query
flask_api: Flask = Flask(__name__)
database_api_var: database_api.SMariaDB = database_api.SMariaDB('posts')

@flask_api.route('/api/get_post', methods=['GET'])
def get_post_from_database():
    post_id: int = request.args.get('post_id', type=int)
    logger.info(f'New request {request.base_url}')
    with database_api_var as query:
        post_data_from_db: dataclass_db.PostInfo = query.query_get_post(post_id)
        if not post_data_from_db: # если пост не найден, возвращаем 404 ошибку
            message: dict = dict()
            message['code_status'] = HTTPStatus.NOT_FOUND
            message['text'] = ' Couldnt find a post with a required ID'
            return jsonify(message), HTTPStatus.NOT_FOUND
        return jsonify(asdict(post_data_from_db)), HTTPStatus.OK # иначе возвращаем пост


@flask_api.route('/api/get_post_ids', methods=['GET'])
def get_post_ids_from_database():
    logger.info(f'New request {request.base_url}')
    with database_api_var as query:
        post_ids: list[int] = query.query_get_post_ids()
    return jsonify(post_ids), HTTPStatus.OK
if __name__ == '__main__':
    flask_api.run(port=3232)