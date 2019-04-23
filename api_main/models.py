from django.db import models
from django.conf import settings
# Create your models here.
class Employee(models.Model):
    emp_id = models.IntegerField(primary_key = True)
    salary = models.FloatField()
    bonus = models.FloatField()
    def __str__(self):
        return str(self.emp_id)
