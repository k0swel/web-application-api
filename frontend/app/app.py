import random
from flask import Flask, render_template
from dataclasses import dataclass, asdict
import httpx
from modules import images
from dotenv import load_dotenv
import os
from json import loads
from modules.posts import PostInfo
from datetime import datetime

app = Flask(__name__)
application = app


@app.route('/')
def index():
    return render_template('index.html', title="Лабораторная работа №1 by Leonenko Roman")

@app.route('/posts')
def posts():
    request_get_post_ids: httpx.Response = httpx.get(f'{os.environ["API_DOMAIN"]}/get_post_ids')
    ids: list[str] = loads(request_get_post_ids.text)
    posts: list[list] = list()
    for id in ids:
        post_responce_from_api: dict = loads(httpx.get(f'{os.environ["API_DOMAIN"]}/get_post?post_id={id}').text)
        post: PostInfo = PostInfo(id=post_responce_from_api['id'], title=post_responce_from_api['title'], creation_date=datetime.fromisoformat(post_responce_from_api['creation_date']),
                 text=post_responce_from_api['text'], images=post_responce_from_api['images'], author=post_responce_from_api['author'])
        posts.append(asdict(post))
    posts.sort(key=lambda item: item['creation_date'], reverse=True)
    print(posts)
    return render_template('posts.html', title='Посты', posts=posts)

@app.route('/posts/<int:index>')
def post(index):
    post: dict = loads(httpx.get(f'{os.environ["API_DOMAIN"]}/get_post', params={'post_id': index}).text)
    print(post)
    post['avatar_path'] = images.AvatarImage().get_random_image_path()

    comments = [
        {
            'author': 'Иван Иванов',
            'avatar': images.AvatarImage().get_random_image_path(),
            'date': '10.03.2026',
            'text': 'Отличная статья! Очень познавательно.',
            'replies': [
                {
                    'author': post.get('author', 'Автор'),
                    'avatar': post['avatar_path'],
                    'date': '10.03.2026',
                    'text': 'Спасибо за отзыв!',
                },
            ],
        },
        {
            'author': 'Мария Петрова',
            'avatar': images.AvatarImage().get_random_image_path(),
            'date': '11.03.2026',
            'text': 'Интересно, хотелось бы увидеть продолжение на эту тему.',
            'replies': [],
        },
        {
            'author': 'Алексей Сидоров',
            'avatar': images.AvatarImage().get_random_image_path(),
            'date': '12.03.2026',
            'text': 'Полностью согласен с автором. Добавлю, что тема очень актуальна в наше время.',
            'replies': [
                {
                    'author': 'Иван Иванов',
                    'avatar': images.AvatarImage().get_random_image_path(),
                    'date': '12.03.2026',
                    'text': 'Согласен, ждём новых постов!',
                },
                {
                    'author': post.get('author', 'Автор'),
                    'avatar': post['avatar_path'],
                    'date': '13.03.2026',
                    'text': 'Обязательно будут новые материалы. Следите за обновлениями!',
                },
            ],
        },
    ]

    return render_template('post.html', post=post, comments=comments)

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')

if __name__ == '__main__':
    app.run()
