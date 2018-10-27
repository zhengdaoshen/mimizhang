from django.conf import settings
from goods.models import *
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
# from django.urls import reverse
from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect, response, cookie, JsonResponse
from  tiantianshengxian import settings
from db.user_util import LoginRequiredMixin
from user.models import *
from goods.models import *
from order.models import *
import datetime
from django.db import transaction


class OrderPlaceView(LoginRequiredMixin, View):
    # 提交订单显示页面
    def post(self, request):

        user = request.user
        # 获取参数sku——ids

        sku_ids = request.POST.get('sku_ids')

        # 检验参数
        if not sku_ids:
            # 跳转到购物车页面
            # return HttpResponseRedirect(reverse('cart:show'))
            return redirect(reverse('cart:show'))
        #
        conn = settings.REDIS_CONN
        cart_key = 'cart_%d' % user.id
        print(cart_key)

        skus = []
        # 保存商品的总件数和总价格
        total_count = 0
        total_price = 0

        # 遍历sku，ids获取用户要购买的商品信息
        for sku_id in sku_ids:
            # 根据商品的id获取商品信息
            sku = GoodSKU.objects.get(id=sku_id)
            print(sku_id)
            # 获取用户要够买商品的数量
            count = conn.hget(cart_key, sku_id)

            # 计算商品的小计
            amount = sku.price * int(count)
            print(amount)
            # 动态给sku增加属性amount，保存购买商品的数量
            sku.count = count
            # 动态给sku增加属性amount，保存购买商品的小计
            sku.amount = amount
            # 追加
            skus.append(sku)
            # 累加计算商品的总件数和总价格
            total_count += int(count)
            total_price += amount

        # 运费 实际开发的时候属于一个系统
        transit_peice = 10

        # 实际付款
        total_pay = total_price + transit_peice

        # 获取用户的收件地址
        addrs = Address.objects.filter(user=user)

        # 组织上下文
        sku_ids = ','.join(sku_ids)

        context = {
            'skus': skus,
            'total_count': total_count,
            'total_price': total_price,
            'transit_peice': transit_peice,
            'total_pay': total_pay,
            'addrs': addrs,
            'sku_ids': sku_ids
        }

        # 使用模板
        return render(request, 'place_order.html', context)


class OrderCommitView(LoginRequiredMixin, View):
    @transaction.atomic()
    def post(self, request):
        # 订单创建
        # 判断用户是否登录
        user = request.user
        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接搜数据
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')

        # 检验参数
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})

        # 检验支付方式
        try:
            pay_method = int(pay_method)
        except ValueError:
            return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})

        if pay_method not in dict(OrderInfo.PAY_METHOD_CHOICES).keys():
            return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})

        # 检验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            # 地点不存在
            return JsonResponse({'res': 3, 'errmsg': '地址不存在'})

        # todo : 创建订单核心业务

        # 组织参数
        # 订单ID ：20781122181630+用户ID

        order_id = datetime.datetime.today().strftime('%Y%m%d%H%M%S') + str(user.id)

        # 运费
        transit_price = 10

        # 总数木和总金额
        total_count = 0
        total_price = 0

        try:
            # 设置事物保存点
            save_point = transaction.savepoint()

            # todo : 向df——order——info 表中添加一条记录
            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                addr=addr,
                pay_method=pay_method,
                total_count=total_count,
                total_price=total_price,
                transit_price=transit_price
            )
            # todo 同胡的订单中有几个商品，需要向df——order——goods表中加入几条记录e
            conn = settings.REDIS_CONN
            cart_key = 'cart_%d' % user.id

            sku_ids = sku_ids.split(',')
            for sku_id in sku_ids:
                try:
                    sku = GoodSKU.objects.get(id=sku_id)
                except:
                    # 商品不存在
                    return JsonResponse({'res': 4, 'errmsg': '商品不卒中乃'})

                # 从redis中获取用户所要购买的商品数量
                count = conn.hget(cart_key, sku_id)

                # todo 判断商品的库存
                if int(count) > sku.stock:
                    return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})

                # todo 向df——order——goods表中添加一条记录
                OrderGoods.objects.create(
                    order=order,
                    sku=sku,
                    count=count,
                    price=sku.price

                )

                # todo 更新商品的库存和销量
                sku.stock -= int(count)
                sku.sales += int(count)
                sku.save()

                # todo 累加计算订单商品的总数两和总价格
                amount = sku.price * int(count)
                total_count += int(count)
                total_price += amount

            # todo 更新订单信息表中的商品的总数量和总价格
            order.total_count = total_count
            order.total_price = total_price
            order.save()

            # 提交
            transaction.savepoint_commit(save_point)
        except Exception as e:
            # 回滚
            transaction.savepoint_rollback(save_point)
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})

        # todo 清除用户购物车对应的记录
        conn.hdel(cart_key, sku_ids)

        # 返回应答
        return JsonResponse({'res': 5, 'errmsg': '床架成功'})
