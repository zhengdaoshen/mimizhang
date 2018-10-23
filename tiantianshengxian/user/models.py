from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel


class User(AbstractUser, BaseModel):
    class Meta:
        db_table = 'tt_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class Address(BaseModel):
    user = models.ForeignKey('User', verbose_name='所属账户')
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    addr = models.CharField(max_length=256, verbose_name='收件地址')
    zip_code = models.CharField(max_length=6, null=True, verbose_name='邮政编码')
    phone = models.CharField(max_length=11, verbose_name='联系电话 ')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')

    class Meta:
        db_table = 'df_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name


class Province(models.Model):
    province = models.CharField(max_length=100, unique=True)
    provinceID = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.province


class City(models.Model):
    cityID = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100, unique=True)
    fatherID = models.ForeignKey(Province, db_column='fatherID')

    def __str__(self):
        return self.city


class Area(models.Model):
    areaID = models.CharField(max_length=100, unique=True)
    area = models.CharField(max_length=100, unique=True)
    fatherID = models.ForeignKey(City, db_column='fatherID')

    def __str__(self):
        return self.area
