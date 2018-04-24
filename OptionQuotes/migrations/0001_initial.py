from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('futuresType', models.CharField(max_length=20, verbose_name='期货合约类型')),
                ('qixian', models.CharField(max_length=20, verbose_name='期权期限')),
                ('selected_date', models.DateField(null=True, verbose_name='报价时间')),
                ('instrument', models.DateField(null=True, verbose_name='合约代码')),
                ('startTime', models.DateField(null=True, verbose_name='开始时间')),
                ('endTime', models.DateField(null=True, verbose_name='结束时间')),
                ('containerName', models.CharField(max_length=50, verbose_name='容器名')),
                ('method', models.CharField(max_length=20, verbose_name='加载方式')),
                ('forward', models.CharField ('期货目标价格', max_length=20)),
                ('lastPrice', models.CharField ('上日收盘价', max_length=20)),
                ('optionPremium', models.CharField('权利金', max_length=20)),
                ('quoteData', models.TextField(default='--', verbose_name='序列数据')),
                ('strikePrice', models.CharField('行权价', max_length=20)),
                ('revenueList', models.TextField(verbose_name='预期收益序列', default='--')),


            ],
        ),
    ]
