from django.urls import path
from rest_framework import routers

from dvadmin.hrms.views.employee import EmployeeViewSet
from dvadmin.hrms.views.position import PositionViewSet
from dvadmin.hrms.views.attendance import AttendanceViewSet
from dvadmin.hrms.views.leave import LeaveViewSet
from dvadmin.hrms.views.resume import ResumeViewSet

router = routers.SimpleRouter()
router.register(r'employee', EmployeeViewSet)
router.register(r'position', PositionViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'leave', LeaveViewSet)
# 添加简历相关路由
router.register(r'resume', ResumeViewSet)

urlpatterns = [
    # 这里可以添加不适合使用ModelViewSet的接口
]

urlpatterns += router.urls