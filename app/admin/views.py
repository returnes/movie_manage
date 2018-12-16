import os

from . import admin
from flask import render_template, redirect, url_for, session, request, flash
from app.admin.forms import LoginForm,TagForm,MovieForm,PreviewForm
from app.models import Admin, Tag, db, Oplog, Movie,Preview
from functools import wraps
from werkzeug.utils import secure_filename
from app import app
from datetime import datetime
import uuid


def change_filename(filename):
    fileinfo=os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename

def admin_login_req(f):
    '''登录装饰器'''

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# 主界面
@admin.route('/')
@admin_login_req
def index():
    return render_template('admin/index.html')


# 登录
@admin.route('/login', methods=["GET", "POST"])
# @admin_login_req
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data['account']).first()
        if not admin.check_pwd(data['pwd']):
            flash('密码错误.', 'err')
            return redirect(url_for('admin.login'))
        session['admin'] = data['account']
        return redirect(request.args.get('next') or url_for('admin.index'))
    return render_template('admin/login.html', form=form)


# 登出
@admin.route('/logout')
@admin_login_req
def logout():
    session.pop('account', None)
    return redirect(url_for('admin.login'))


# 修改密码
@admin.route('/pwd')
@admin_login_req
def pwd():
    return render_template('admin/pwd.html')


# 标签添加
@admin.route('/tag/add',methods=['GET','POST'])
@admin_login_req
def tag_add():
    form=TagForm()
    if form.validate_on_submit():
        data=form.data
        tag=Tag.query.filter_by(name=data['name']).count()
        if tag==1:
            flash('标签已经存在','err')
            return redirect(url_for('admin.tag_add'))
        tag=Tag(
            name=data['name']
        )
        db.session.add(tag)
        db.session.commit()
        # oplog=Oplog(
        #     admin_id=session['admin'],
        #     ip=request.remote_addr,
        #     reason='添加标签%s'%data['name']
        # )
        # db.session.add(oplog)
        # db.session.commit()
        flash('添加成功','ok')
        redirect(url_for('admin.tag_add'))
    return render_template('admin/tag_add.html',form=form)


# 标签列表
@admin.route('/tag/list/<int:page>',methods=["GET"])
@admin_login_req
def tag_list(page=None):
    page_data=Tag.query.order_by(Tag.addtime.desc())
    page_data=page_data.paginate(page=page,per_page=3) #分页
    return render_template('admin/tag_list.html',page_data=page_data)


# 标签删除
@admin.route('/tag/del/<int:id>',methods=["GET"])
@admin_login_req
def tag_del(id=None):
    tag=Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash('标签删除成功','ok')
    return redirect(url_for('admin.tag_list',page=1))
# 标签编辑
@admin.route('/tag/edit/<int:id>',methods=["GET","POST"])
@admin_login_req
def tag_edit(id=None):
    form = TagForm()
    tag=Tag.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data['name']).count()
        if tag.name!=data['name'] and tag_count == 1:
            flash('名称已经存在', 'err')
            return redirect(url_for('admin.tag_edit',id=id))
        tag.name=data['name']
        db.session.add(tag)
        db.session.commit()
        flash('编辑成功', 'ok')
        redirect(url_for('admin.tag_edit',id=id))
    return render_template('admin/tag_edit.html', form=form,tag=tag)

# 电影添加
@admin.route('/movie/add',methods=['GET','POST'])
@admin_login_req
def movie_add():

    form=MovieForm()
    if form.validate_on_submit():
        data=form.data
        file_url=secure_filename(form.url.data)
        file_logo=secure_filename(form.logo.data)
        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'],'rw')
        url=change_filename(file_url)
        logo=change_filename(file_logo)
        # --------------------错误---------------
        # form.url.data.save(app.config["UP_DIR"] + url)
        # form.logo.data.save(app.config["UP_DIR"] + logo)
        movie=Movie(
            title=data['title'],
            url=url,
            info=data['info'],
            logo=logo,
            star=data['star'],
            playnum=0,
            commentnum=0,
            tag_id=data['tag'],
            area=data['area'],
            length=data['length'],
            release_time=data['release_time'],
        )
        try:
            db.session.add(movie)
            db.session.commit()
            flash('添加成功！','ok')
        except Exception as e:
            db.session.rollback()
            flash('请不要重复添加!','err')
        redirect(url_for('admin.movie_add'))
    return render_template('admin/movie_add.html',form=form)


# 电影列表
@admin.route('/movie/list/<int:page>',methods=['GET'])
@admin_login_req
def movie_list(page=1):
    page_data=Movie.query.join(Tag).filter(Tag.id==Movie.tag_id).order_by(
        Movie.addtime.desc()).paginate(page=page,per_page=2)
    return render_template('admin/movie_list.html',page_data=page_data)


# 预告添加
@admin.route('/preview/add',methods=['GET','POST'])
def preview_add():
    form=PreviewForm()
    if form.validate_on_submit():
        data=form.data
        file_logo=secure_filename(form.logo.data) #获取文件名
        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'],'rw')
        logo=change_filename(file_logo)
        file_data=form.logo
        print(type(file_data),file_data)
        file_data.save(app.config['UP_DIR']+logo)
        # form.logo.data.save(app.config['UP_DIR']+logo)
        preview=Preview(
            title=data['title'],
            logo=logo
        )
        try:
            db.session.add(preview)
            db.session.commit()
            flash('添加成功','ok')
        except Exception as e:
            db.session.rollback()
            flash('请不要重复添加','err')
        redirect(url_for('admin.preview_add'))
    return render_template('admin/preview_add.html',form=form)


# 预告列表
@admin.route('/preview/list/<int:page>')
@admin_login_req
def preview_list(page=1):
    previews=Preview.query.order_by(Preview.addtime.desc()).paginate(page=page,per_page=2)
    return render_template('admin/preview_list.html',previews=previews)


# 会员列表
@admin.route('/user/list')
@admin_login_req
def user_list():
    return render_template('admin/user_list.html')


# 会员查看
@admin.route('/user/view')
@admin_login_req
def user_view():
    return render_template('admin/user_view.html')


# 评论列表
@admin.route('/comment/list')
@admin_login_req
def comment_list():
    return render_template('admin/comment_list.html')


# 收藏列表
@admin.route('/moviecol/list')
@admin_login_req
def moviecol_list():
    return render_template('admin/moviecol_list.html')


# 操作日志列表
@admin.route('/oplog/list')
@admin_login_req
def oplog_list():
    return render_template('admin/oplog_list.html')


# 管理员登录日志列表
@admin.route('/adminloginlog/list')
@admin_login_req
def adminloginlog_list():
    return render_template('admin/adminloginlog_list.html')


# 会员登录日志列表
@admin.route('/userloginlog/list')
@admin_login_req
def userloginlog_list():
    return render_template('admin/userloginlog_list.html')


# 权限添加
@admin.route('/auth/add')
@admin_login_req
def auth_add():
    return render_template('admin/auth_add.html')


# 权限列表
@admin.route('/auth/list')
@admin_login_req
def auth_list():
    return render_template('admin/auth_list.html')


# 角色添加
@admin.route('/role/add')
@admin_login_req
def role_add():
    return render_template('admin/role_add.html')


# 角色列表
@admin.route('/role/list')
@admin_login_req
def role_list():
    return render_template('admin/role_list.html')


# 管理员添加
@admin.route('/admin/add')
@admin_login_req
def admin_add():
    return render_template('admin/admin_add.html')


# 管理员列表
@admin.route('/admin/list')
@admin_login_req
def admin_list():
    return render_template('admin/admin_list.html')
