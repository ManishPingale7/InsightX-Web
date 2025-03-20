from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class MonitorRecord(models.Model):
    id=models.AutoField(primary_key=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    machine_name=models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    predictions = models.JSONField()


class VibrationAnalysisRecord(models.Model):
    machine_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_text = models.TextField()
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.machine_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


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
                self.status = f"No Failure ({(self.predictions[0][ind]*100):.2f} %)"
            case 1:
                self.status = f"Power Failure ({(self.predictions[0][ind]*100):.2f} %)"
            case 2:
                self.status = f"Tool Failure ({(self.predictions[0][ind]*100):.2f} %)"
            case 3:
                self.status = f"Overstrain Failure ({(self.predictions[0][ind]*100):.2f} %)"
            case 4:
                self.status = f"Heat Failure ({(self.predictions[0][ind]*100):.2f} %)"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.machine_name
