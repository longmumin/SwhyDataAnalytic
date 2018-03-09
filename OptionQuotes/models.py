from django.db import models

# Create your models here.

class loadDataModel(models.Model):
    qixian = models.CharField('期权期限', max_length=20)
    selected_date = models.CharField('报价日期', max_length=20)
    instrument = models.CharField('标的', max_length=50)
    futuresType = models.CharField('标的合约', max_length=20)
    startTime = models.DateField('开始时间', null=True)
    endTime = models.DateField('结束时间', null=True)
    containerName = models.CharField('容器名', max_length=50)
    forward = models.CharField('期货目标价格', max_length=20)
    lastPrice = models.CharField('上日收盘价', max_length=20)

    quoteData = models.TextField('期货序列数据', default='--')
    TQuoteData = models.TextField('期货T型报价序列数据', default='--')

    def __unicode__(self):
        return self.title

