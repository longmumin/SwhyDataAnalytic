from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class loadDataModel(models.Model):
    bondType = models.CharField('债券类型', max_length=20)
    duration = models.CharField('债券期限', max_length=20)
    startTime = models.DateField('开始时间', null=True)
    endTime = models.DateField('结束时间', null=True)
    containerName = models.CharField('容器名', max_length=50)
    method = models.CharField('加载方式', max_length=20)
    quoteData = models.TextField('债券序列数据', default='--')

    def __unicode__(self):
        return self.title

# class bondYTMAnalyicDataModel(models.Model):
#     latestDiff = models.FloatField('最新价差显示', default=0)
#     latestDiffDiff = models.FloatField('最新价差分析变化量', default=0)
#     latestDiffPercent = models.FloatField('最新价差分析变化量幅度', default=0)
#     lastDiff = models.FloatField('昨结价差', default=0)
#     mean = models.FloatField('平均值', default=0)
#     median = models.FloatField('中位数', default=0)
#     deviateMean = models.FloatField('偏离平均值', default=0)
#     standardDeviation = models.FloatField('标准差', default=0)
#     percentile = models.FloatField('百分位数', default=0)
#     deviateStandardDeviation = models.FloatField('偏离标准差', default=0)
#     max = models.FloatField('最大值', default=0)
#     min = models.FloatField('最小值', default=0)
#
#     def __unicode__(self):
#         return self.title

# class bondYTMDiffModel(models.Model):
#     bondType = models.CharField('债券类型', max_length=20)
#     duration = models.CharField('债券期限', max_length=20)
#     startTime = models.DateField('开始时间', null=True)
#     endTime = models.DateField('结束时间', null=True)
#     containerName = models.CharField('容器名', max_length=50)
#     method = models.CharField('加载方式', max_length=20)
#     quoteData = JSONField()
#
#     def __unicode__(self):
#         return self.title
#
# class diffDataModel(models.Model):
#     diffData = models.TextField('价差数据', default='--')
#
#     def __unicode__(self):
#         return self.title