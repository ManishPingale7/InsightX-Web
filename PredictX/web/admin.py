from django.contrib import admin
from .models import MachineRecord,MonitorRecord

# Register your models here.

class MachineRecordAdmin(admin.ModelAdmin):
    readonly_fields=('timestamp',)

admin.site.register(MachineRecord,MachineRecordAdmin)
admin.site.register(MonitorRecord)