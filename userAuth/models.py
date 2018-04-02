from django.db import models

# Create your models here.
class loadUserDataModel(models.Model):
    userData = models.TextField('用户信息', default='--')

    def __unicode__(self):
        return self.title