from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,TextAreaField,FileField,IntegerField,DateField,SelectField,SelectMultipleField
from wtforms.validators import DataRequired,ValidationError
from app.models import Admin, Tag, Auth


class LoginForm(FlaskForm):
    '''管理员登录表单验证'''
    account=StringField(
        label='账号',
        validators=[DataRequired('请输入账号！')],
        description='账号',
        render_kw={
            "class":"form-control",
            "placeholder":"请输入账号!",
            "required":False,
            }
        )
    pwd=PasswordField(
        label='密码',
        validators=[DataRequired('请输入密码！')],
        description='密码',
        render_kw={
            "class":"form-control",
            "placeholder":"请输入密码!",
            "required":False,
            }
        )
    submit=SubmitField(
        label='登录',
        render_kw={
            "class":"btn btn-primary btn-block btn-flat",
            }
        )

    def validate_account(self,field):
        account=field.data
        admin=Admin.query.filter_by(name=account).count()
        if admin==0:
            raise ValidationError('账号不存在!')
        

class TagForm(FlaskForm):
    '''标签表单验证'''
    name=StringField(
        label='标签名称',
        validators=[DataRequired('请输入标签名称！')],
        description='标签名称',
        render_kw={
            'class':'form-control',
            'id':'input_name',
            'placeholder':'请输入标签名称! ',
            "required": False,
        }
        )
    submit=SubmitField(
        label='添加/编辑',
        render_kw={
            'class':"btn btn-primary"
        }
    )

class MovieForm(FlaskForm):
    '''电影表单验证'''
    title=StringField(
        label='片名',
        validators=[DataRequired('请输入片名！')],
        description='片名',
        render_kw={'class':"form-control",'id':"input_title",'placeholder':"请输入片名！",'required':False}
    )
    url=FileField(
        label='文件',
        validators=[DataRequired('选择文件')],
        description='电影文件',
        render_kw={'id':"input_url",'required':False}
    )
    info=TextAreaField(
        label='简介',
        validators=[DataRequired('请输入介绍！')],
        description='简介',
        render_kw={'class':"form-control", 'rows':"10",'id':"input_info",'required':False}
    )
    logo=FileField(
        label='封面',
        validators=[DataRequired('上传封面！')],
        description='封面',
        render_kw={'id':"input_logo",'required':False}
    )
    star=SelectField(
        label='星级',
        validators=[DataRequired('请选择星级!')],
        description='星级',
        coerce=int,
        choices=[(1, "1星"), (2, "2星"), (3, "3星"), (4, "4星"), (5, "5星")],
        render_kw={'class':"form-control",'id':"input_star",'required':False}
    )
    tag=SelectField(
        label='标签',
        validators=[DataRequired('请选择标签！')],
        coerce=int,
        # 通过列表生成器生成列表
        choices=[(v.id, v.name) for v in Tag.query.all()],
        description='标签',
        render_kw={'class':"form-control",'id':"input_tag_id",'required':False}
    )
    area=StringField(
        label='区域',
        validators=[DataRequired('请输入区域!')],
        description='区域',
        render_kw={'class':"form-control",'id':"input_area",'placeholder':"请输入地区！",'required':False}
    )
    length=StringField(
        label='片长',
        validators=[DataRequired('请输入片长!')],
        description='片长',
        render_kw={'class':"form-control",'id':"input_length",'placeholder':"请输入片长！",'required':False}
    )
    release_time=StringField(
        label='上映时间',
        validators=[DataRequired('请选择上映时间!')],
        description='上映时间',
        render_kw={'class':"form-control",'id':"input_release_time",'placeholder':"请选择上映时间！",'required':False}
    )
    submit=SubmitField(
        '添加/编辑',
        render_kw={'class':"btn btn-primary"}
    )


class PreviewForm(FlaskForm):
    '''电影预告表单验证'''
    title=StringField(
        label='预告标题',
        validators=[DataRequired('请输入预告标题')],
        description='预告标题',
        render_kw={'class':"form-control", 'id':"input_title", 'placeholder':"请输入预告标题！",'required':False}
    )
    logo=FileField(
        label='预告封面',
        validators=[DataRequired("请选择预告封面！")],
        description='预告封面',
        render_kw={'id':"input_logo",'placeholder':"请输入预告封面！",'required':False}
    )
    submit=SubmitField(
        '添加',
        render_kw={'class':"btn btn-primary"}
    )


class AuthForm(FlaskForm):
    '''权限添加表单验证'''
    name=StringField(
        label='权限名称',
        validators=[DataRequired('请输入权限名称！')],
        description='权限名称',
        render_kw={'class':"form-control", 'id':"input_name", 'placeholder':"请输入权限名称！",'required':False}
    )
    url=StringField(
        label='权限地址',
        validators=[DataRequired('请输入权限地址！')],
        description='权限地址',
        render_kw={'class':"form-control", 'id':"input_url", 'placeholder':"请输入权限地址！",'required':False}
    )
    submit=SubmitField(
        '添加/编辑',
        render_kw={'class':"btn btn-primary",'required':False}
    )


# 自定义checbox类
class CheckboxField(SelectMultipleField):
    from wtforms.widgets import ListWidget, CheckboxInput
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
class RoleForm(FlaskForm):
    '''角色表单验证'''
    name=StringField(
        label='角色名称',
        validators=[DataRequired('请输入角色名称！')],
        description='角色名称',
        render_kw={'class':"form-control", 'id':"input_name",'placeholder':"请输入角色名称！",'required':False}
    )

    auths=CheckboxField(
        label='权限',
        validators=[DataRequired('请选择权限！')],
        coerce=int,
        # 通过列表生成器生成列表
        choices=[(v.id, v.name) for v in Auth.query.all()],
        description='权限',
        render_kw={'name':"input_url",'required':False}
    )

    submit=SubmitField(
        '添加/编辑',
        render_kw={'class':"btn btn-primary"}
    )



