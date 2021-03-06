# Generated by Django 2.0 on 2018-03-30 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='loadDataModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bondType', models.CharField(max_length=20, verbose_name='债券类型')),
                ('duration', models.CharField(max_length=20, verbose_name='债券期限')),
                ('startTime', models.DateField(null=True, verbose_name='开始时间')),
                ('endTime', models.DateField(null=True, verbose_name='结束时间')),
                ('containerName', models.CharField(max_length=50, verbose_name='容器名')),
                ('method', models.CharField(max_length=20, verbose_name='加载方式')),
                ('quoteData', models.TextField(default='--', verbose_name='债券序列数据')),
            ],
        ),
    ]
