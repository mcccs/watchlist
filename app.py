# -*- coding:utf-8-*-
from flask import Flask, render_template  # render_template()渲染模板 模板文件路径，内部变量
from flask import url_for
app = Flask(__name__)


name = 'Grey Li'
movies = [
    {'title': 'My Neighbor Totoro', 'year': '1988'},
    {'title': 'Dead Poets Society', 'year': '1989'},
    {'title': 'A Perfect World', 'year': '1993'},
    {'title': 'Leon', 'year': '1994'},
    {'title': 'Mahjong', 'year': '1996'},
    {'title': 'Swallowtail Butterfly', 'year': '1996'},
    {'title': 'King of Comedy', 'year': '1999'},
    {'title': 'Devils on the Doorstep', 'year': '1999'},
    {'title': 'WALL-E', 'year': '2008'},
    {'title': 'The Pork of Music', 'year': '2012'},
]


@app.route('/')
@app.route('/hello')
def index():
    return render_template('index.html', name=name, movies=movies)


@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % name


@app.route('/test')
def test_url_for():
    print(url_for('hello'))                     # /hello
    print(url_for('user_page', name='hn'))      # /user/hn
    print(url_for('test_url_for'))              # /test
    print(url_for('test_url_for', num=2))       # test?num=2
    return 'Test page'


if __name__ == '__main__':
    app.run(host='192.168.179.131', port=5000)
