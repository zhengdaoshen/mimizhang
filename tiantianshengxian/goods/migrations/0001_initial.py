# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updae_time', models.DateTimeField(auto_now_add=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('name', models.CharField(verbose_name='商品SPU名称', max_length=20)),
                ('detail', tinymce.models.HTMLField(blank=True, verbose_name='商品详情')),
            ],
            options={
                'verbose_name': '商品SPU',
                'verbose_name_plural': '商品SPU',
                'db_table': 'df_goods',
            },
        ),
        migrations.CreateModel(
            name='GoodsImage',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updae_time', models.DateTimeField(auto_now_add=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('image', models.ImageField(upload_to='goods', verbose_name='图片路径')),
            ],
            options={
                'verbose_name': '商品图片',
                'verbose_name_plural': '商品图片',
                'db_table': 'df_good_image',
            },
        ),
        migrations.CreateModel(
            name='GoodSKU',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updae_time', models.DateTimeField(auto_now_add=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('name', models.CharField(verbose_name='商品名称', max_length=20)),
                ('desc', models.CharField(verbose_name='商品简介', max_length=256)),
                ('price', models.DecimalField(decimal_places=2, verbose_name='商品价格', max_digits=10)),
                ('unice', models.CharField(verbose_name='商品单位', max_length=20)),
                ('stock', models.IntegerField(default=1, verbose_name='商品库存')),
                ('sales', models.IntegerField(default=0, verbose_name='商品销量')),
                ('status', models.SmallIntegerField(default=1, choices=[(0, '下线'), (1, '上线')], verbose_name='商品状态 ')),
                ('goos', models.ForeignKey(to='goods.Goods', verbose_name='商品SPU')),
            ],
            options={
                'verbose_name': '商品SKU',
                'verbose_name_plural': '商品SKU',
                'db_table': 'df_goods_sku',
            },
        ),
        migrations.CreateModel(
            name='GoodType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updae_time', models.DateTimeField(auto_now_add=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('name', models.CharField(verbose_name='种类名称', max_length=20)),
                ('logo', models.CharField(verbose_name='标识', max_length=20)),
                ('image', models.ImageField(upload_to='type', verbose_name='商品类型图片')),
            ],
            options={
                'verbose_name': '商品种类',
                'verbose_name_plural': '商品种类',
                'db_table': 'df_good_type',
            },
        ),
        migrations.CreateModel(
            name='IndexGoodBanner',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updae_time', models.DateTimeField(auto_now_add=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('image', models.ImageField(upload_to='banner', verbose_name='图片')),
                ('index', models.SmallIntegerField(default=0, verbose_name='战士顺序')),
                ('sku', models.ForeignKey(to='goods.GoodSKU', verbose_name='商品')),
            ],
            options={
                'verbose_name': '首页轮播图',
                'verbose_name_plural': '首页轮播图',
                'db_table': 'df_index_banner',
            },
        ),
        migrations.CreateModel(
            name='IndexPromotionBanner',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updae_time', models.DateTimeField(auto_now_add=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('name', models.CharField(verbose_name='活动名称', max_length=20)),
                ('url', models.CharField(verbose_name='活动链接', max_length=256)),
                ('image', models.ImageField(upload_to='banner', verbose_name='活动图片')),
                ('index', models.SmallIntegerField(default=0, verbose_name='展示顺序')),
            ],
            options={
                'verbose_name': '主页促销活动',
                'verbose_name_plural': '主页促销活动',
                'db_table': 'df_index_promotion',
            },
        ),
        migrations.CreateModel(
            name='IndexTypeGoodBanner',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updae_time', models.DateTimeField(auto_now_add=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('display_type', models.SmallIntegerField(default=1, choices=[(0, '标题'), (1, '图片')], verbose_name='展示')),
                ('index', models.SmallIntegerField(default=0, verbose_name='展示顺序')),
                ('sku', models.ForeignKey(to='goods.GoodSKU', verbose_name='商品SKU')),
                ('type', models.ForeignKey(to='goods.GoodType', verbose_name='商品类型')),
            ],
            options={
                'verbose_name': '主页分类展示商品',
                'verbose_name_plural': '主页分类展示商品',
                'db_table': 'df_index_tyoe_good',
            },
        ),
        migrations.AddField(
            model_name='goodsku',
            name='type',
            field=models.ForeignKey(to='goods.GoodType', verbose_name='商品种类'),
        ),
        migrations.AddField(
            model_name='goodsimage',
            name='sku',
            field=models.ForeignKey(to='goods.GoodSKU', verbose_name='商品'),
        ),
    ]
