from django.db import models
from db.base_model import BaseModel
from tinymce.models import HTMLField
from goods.models import *
from user.models import *


class CartInfo(BaseModel):
    gid = models.ForeignKey('GoodSKU', verbose_name='商品ID')
    uid = models.ForeignKey('User', verbose_name='用户ID')
    num = models.IntegerField(default=0, verbose_name='商品数量')

    class Meta:
        db_table = 'df_cart_info'
        verbose_name = '购物车详情'
        verbose_name_plural = verbose_name
