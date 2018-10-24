from django.shortcuts import render, redirect
import re
from user.models import *
from django.views.generic import View
import random
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse, HttpResponseRedirect, response, cookie, JsonResponse
from itsdangerous import TimedJSONWebSignatureSerializer as Serillizer, SignatureExpired, BadTimeSignature
from django.core.mail import send_mail
from  tiantianshengxian import settings
from django.core.urlresolvers import reverse
from django.core import serializers

from db.tasks import task_send_mail
from django.contrib.auth import authenticate, login, logout
from db.user_util import LoginRequiredMixin
from redis import StrictRedis


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

        if user_name == "":

            return render(request, 'register.html', {'errmsg': '用户名必填'})
        elif not 6 <= len(user_name) <= 10:

            return render(request, 'register.html', {'errmsg': '用户名长度必须是6-10位'})

            # 用户名已经存在
        elif user:
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
            # def post(self, request):
            #     # 获取属性
            #
            #
            #     validate = request.POST.get("validate_code", '').strip()
            #     print(validate)
            #     # 判断验证码
            #     if validate != request.session.get('validate_code'):
            #         print(request.session.get('validate_code'))
            #         return HttpResponseRedirect(reverse("user:login"))
            #
            #     user_name = request.POST.get("user_name").strip()
            #     user_pwd = request.POST.get("user_pwd").strip()
            #     remember = request.POST.get("remember")
            #
            #     user = User.objects.filter(name=user_name, pwd=user_pwd)
            #
            #     # 查询
            #     if len(user) != 0:
            #         # 保存到ｓｅｓｓｉｏｎ
            #         request.session['login_user_id'] = user[0].id
            #
            #         # 判断是否跳转到上一次的页面
            #         url_dest = request.COOKIES.get("url_dest")
            #         if url_dest:
            #             resp = HttpResponseRedirect(url_dest)
            #             resp.delete_cookie("url_dest")
            #         else:
            #             resp = HttpResponseRedirect(reverse("book:index"))
            #
            #         if remember == "1":
            #             resp.set_cookie("remember_user_name", user_name, 3600 * 24 * 7)
            #         else:
            #             resp.set_cookie("remember_user_name", user_name, 0)
            #         # 转发
            #         # return book_views.index(request)
            #
            #         # 重定向
            #         return render(request, 'index.html')
            #
            #     else:
            #         return render(request, 'login.html')


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
    # 用户中心信息

    def get(self, request):
        # 获取登录用户对应USER对象
        user = request.user

        # 获取用户的收货地址
        try:
            address = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            # 不存在默认收货地址
            address = None

        # 读取历史记录
        coon = StrictRedis('192.12.168.197')
        history = coon.lrange('history_%d' % user.id, 0, -1)  # 数据字典

        context = {
            'page': '1',
            'address': address,

        }

        # 渲染

        return render(request, 'user_center_info.html', context)


class OrderView(LoginRequiredMixin, View):
    # 用户中心信息

    def get(self, request):
        # 获取登录用户对应USER对象
        user = request.user

        # 获取用户的收货地址
        try:
            address = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            # 不存在默认收货地址
            address = None
        # 数据字典
        context = {
            'page': '2',
            'address': address,

        }

        # 渲染
        return render(request, 'user_center_order.html', context)


class AddressView(LoginRequiredMixin, View):
    # 用户中心信息

    def get(self, request):
        # 获取登录用户对应USER对象
        user = request.user

        # 获取用户的收货地址
        try:
            address = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            # 不存在默认收货地址
            address = None
        # 数据字典
        context = {
            'page': '3',
            'address': address,

        }

        # 渲染
        return render(request, 'user_center_site.html', context)

    def post(self, request):
        # 地址添加
        # 接收数据
        receiver = request.POST.get('receiver')
        print(receiver)
        addr = request.POST.get('addr')
        print(addr)
        zip_code = request.POST.get('zip_code')
        print(zip_code)
        phone = request.POST.get('phone')
        print(phone)

        # 检验数据
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})

        # # 校验手机号
        # if not re.match(r'^1[3|4|5|7|8][0-9]$', phone):
        #     return render(request, 'user_center_site.html', {'errmsg': '手机格式不正确'})

        # 业务处理：地址添加
        # 用户新添加的地址作为默认收货地址，如果原来有默认地址要取消
        # 获取用户的默认收货地址

        # 获取登录用户对应的USER对象

        user = request.user
        try:
            address = Address.objects.get(user=user, is_default=True)
        except:
            # 不存在默认收货地址
            pass

        # 添加地址
        Address.objects.create(
            user=user,
            receiver=receiver,
            addr=addr,
            zip_code=zip_code,
            phone=phone,
            is_default=True,
        )

        # 返回应答，刷新地址页面
        return redirect(reverse('user:address'))  # get请求方式


def checkusername(request):
    user_name = request.GET.get('user_name')
    if 20 >= len(user_name) >= 5:
        if User.objects.filter(username=user_name).exists():
            return HttpResponse('1')
        else:
            return HttpResponse('0')
    else:
        return HttpResponse('3')


class LogoutView(View):
    # def get(self, request):
    #     logout(request)
    #     return redirect(reverse('user:index'))

    def get(self, request):
        # 清除session
        request.session.flush()
        return redirect(reverse("user:index"))


# 三级联动
# 跳转到show.html
def show(request):
    return render(request, 'show.html')


# 获取所有的省份,转成json
def get_all_province(request):
    province_list = Province.objects.all()
    content = {
        'province_list': serializers.serialize('json', province_list)
    }

    return JsonResponse(content)


# 根据省份的id获取下面的城市,转成json
def get_city_by_pid(request):
    province_id = request.GET.get('province_id')
    print(province_id)
    city_list = City.objects.filter(fatherID=province_id)
    content = {
        'city_list': serializers.serialize('json', city_list)
    }

    return JsonResponse(content)


# 根据城市的id获取下面的区,转成json
def get_area_by_cid(request):
    city_id = request.GET.get('city_id')
    area_list = Area.objects.filter(fatherID=city_id)
    content = {
        'area_list': serializers.serialize('json', area_list)
    }

    return JsonResponse(content)
