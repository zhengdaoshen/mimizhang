import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tiantianshengxian.settings")
django.setup()
from goods.models import *
from celery import Celery
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template import RequestContext, loader
from tiantianshengxian import settings

app = Celery('db.tasks', broker='redis://192.168.12.197:6379/3')




@app.task
def task_send_mail(subject, message, sender, receiver, html_message):
    send_mail(subject, message, sender, receiver, html_message=html_message)  # 发送


@app.task
def task_generate_static_index():
    # 显示首页
    # 获取商品的种类信息
    types = GoodType.objects.all()

    # 获取首页轮播商品信息
    goods_banners = IndexGoodBanner.objects.all().order_by('index')

    # 获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息
    for type in types:
        # 获取type种类首页分类商品的图片展示信息

        image_banners = IndexTypeGoodBanner.objects.filter(type=type, display_type=1).order_by('index')
        title_banners = IndexTypeGoodBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 动态给type加属性，分别保存首页分类商品的图片展示信息和文字提示信息

        type.image_banners = image_banners
        type.title_banners = title_banners


        # 获取用户的购物车中的商品数目
        # cart_count=0

    # 组织莫阿坝你上下文
    context = {
        'types': types,
        'goods_banners': goods_banners,
        'promotion_banners': promotion_banners,
        'cart_count': 0
    }

    # 使用模板
    # 1：加载模板文件，返回模板对象
    temp = loader.get_template('static_index.html')
    # 2：模板渲染
    static_index_html = temp.render(context)

    # 生成首页对应静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/html/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)

    print('生成首页静态页')
