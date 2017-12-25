import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, flash,redirect, request, url_for
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo


app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
base_dir = os.path.abspath(os.path.dirname(__file__))
database_uri = 'sqlite:///' + os.path.join(base_dir,'blog.sqlit')
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = 'wwwwwww'
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    account = db.Column(db.String(32),unique=True)
    passwd = db.Column(db.String(32))
class RegForm(FlaskForm):
    account = StringField('用户名',validators=[DataRequired(),Length(6,100,message='用户名长度不少于6位')])
    passwd = PasswordField('密码',validators=[DataRequired(),Length(6,100,message='密码长度不少于6位')])
    password = PasswordField('密码',validators=[EqualTo('passwd')])
    submit = SubmitField('确认注册')
class LogForm(FlaskForm):
    account = StringField('用户名',validators=[DataRequired(),Length(6,100,message='用户名长度不少于6位')])
    passwd = PasswordField('密码',validators=[DataRequired(),Length(6,100,message='密码长度不少于6位')])
    # password = PasswordField('密码',validators=[EqualTo(passwd),Length(6,100,message='密码长度不少于6位')])
    submit = SubmitField('确认登录')

from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from PIL import Image
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.getcwd(),'static/img')
# app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()
photos = UploadSet('photos',IMAGES)
configure_uploads(app,photos)
patch_request_class(app,size=2*1024*1024)
# 文件上传表单
class UploadForm(FlaskForm):
    photo = FileField(validators=[FileRequired(message='未选择文件'),
                      FileAllowed(photos, message='只能上传图片')])
    submit = SubmitField('上传图片')

#生成随机的字符串
def random_string(length=32):
    import random
    base_string = 'asdfghjklqwertyuiopzxcvbnm1234567890'
    return ''.join(random.choice(base_string) for i in range(length))

@app.route('/',methods=['POST','GET'])
def index_html():
    img_url = None
    form = UploadForm()
    if form.validate_on_submit():
        # 生成随机的文件名
        suffix = os.path.splitext(form.photo.data.filename)[1]
        filename = random_string() + suffix
        # 保存上传文件
        photos.save(form.photo.data, name=filename)
        # 生成缩略图
        # pathname = os.path.join(app.config['UPLOADED_PHOTOS_DEST'],filename)
        # 1.打开文件
        # img = Image.open(pathname)
        # 2.设置尺寸
        # img.thumbnail((128, 128))
        # 3.保存修改后的文件
        # img.save(pathname)
        # 获取上传文件的URL
        img_url = photos.url(filename)
    return render_template('index.html',form=form,img_url=img_url)

@app.route('/register/',methods=['GET','POST'])
def register_html():
    form = RegForm()
    if form.validate_on_submit():
        # addUser(form)
        account = form.account.data
        passwd = form.passwd.data
        user = Users.query.all()
        for u in user:
            if u.account == account:
                flash('用户名已存在请重新注册')
                return render_template('register.html',form=form)
        user = Users(account=account,passwd=passwd )
        db.session.add(user)
        flash('注册成功，请登录')
        # return render_template('success.html',context=context)

        return redirect(url_for('login_html'))
    return render_template('register.html',form=form)

@app.route('/login/',methods=['POST','GET'])
def login_html():
    form = LogForm()
    if form.validate_on_submit():
        account = form.account.data
        passwd = form.passwd.data
        user = Users.query.all()
        for u in user:
            if u.account == account and u.passwd == passwd:
                flash('登录成功')
                return redirect('index')
        flash(message='用户名或密码不正确，请重新登录')
    return render_template('login.html', form=form)



#创建数据库
@manager.command
def createdb():
    db.create_all()
    return
if __name__ == '__main__':
    manager.run()
