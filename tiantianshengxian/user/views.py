from django.shortcuts import render, redirect
import re
from user.models import User
from django.views.generic import View
import random
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse, HttpResponseRedirect, response, cookie
from itsdangerous import TimedJSONWebSignatureSerializer as Serillizer, SignatureExpired, BadTimeSignature
from django.core.mail import send_mail
from  tiantianshengxian import settings
from django.core.urlresolvers import reverse

from db.tasks import task_send_mail
from django.contrib.auth import authenticate, login
from db.user_util import LoginRequiredMixin


def index(request):
    return render(request, 'index.html')


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        user_name = request.POST.get('user_name')
        user_pwd = request.POST.get('pwd')
        user_cpwd = request.POST.get('cpwd')
        user_email = request.POST.get('email')
        user_allow = request.POST.get('allow')

        # 进行数据检验

        if not all([user_name, user_pwd, user_cpwd, user_email, user_allow]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 检验用户名是否重复delete_cookie
        try:
            user = User.objects.get(username=user_name)
        except User.DoesNotExist:
            user = None

        if user:
            # 用户名已经存在
            return render(request, 'register.html', {'errmsg': '用户名已经存在'})

        if len(user_pwd) > 20 and len(user_pwd) < 8:
            return render(request, 'register.html', {'errmsg': '密码格式错误'})

        # 邮箱验证
        if not re.match(r'[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', user_email):
            return render(request, 'register.html', {'errmsg': '邮箱格式错误'})

        # 同意协议
        if user_allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 进行业务处理：进行用户注册
        print(111)
        user = User.objects.create_user(user_name, user_email, user_pwd)
        user.is_active = 0
        user.save()
        print(222)
        # 发送邮件
        serializer = Serillizer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info).decode()
        encryption_url = 'http://192.168.12.197:8000/active/%s' % token
        print(333)
        # 发邮件
        subject = '正道本正欢迎您'  # 主题
        message = ''  # 文本内容
        sender = settings.EMAIL_FROM
        receiver = [user_email]
        html_message = "欢迎您成为正道本正的客户，请点击下面链接激活账户<hr><a href='%s'>%s</a>" % (encryption_url, encryption_url)
        print(444)
        task_send_mail.delay(subject, message, sender, receiver, html_message)
        print(7777)

        # 返回应答，跳转到首页
        return render(request, 'login.html')


class ActiveView(View):
    """用户激活"""

    def get(self, request, token):
        print(token)
        serializer = Serillizer(settings.SECRET_KEY, 3600)

        try:
            info = serializer.loads(token)
            # 获取激活用户的ID
            user_id = info['confirm']
            # 根据ID获得用户的信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录页面
            return render(request, 'login.html')
        except SignatureExpired as e:
            # 激活过期
            return HttpResponse('激活已经过期')
        except BadTimeSignature as e:
            return HttpResponse('激活链接非法')


class LoginView(View):
    def get(self, request):
        # 判断是否记住用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'

        else:
            username = ''
            checked = ''
        return render(request, 'login.html')

    def post(self, request):
        user_name = request.POST.get('username')
        user_pwd = request.POST.get('pwd')

        user = authenticate(username=user_name, password=user_pwd)
        print(user)
        if user is not None:
            # the password verified for the user
            if user.is_active:
                print("用户是有效的、主动的和经过身份验证的")
                # 记住用户名的登录状态
                login(request, user)

                url_next = request.GET.get('next')

                if url_next:
                    response = redirect(url_next)
                else:
                    response = redirect(reverse('user:index'))

                # 判断是否记住用户名
                remermber = request.POST.get('remember')

                if remermber == 'on':
                    # 记住用户名
                    response.set_cookie('username', user_name, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie('username')
            else:
                print("密码是有效的，但是帐号已经被禁用了！")

            return response
        else:
            # the authentication system was unable to verify the username and password
            print("用户名和密码不正确。")

            return render(request, 'login.html', {'errmsg': '账户未激活'})


def validate_code(request):
    # 定义变量，用于画面的背景色、宽、高
    bgcolor = (random.randrange(20, 100), random.randrange(20, 100), 255)
    width = 100
    height = 25
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    print(rand_str)
    # 验证码保存到数据库
    request.session['validate_code'] = rand_str
    # 构造字体对象
    font = ImageFont.truetype('FreeMono.ttf', 23)
    # 构造字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制4个字
    for i in range(4):
        draw.text((5 + i * 20, 2), rand_str[i], font=font, fill=fontcolor)

    # 释放画笔
    del draw
    # 存入session，用于做进一步验证
    request.session['verifycode'] = rand_str
    # 内存文件操作
    from io import BytesIO
    buf = BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')


class InfoView(LoginRequiredMixin, View):
    def get(self, request):
        context = {'page': '1'}
        return render(request, 'user_center_info.html', context)


class OrderView(LoginRequiredMixin, View):
    def get(self, request):
        context = {'page': '2'}
        return render(request, 'user_center_order.html', context)


class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        context = {'page': '3'}
        return render(request, 'user_center_site.html', context)
