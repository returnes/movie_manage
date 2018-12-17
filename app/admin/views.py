import os

from . import admin
from flask import render_template, redirect, url_for, session, request, flash
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, AuthForm, RoleForm
from app.models import Admin, Tag, db, Oplog, Movie, Preview, User, Comment, Moviecol, Auth, Role
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
        return redirect(url_for('admin.tag_add'))
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
        return redirect(url_for('admin.tag_edit',id=id))
    return render_template('admin/tag_edit.html', form=form,tag=tag)

# 电影添加
@admin.route('/movie/add',methods=['GET','POST'])
@admin_login_req
def movie_add():

    form=MovieForm()
    if form.validate_on_submit():
        data=form.data
        file_url=secure_filename(form.url.data.filename)
        file_logo=secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'],'rw')
        url=change_filename(file_url)
        logo=change_filename(file_logo)
        form.url.data.save(app.config["UP_DIR"] + url)
        form.logo.data.save(app.config["UP_DIR"] + logo)
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
        return redirect(url_for('admin.movie_add'))
    return render_template('admin/movie_add.html',form=form)


# 电影列表
@admin.route('/movie/list/<int:page>',methods=['GET'])
@admin_login_req
def movie_list(page=1):
    page_data=Movie.query.join(Tag).filter(Tag.id==Movie.tag_id).order_by(
        Movie.addtime.desc()).paginate(page=page,per_page=2)
    return render_template('admin/movie_list.html',page_data=page_data)

# 电影删除
@admin.route('/movie/del/<int:id>')
@admin_login_req
def movie_del(id):
    movie=Movie.query.get_or_404(id)
    try:
        db.session.delete(movie)
        db.session.commit()
        flash('删除成功','ok')
    except Exception as e:
        db.session.rollback()
        flash('删除失败','err')
    return redirect(url_for('admin.movie_list',page=1))
# 电影编辑
@admin.route('/movie/edit/<int:id>',methods=['POST','GET'])
@admin_login_req
def movie_edit(id=None):
    form=MovieForm()
    movie=Movie.query.get_or_404(id)
    if form.validate_on_submit() and movie:
        data=form.data
        file_logo=secure_filename(form.logo.data.filename)
        file_url=secure_filename(form.url.data.filename)
        logo=change_filename(file_logo)
        url=change_filename(file_url)
        form.logo.data.save(app.config['UP_DIR']+logo)
        form.url.data.save(app.config['UP_DIR']+url)
        movie.title = data['title']
        movie.url = url
        movie.info = data['info']
        movie.logo = logo
        movie.star = data['star']
        movie.tag_id = data['tag']
        movie.area = data['area']
        movie.length = data['length']
        movie.release_time = data['release_time']
        try:
            db.session.commit()
            flash('修改成功','ok')
        except Exception as e:
            db.session.rollback()
            flash('修改失败','err')
        return redirect(url_for('admin.movie_edit',id=id))
    return render_template('admin/movie_edit.html',form=form,movie=movie)

# 预告添加
@admin.route('/preview/add',methods=['GET','POST'])
@admin_login_req
def preview_add():
    form=PreviewForm()
    if form.validate_on_submit():
        data=form.data
        file_logo=secure_filename(form.logo.data.filename) #获取文件名
        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'],'rw')
        logo=change_filename(file_logo)
        form.logo.data.save(app.config['UP_DIR']+logo)
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
        return redirect(url_for('admin.preview_add'))
    return render_template('admin/preview_add.html',form=form)


# 预告列表
@admin.route('/preview/list/<int:page>')
@admin_login_req
def preview_list(page=1):
    previews=Preview.query.order_by(Preview.addtime.desc()).paginate(page=page,per_page=2)
    return render_template('admin/preview_list.html',previews=previews)

