from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class MachineRecord(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    air_temp = models.IntegerField()
    process_temp = models.IntegerField()
    rotational_speed = models.IntegerField()
    torque = models.IntegerField()
    tool_wear = models.IntegerField()
    quality = models.IntegerField()
    predictions = models.JSONField()

    def __str__(self):
        return self.name
