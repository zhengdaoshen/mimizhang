# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0002_goodsku_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='goodsku',
            old_name='goos',
            new_name='goods',
        ),
    ]
