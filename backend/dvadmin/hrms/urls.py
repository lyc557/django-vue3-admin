from django.urls import path
from rest_framework import routers

from dvadmin.hrms.views.employee import EmployeeViewSet
from dvadmin.hrms.views.attendance import AttendanceViewSet
from dvadmin.hrms.views.leave import LeaveViewSet
from dvadmin.hrms.views.resume import ResumeFileViewSet

hrms_url = routers.SimpleRouter()
hrms_url.register(r'employee', EmployeeViewSet)
hrms_url.register(r'attendance', AttendanceViewSet)
hrms_url.register(r'leave', LeaveViewSet)
hrms_url.register(r'resume', ResumeFileViewSet)

urlpatterns = [
    path('employee/export/', EmployeeViewSet.as_view({'post': 'export_data', })),
    path('employee/import/', EmployeeViewSet.as_view({'get': 'import_data', 'post': 'import_data'})),
    path('resume/upload/', ResumeFileViewSet.as_view({'post': 'upload'})),
]
urlpatterns += hrms_url.urls