# 预告删除
@admin.route('/preview/del/<int:id>')
@admin_login_req
def preview_del(id):
    preview=Preview.query.get_or_404(id)
    try:
        db.session.delete(preview)
        db.session.commit()
        flash('删除成功','ok')
    except Exception as e:
        db.session.rollback()
        flash('删除失败','err')
    return redirect(url_for('admin.preview_list',page=1))

# 预告编辑
@admin.route('/preview/edit/<int:id>',methods=['GET','POST'])
@admin_login_req
def preview_edit(id=None):
    form=PreviewForm()
    preview=Preview.query.get_or_404(id)
    if form.validate_on_submit() and preview:
        data=form.data
        file_logo=secure_filename(form.logo.data.filename)
        logo=change_filename(file_logo)
        form.logo.data.save(app.config['UP_DIR']+logo)
        preview.title=data['title']
        preview.logo=logo
        try:
            db.session.commit()
            flash('保存成功','ok')
        except Exception as e:
            db.session.rollback()
            flash('保存失败','err')
        return redirect(url_for('admin.preview_edit',id=id))
    return render_template('admin/preview_edit.html',form=form,preview=preview)


# 会员列表
@admin.route('/user/list/<int:page>')
@admin_login_req
def user_list(page=1):
    users=User.query.order_by(User.addtime.desc()).paginate(page=page,per_page=2)
    return render_template('admin/user_list.html',users=users)


# 会员查看
@admin.route('/user/view/<int:id>')
@admin_login_req
def user_view(id):
    user=User.query.get_or_404(id)

    return render_template('admin/user_view.html',user=user)

# 会员删除
@admin.route('/user/del/<int:id>')
@admin_login_req
def user_del(id):
    user=User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('删除成功','ok')
    except Exception as e:
        db.session.rollback()
        flash('删除失败','err')
    return redirect(url_for('admin.user_list',page=1))


# 评论列表
@admin.route('/comment/list/<int:page>')
@admin_login_req
def comment_list(page=1):
    comments=Comment.query.join(User).join(Movie).filter(Comment.user_id==User.id,Comment.movie_id==Movie.id).order_by(Comment.addtime.desc()).paginate(page=page,per_page=2)

    return render_template('admin/comment_list.html',comments=comments)


# 评论删除
@admin.route('/comment/del/<int:id>')
@admin_login_req
def comment_del(id):
    comment=Comment.query.get_or_404(id)
    try:
        db.session.delete(comment)
        db.session.commit()
        flash('删除成功','ok')
    except Exception as e:
        db.session.rollback()
        flash('删除失败','err')
    return redirect(url_for('admin.comment_list',page=1))


# 收藏列表
@admin.route('/moviecol/list/<int:page>')
@admin_login_req
def moviecol_list(page=1):
    moviecols=Moviecol.query.join(User).join(Movie).filter(Moviecol.user_id==User.id,Moviecol.movie_id==Movie.id).paginate(page=page,per_page=2)
    return render_template('admin/moviecol_list.html',moviecols=moviecols)
# 删除收藏
@admin.route('/moviecol/del/<int:id>')
@admin_login_req
def moviecol_del(id):
    moviecol=Moviecol.query.get_or_404(id)
    try:
        db.session.delete(moviecol)
        db.session.commit()
        flash('删除成功','ok')
    except Exception as e:
        db.session.rollback()
        flash('删除失败','err')
    return redirect(url_for('admin.moviecol_list',page=1))

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
@admin.route('/auth/add',methods=['GET','POST'])
@admin_login_req
def auth_add():
    form=AuthForm()
    if form.validate_on_submit():
        data=form.data
        counts=Auth.query.filter_by(name=data['name']).count()
        if counts==1:
            flash('已经存在，添加错误','err')
            return redirect(url_for('admin.auth_add'))
        auth=Auth(name=data['name'],url=data['url'])
        try:
            db.session.add(auth)
            db.session.commit()
            flash('添加成功','ok')
        except Exception as e:
            db.session.rollback()
            flash('添加失败','err')
        return redirect(url_for('admin.auth_add'))

    return render_template('admin/auth_add.html',form=form)


