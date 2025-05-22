from django.contrib import admin
from dvadmin.hrms.models import Employee, Position, Attendance, Leave
# 这是一个Django管理后台配置文件
# 用于注册HRMS(人力资源管理系统)的模型到Django管理界面
# 包含了以下模型:
# - Employee: 员工信息模型
# - Position: 职位信息模型  
# - Attendance: 考勤记录模型
# - Leave: 请假记录模型
# - resume： 简历管理模型

admin.site.register(Employee)
admin.site.register(Position)
admin.site.register(Attendance)
admin.site.register(Leave)
admin.site.register(resume)