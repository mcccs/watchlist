# -*- coding: utf-8 -*-
import os
import sys
import click
from flask import Flask, render_template  # render_template()渲染模板 模板文件路径，内部变量
from flask import url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash   # 生成和校验密码散列值

from flask_login import LoginManager      # flask-login 提供了实现用户认证需要的各类功能函数
from flask_login import UserMixin
from flask_login import login_user, logout_user         # login_user() 传入用户模型对象
from flask_login import login_required, current_user     # 登出

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'    # 设置签名密钥，等同于 app.secret_key = 'dev

db = SQLAlchemy(app)
login_manager = LoginManager(app)   # 实例化扩展类


"""
数据库
"""


# 创建数据模型
class User(db.Model, UserMixin):                    # 继承UserMixin类，判断当前用户的认真状态
    id = db.Column(db.Integer, primary_key=True)    # 主键
    name = db.Column(db.String(20))                 # 名字
    username = db.Column(db.String(20))             # 用户名
    password_hash = db.Column(db.String(128))       # 密码散列值

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))                 # 电影标题
    year = db.Column(db.String(4))                  # 年份


@app.cli.command()  # 生成数据库 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:    # 判断是否输入选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')     # 输出提示信息


@app.cli.command()  # 创建管理员 # flask admin
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True,
              help='The password used to login')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo("Updating user...")
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')

# 登录管理
@login_manager.user_loader
def load_user(user_id):                     # 创建用户加载回调函数，接受用户ID作为参数
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'login'
# login_manager.login_message = 'Your custom message'

# 登录界面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash("Invalid input.")
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))
    return render_template('login.html')


# 登出
@app.route('/logout')
@login_required     # 视图保护
def logout():
    logout_user()     # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))


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
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
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


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))
    return render_template('settings.html')


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
@login_required    # 登录保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


"""URL 解析"""
@app.route('/user/<name>')
@login_required
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