# 权限列表
@admin.route('/auth/list/<int:page>')
@admin_login_req
def auth_list(page=1):
    auths=Auth.query.order_by(Auth.addtime.desc()).paginate(page=page,per_page=2)

    return render_template('admin/auth_list.html',auths=auths)

# 权限删除
@admin.route('/auth/del/<int:id>')
@admin_login_req
def auth_del(id=None):
    auth=Auth.query.get_or_404(id)
    if not auth:
        flash('删除失败','err')
    else:
        try:
            db.session.delete(auth)
            db.session.commit()
            flash('删除成功','ok')
        except Exception as e:
            db.session.rollback()
            flash('删除失败','err')
    return redirect(url_for('admin.auth_list',page=1))

# 权限编辑
@admin.route('/auth/edit/<int:id>',methods=['GET','POST'])
@admin_login_req
def auth_edit(id):
    form=AuthForm()
    auth=Auth.query.filter_by(id=id).first()
    if not auth:
        flash('跳转错误','err')
        return redirect(url_for('admin.auth_list'))
    if form.validate_on_submit() and auth:
        data=form.data
        auth.name=data['name']
        auth.url=data['url']
        try:
            db.session.commit()
            flash('修改成功','ok')
        except Exception as e:
            db.session.rollback()
            flash('修改失败','err')
        return redirect(url_for('admin.auth_edit',id=id))
    return render_template('admin/auth_edit.html',form=form,auth=auth)


# 角色添加
@admin.route('/role/add',methods=['GET','POST'])
@admin_login_req
def role_add():
    form=RoleForm()
    if form.validate_on_submit():
        data=form.data
        role=Role.query.filter_by(name=data['name']).first()
        if role:
            flash('已经存在','err')
            return redirect(url_for('admin.role_add'))
        roles=Role(
            name=data['name'],
            # auths=data['auths']
            auths=",".join(map(lambda v: str(v), data["auths"]))
        )
        try:
            db.session.add(roles)
            db.session.commit()
            flash('添加成功','ok')
        except Exception as e:
            db.session.rollback()
        return redirect(url_for('admin.role_add'))
    return render_template('admin/role_add.html',form=form)


# 角色列表
@admin.route('/role/list/<int:page>')
@admin_login_req
def role_list(page=1):
    roles=Role.query.order_by(Role.addtime.desc()).paginate(page=page,per_page=2)
    return render_template('admin/role_list.html',roles=roles)

# 角色删除
@admin.route('/role/del/<int:id>')
@admin_login_req
def role_del(id):
    role=Role.query.get_or_404(id)
    try:
        db.session.delete(role)
        db.session.commit()
        flash('删除成功','ok')
    except Exception as e:
        db.session.rollback()
        flash('删除失败','err')
    return redirect(url_for('admin.role_list',page=1))

# 角色编辑
@admin.route('/role/edit/<int:id>',methods=['GET','POST'])
@admin_login_req
def role_edit(id):
    form=RoleForm()
    role=Role.query.get_or_404(id)
    if request.method=='GET':
        auths=role.auths
        form.auths.data = list(map(lambda v: int(v), auths.split(",")))
    if form.validate_on_submit():
        data=form.data
        role_count=Role.query.filter_by(name=data['name']).count()
        if role.name!=data['name']and role_count==1:
            flash('已经存在','err')
            return redirect(url_for('admin.role_edit',id=id))
        role.name=data['name']
        role.auths=','.join(map(lambda v:str(v),data['auths']))
        try:
            db.session.commit()
            flash('编辑成功','ok')
        except Exception as e:
            db.session.rollback()
            flash('编辑错误','err')
        return redirect(url_for('admin.role_edit',id=id))

    return render_template('admin/role_edit.html',form=form,role=role)

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
