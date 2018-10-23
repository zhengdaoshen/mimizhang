# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='goodsku',
            name='image',
            field=models.ImageField(default=datetime.datetime(2018, 10, 23, 10, 4, 56, 493574), verbose_name='商品图片', upload_to='goods'),
            preserve_default=False,
        ),
    ]
