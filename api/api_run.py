from dotenv import load_dotenv
load_dotenv()

from flask import Flask, make_response , request , jsonify
from http import HTTPStatus
from modules import database_api
from modules import dataclass_db
from dataclasses import asdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from logger import logger
flask_api: Flask = Flask(__name__)
database_api_var: database_api.SMariaDB = database_api.SMariaDB('blog')

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
    print('huuuuuy', post_ids)
    return jsonify(post_ids), HTTPStatus.OK


@flask_api.route('/api/add_comment', methods=['POST'])
def add_comment_to_database():
    data: dict = request.get_json()
    post_id: int = data.get('post_id')
    author: str = data.get('author')
    text: str = data.get('text')
    parent_id: int | None = data.get('parent_id')
    if not post_id or not author or not text:
        return jsonify({'error': 'post_id, author and text are required'}), HTTPStatus.BAD_REQUEST
    logger.info(f'New request {request.base_url}')
    with database_api_var as query:
        success: bool = query.query_add_comment(post_id, author, text, parent_id)
    if not success:
        return jsonify({'error': 'Failed to save comment'}), HTTPStatus.INTERNAL_SERVER_ERROR
    return jsonify({'status': 'ok'}), HTTPStatus.CREATED


@flask_api.route('/api/get_comments', methods=['GET'])
def get_comments_from_database():
    post_id: int = request.args.get('post_id', type=int)
    logger.info(f'New request {request.base_url}')
    if post_id is None:
        return jsonify({'error': 'post_id is required'}), HTTPStatus.BAD_REQUEST
    with database_api_var as query:
        comments: list = query.query_get_comments(post_id)
    return jsonify(comments), HTTPStatus.OK


if __name__ == '__main__':
    flask_api.run(port=3232)