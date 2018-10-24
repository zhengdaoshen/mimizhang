from django.views.generic import View
from goods.models import *
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from redis import StrictRedis
from django.contrib.auth.models import User
from user.models import *


class IndexView(View):
    def get(self, request):
        context = cache.get('cache_index')

        if context == None:
            print('设置缓存...')
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

            # 组织莫阿坝你上下文
            context = {
                'types': types,
                'goods_banners': goods_banners,
                'promotion_banners': promotion_banners,
                'cart_count': 0
            }

            cache.set('cache_index', context, 3600 * 24 * 7)

        # 获取用户的购物车中的商品数目
        cart_count = 0
        context.update(cart_count=cart_count)

        # 渲染模板

        return render(request, 'index.html', context)


class DetailView(View):
    # 详情页
    def get(self, request, goods_id):
        try:
            sku = GoodSKU.objects.get(id=goods_id)

        except GoodSKU.DoesNotExist:
            # 商品不存在

            return redirect(reverse('goods:index'))
        # 获取商品的分类信息
        types = GoodType.objects.all()

        # 获取商品的评论信息，后期扩展

        # 获取商品信息
        new_skus = GoodSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]

        # 获取同一个SPU的其他规格撒谎嗯品，后期扩展
        same_spu_skus = GoodSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)

        # 如果用户已经登录
        user = request.user

        if user.is_authenticated():
            # 添加用户的历史记录

            # 链接redis
            coon = StrictRedis('192.168.12.197')
            # key
            history_key = 'history_%d' % user.id
            # 移除列表中的goods——id
            coon.lrem(history_key, 0, goods_id)
            # 把good——地插入到列表的左侧
            coon.lpush(history_key, 0, goods_id)
            # 只保存用户最新浏览的五条信息
            coon.ltrim(history_key, 0, 4)
        # 获取用户购物车中的商品数目

        cart_count = 0
        # 组织上下文
        content = {
            'sku': sku,
            'types': types,
            'new_skus': new_skus,
            'cart_count': cart_count
        }

        # 渲染模板
        return render(request, 'detail.html', content)
