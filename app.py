# -*- coding: utf-8 -*-
import os
import sys
import click
from flask import Flask, render_template  # render_template()渲染模板 模板文件路径，内部变量
from flask import url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'    # 设置签名密钥，等同于 app.secret_key = 'dev

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
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title)>60:
            flash('Invalid input.')    # 显示错误信息
            return redirect(url_for('index'))   # 重定向回主页
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created')
        return  redirect(url_for('index'))

    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', user=user, movies=movies)


# 上下文处理 变量在所有模板中可见
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)

# 错误页面模板
@app.errorhandler(404)
def page_not_found(e):
    user = User.query.first()
    return render_template('404.html'), 404  # 返回模板和状态码

# 编辑页面
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')  # 显示错误信息
            return redirect(url_for('index'))  # 重定向回主页
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item created')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)


# 删除条目
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


"""URL 解析"""
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
