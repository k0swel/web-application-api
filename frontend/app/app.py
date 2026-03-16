import random
from flask import Flask, render_template, request, redirect, url_for, abort
from dataclasses import dataclass, asdict
import httpx
from modules import images
from dotenv import load_dotenv
import os
from json import loads
from modules.posts import PostInfo
from datetime import datetime, timedelta

app = Flask(__name__)
application = app

TITLE='Лабораторная работа №1 by Leonenko Roman'

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
        post.creation_date = post.creation_date + timedelta(hours=3)
        posts.append(asdict(post))
    posts.sort(key=lambda item: item['creation_date'], reverse=True)
    for post in posts: post['creation_date'] = post['creation_date'].strftime('%Y-%m-%d %H:%M:%S')
    return render_template('posts.html', title='Посты', posts=posts)

@app.route('/posts/<int:index>')
def post(index):
    response = httpx.get(f'{os.environ["API_DOMAIN"]}/get_post', params={'post_id': index})
    if response.status_code != 200:
        abort(404)
    post: dict = loads(response.text)
    post['avatar_path'] = 'https://avatars.mds.yandex.net/i?id=e263f05efe8c9f9019d8f857f5a2cb9c_sr-4081108-images-thumbs&n=13'

    raw_comments: list = loads(httpx.get(f'{os.environ["API_DOMAIN"]}/get_comments', params={'post_id': index}).text)

    def attach_avatars(comments: list) -> list:
        for comment in comments:
            comment['avatar'] = 'https://avatars.mds.yandex.net/i?id=e263f05efe8c9f9019d8f857f5a2cb9c_sr-4081108-images-thumbs&n=13'
            comment['date'] = (datetime.strptime(comment.get('creation_date', ''), '%Y-%m-%dT%H:%M:%S') + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S') # прибавляем к UTC +3 часа = Moscow
            if comment.get('replies'):
                attach_avatars(comment['replies'])
        return comments

    comments = attach_avatars(raw_comments)
    post['creation_date'] = (datetime.strptime(post['creation_date'], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
    return render_template('post.html', post=post, comments=comments, title=TITLE)

@app.route('/posts/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    author: str = request.form.get('author', '').strip()
    text: str = request.form.get('text', '').strip()
    parent_id: int | None = request.form.get('parent_id', type=int)
    if author and text:
        httpx.post(f'{os.environ["API_DOMAIN"]}/add_comment', json={
            'post_id': post_id,
            'author': author,
            'text': text,
            'parent_id': parent_id,
        })
    return redirect(url_for('post', index=post_id))


@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе', image='https://i.pinimg.com/736x/15/9d/0e/159d0e3950a69324e673429ab6de5ec8.jpg',
                           text='Леоненко Роман 241-3211')

if __name__ == '__main__':
    app.run()
