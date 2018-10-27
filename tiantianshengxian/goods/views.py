# from django.urls import reverse
from django.views.generic import View
from goods.models import *
from django.core.cache import cache
from django.shortcuts import render
from django.shortcuts import redirect
# from django.core.urlresolvers import reverse
# from django.urls import reverse
from django.core.paginator import Paginator
from redis import StrictRedis
from cart.views import get_cart_count
from django.http import HttpResponse, HttpResponseRedirect


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

            # 获取用户的购物车中的商品数目
            cart_count = get_cart_count(request.user)

            # 组织莫阿坝你上下文
            context = {
                'types': types,
                'goods_banners': goods_banners,
                'promotion_banners': promotion_banners,
                'cart_count': cart_count
            }

            cache.set('cache_index', context, 3600 * 24 * 7)

        # 渲染模板

        return render(request, 'index.html', context)


class DetailView(View):
    # 详情页
    def get(self, request, goods_id):
        try:
            sku = GoodSKU.objects.get(id=goods_id)
            print(sku.id)

        except GoodSKU.DoesNotExist:
            # 商品不存在

            return HttpResponseRedirect(reverse('goods:index'))
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
        # 获取用户的购物车中的商品数目
        cart_count = get_cart_count(request.user)

        # 组织上下文
        content = {
            'sku': sku,
            'types': types,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'same_spu_skus': same_spu_skus
        }

        # 渲染模板
        return render(request, 'detail.html', content)


# 种类id 页码 排序方式
# /list》type——id种类id&page=页码&sort=排序方式
# /list/种类id/页码/排序方式
# /list/种类id/页码？sort=排序方式

class ListView(View):
    # 列表页
    def get(self, request, type_id, page):
        # 显示列表页

        # 获取种类信息
        try:
            type = GoodType.objects.get(id=type_id)
        except GoodType.DoesNotExist:
            # 种类不存在
            return HttpResponseRedirect(reverse('goods:index'))

        # 获取商品的分类信息

        types = GoodType.objects.all()
        # 获取商品的排序方式， 获取商品分类的信息
        # sort=default 按照默认id排序
        # sort=price 按照价格排序
        # sort=hot 按照销量排序
        sort = request.GET.get('sort')

        if sort == 'peice':
            skus = GoodSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodSKU.objects.filter(type=type).order_by('sales')

        else:
            sort = 'default'
            skus = GoodSKU.objects.filter(type=type).order_by('-id')

        # 对数据进行分页
        paginator = Paginator(skus, 1)

        # 获取页面内容
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1

        # 获取低page页的page实例对象
        skus_page = paginator.page(page)

        # todo:进行页码的控制，页面上面最多显示五个页码
        # 1 总页数小于5页，页面上面显示所有页码
        # 2 如果当前页是前三页，显示一到五页
        # 3 如果当前页是后四页，显示后五页
        # 4 其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 获取商品信息
        new_skus = GoodSKU.objects.filter(type=type).order_by('-create_time')[:2]

        # 获取用户的购物车中的商品数目
        cart_count = get_cart_count(request.user)

        # 组织上下文
        context = {
            'type': type,
            'skus_page': skus_page,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'sort': sort,
            'pages': pages
        }

        # 使用模板
        return render(request, 'list.html', context)
