from django.db import models
from db.base_model import BaseModel


class OrderInfo(BaseModel):
    # 订单模型类
    PAY_METHOD_CHOICES = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付'),
    )

    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成'),
    )

    # id 比如时间戳加ID
    order_id = models.CharField(max_length=128, primary_key=True, verbose_name='订单ID')
    user = models.ForeignKey('user.User', verbose_name='用户')
    addr = models.ForeignKey('user.Address', verbose_name='地址')
    pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES, default=3, verbose_name='ZHifu')

    # 冗余 为了方便使用，运行本分冗余
    total_count = models.IntegerField(default=1, verbose_name='商品数量')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')

    transit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单运费')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name='订单状态')
    trade_no = models.CharField(max_length=128, default='', verbose_name='订单编号')

    class Meta:
        db_table = 'df_order_info'
        verbose_name = '订单'
        verbose_name_plural = verbose_name


class OrderGoods(BaseModel):
    # 订单详情 商品模型类
    order = models.ForeignKey('OrderInfo', verbose_name='订单')
    sku = models.ForeignKey('goods.GoodSKU', verbose_name='商品SKU')
    count = models.IntegerField(default=1, verbose_name='商品数目')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')

    class Meta:
        db_table = 'df_order_goods'
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name
