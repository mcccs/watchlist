# -*- coding: utf-8 -*-
import os
import sys
import click
from flask import Flask, render_template  # render_template()渲染模板 模板文件路径，内部变量
from flask import url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


"""
数据库
"""


# 创建数据模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)    # 主键
    name = db.Column(db.String(20))                 # 名字


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))                 # 电影标题
    year = db.Column(db.String(4))                  # 年份


@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:    # 判断是否输入选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')     # 输出提示信息


@app.cli.command()
def forge():
    """产生虚拟数据"""
    db.create_all()
    # 全局的两个变量移动到这个函数内
    name = 'Lemon'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done.')



"""主页"""


@app.route('/')
def index():
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', user=user, movies=movies)


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
