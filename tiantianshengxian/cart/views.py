from django.conf import settings
from goods.models import *
from django.shortcuts import redirect, render
from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect, response, cookie, JsonResponse
from  tiantianshengxian import settings
from db.user_util import LoginRequiredMixin


class CartView(LoginRequiredMixin, View):
    # 购物车记录添加
    def post(self, request):
        user = request.user
        print(1)
        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接搜数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        print(sku_id)
        print(count)

        # 数据检验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        print(2)
        # 检验添加的商品数量
        try:
            count = int(count)
        except Exception as e:
            # 数目出错
            return JsonResponse({'res': 2, 'errmsg': '商品数目出错'})

        # 检验商品是否存在
        try:
            sku = GoodSKU.objects.get(id=sku_id)
        except GoodSKU.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})

        # 业务处理：添加购物车记录
        conn = settings.REDIS_CONN
        cart_key = 'cart_%d' % user.id
        # 先尝试获取水库——id的值>hget——cart——key属性
        # 如果sku—id在hash中不存在，hget放回NONE
        cart_count = conn.hget(cart_key, sku_id)
        print(3)
        if cart_count:
            # 累加购物车中商品的数目
            count += int(cart_count)
        print(4)

        # 检验商品的库存
        if count >= sku.stock:
            print(7)
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})
        print(5)

        # 设置hash中的sku——id对应的值
        # hset>如果sku——id已经存在，更新数据，如果sku——id不存在，添加数据
        conn.hset(cart_key, sku_id, count)

        # 计算用户购物车商品的数目
        total_count = get_cart_count(user)
        print(6)

        # 返回应答
        return JsonResponse({'res': 5, 'errmsg': '添加成功'})


def get_cart_count(user):
    # 获取用的购物商品的总数
    # 保存用户购物车中商品的总数目
    total_count = 0

    if user.is_authenticated():
        # 链接redis
        conn = settings.REDIS_CONN
        # key
        cart_key = 'cart_%d' % user.id
        # 获取信息
        cart_dict = conn.hgetall(cart_key)

        # 遍历获取商品的信息
        for sku_id, count in cart_dict.items():
            total_count += int(count)

        return total_count


class CartCountView(View):
    def get(self, request):
        total_count = get_cart_count(request.user)
        return JsonResponse({'total_count': total_count})


class CartInfoView(LoginRequiredMixin, View):
    # 异步获取购物车总数量
    def get(self, request):
        # 获取登录用户
        user = request.user
        # 获取用户的购物车中的商品信息
        conn = settings.REDIS_CONN
        cart_key = 'cart_%d' % user.id
        # {商品id：商品数量}
        cart_dict = conn.hgetall(cart_key)

        skus = []
        # 保存用户购物车中商品的总数目和总价格
        total_count = 0
        total_price = 0
        # 遍历获取商品信息
        for sku_id, count in cart_dict.items():
            # 根据商品的id获取商品的信息
            sku = GoodSKU.objects.get(id=sku_id)
            # 计算商品的小计
            amount = sku.price * int(count)
            sku.amount = amount
            # 动态sku对象增加一个属性count，保存购物车中对应商品的数量
            sku.count = count
            # 添加
            skus.append(sku)
            # 累计计算商品的照片那个数目和价格
            total_count += int(count)
            total_price += amount

        # 组织上下文
        context = {
            'total_count': total_count,
            'total_price': total_price,
            'skus': skus,

        }

        # 渲染末班
        return render(request, 'cart.html', context)


class CartUpdateView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user

        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接受数据
        sku_id = request.POST.get('sku_id')

        count = request.POST.get('count')

        # 数据检验
        if not all([sku_id, count]):
            print(sku_id)
            print(count)
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

        # 检验添加的商品数量
        try:
            sku = GoodSKU.objects.get(id=sku_id)
        except GoodSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '商品数目出错'})

        # 检验商品是否存在
        try:
            sku = GoodSKU.objects.get(id=sku_id)
        except GoodSKU.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})

        # 业务处理：更新购物车记录
        conn = settings.REDIS_CONN
        cart_key = 'cart_%d' % user.id

        # 检验商品的库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})

        # 更新
        ret2 = conn.hset(cart_key, sku_id, count)
        print(ret2)
        ret = conn.hget(cart_key, sku_id, count)
        print(ret)
        # 计算用户购物车商品的数目
        total_count = get_cart_count(user)

        # 返回应答
        return JsonResponse({'res': 5, 'total': total_count, 'errmsg': '更新成功'})


class CartDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user

        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接受数据
        sku_id = request.POST.get('sku_id')

        # 数据检验
        if not sku_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的商品id'})

        # 检验商品是否存在
        try:
            sku = GoodSKU.objects.get(id=sku_id)
        except GoodSKU.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res': 2, 'errmsg': '商品不存在'})
        # 业务处理：更新购物车记录
        conn = settings.REDIS_CONN
        cart_key = 'cart_%d' % user.id

        # 删除hdel
        conn.hdel(cart_key, sku_id)

        # 计算用户购物车中商品总数
        total_count = get_cart_count(user)

        # 返回应答
        return JsonResponse({'res': 3, 'total': total_count, 'errmsg': '商品不存在'})
