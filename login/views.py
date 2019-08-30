from django.shortcuts import render, redirect
from django.http import HttpRequest
from .models import User, ConfirmString
from .form import UserForm, RegisterForm
import bcrypt
from django.conf import settings
import datetime

# Create your views here.


def index(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'login/index.html')


def login(request):
    if request.session.get('is_login', None): # 不允许重登陆
        return redirect('/index/')
    if request.method == 'POST':
        login_form = UserForm(request.POST)
        message = '请检查填写的内容'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password').encode() # bcrypt密码校验类型转为bytes

            try:
                user = User.objects.get(name=username)
            except:
                message = '用户不存在'
                return render(request, 'login/login.html', locals())

            if not user.has_confirmed:
                message = "该用户还未经过邮件确认"
                return render(request, 'login/ack.html', locals())

            if bcrypt.checkpw(password, user.password.encode()):
                # print(username, password)
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/index/')
            else:
                message = '密码不正确'
                return render(request, 'login/login.html', locals())
        else:
            return render(request, 'login/login.html', locals())

    login_form = UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')

    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        message = '请检查填写的内容'
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')

            if password1 != password2:
                message = '两次输入的密码不同'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已存在'
                    return render(request, 'login/register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已经被注册!'
                    return render(request, 'login/register.html', locals())

                new_user = User()
                new_user.name = username
                new_user.password = bcrypt.hashpw(password1.encode(), bcrypt.gensalt()).decode()
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                make_confirm_string(new_user, email)
                # send_email(email, code)

                message = '请前往邮箱进行确认'

                return render(request, 'login/confirm.html', locals())

        else:
            return render(request, 'login/register.html', locals())
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())


def make_confirm_string(user, email):
    code = bcrypt.hashpw(user.name.encode(), bcrypt.gensalt())
    ConfirmString.objects.create(code=code, user=user)
    send_email(email, code)


def send_email(email, code):

    from django.core.mail import EmailMultiAlternatives

    subject = '来自www.luochen.com的注册确认邮件'

    text_content = '''感谢注册www.luochen.com，这里是落尘的博客和教程站点，专注于Python、Django和机器学习技术的分享！\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.luochen.com</a>，\
                    这里是落尘的博客和教程站点，专注于Python、Django和机器学习技术的分享！</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已过期'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢您, 请使用账号登录'
        return render(request, 'login/confirm.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    request.session.flush()
    return redirect('/login/')


def email_ack(request:HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        user = User.objects.get(name=username)
        make_confirm_string(user, user.email)
        # send_email(email, code)

        message = '请前往邮箱进行确认'

        return render(request, 'login/confirm.html', locals())