from django.db import models

# Create your models here.
class NodePositions(models.Model):
    sid = models.CharField(primary_key=True, max_length=35)
    type = models.CharField(max_length=24, default='say-item')
    x = models.FloatField()
    y = models.FloatField()