from django.contrib import admin
from dvadmin.hrms.models import Employee, Position, Attendance, Leave

admin.site.register(Employee)
admin.site.register(Position)
admin.site.register(Attendance)
admin.site.register(Leave)