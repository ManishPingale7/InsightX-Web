from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class MachineRecord(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    machine_name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    air_temp = models.IntegerField()
    process_temp = models.IntegerField()
    rotational_speed = models.IntegerField()
    torque = models.IntegerField()
    tool_wear = models.IntegerField()
    quality = models.IntegerField()
    predictions = models.JSONField()
    status = models.CharField(max_length=30)

    def save(self, *args, **kwargs):
        ind = 0
        for i in range(len(self.predictions[0])):
            if (self.predictions[0][i] > self.predictions[0][ind]):
                ind = i
        match ind:
            case 0:
                self.status = f"No Failure ({(self.predictions[0][ind]*100)} %)"
            case 1:
                self.status = f"Power Failure ({(self.predictions[0][ind]*100)} %)"
            case 2:
                self.status = f"Tool Failure ({(self.predictions[0][ind]*100)} %)"
            case 3:
                self.status = f"Overstrain Failure ({(self.predictions[0][ind]*100)} %)"
            case 4:
                self.status = f"Heat Failure ({(self.predictions[0][ind]*100)} %)"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.machine_name
