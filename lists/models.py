from django.db import models


# Create your models here.
class pokemon(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=30)

    def __str__(self):
        return self.field_name
