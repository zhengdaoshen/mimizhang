from django.shortcuts import render
from django.views.generic import View
from goods.models import *


class IndexView(View):
    def get(self, request):
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

        # 渲染模板

        return render(request, 'index.html', context)
