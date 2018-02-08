from django.db import models

# Create your models here.

class loadDataModel(models.Model):

    bondType = models.CharField('债券类型', max_length=20)
    duration = models.CharField('债券期限', max_length=20)
    startTime = models.DateField('开始时间', null=True)
    endTime = models.DateField('结束时间', null=True)
    containerName = models.CharField('容器名', max_length=20)
    method = models.CharField('加载方式', max_length=20)
    quoteData = models.TextField('债券序列数据', default='--')

    def __unicode__(self):
        return self.title