# 初始化
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "application.settings")
django.setup()

from dvadmin.utils.core_initialize import CoreInitialize
from dvadmin.hrms.fixtures.initSerializer import (
    EmployeeInitSerializer, AttendanceInitSerializer, LeaveInitSerializer
)


class Initialize(CoreInitialize):

    def init_employee(self):
        """
        初始化员工信息
        """
        self.init_base(EmployeeInitSerializer, unique_fields=['employee_id'])

    def init_attendance(self):
        """
        初始化考勤记录
        """
        self.init_base(AttendanceInitSerializer, unique_fields=['employee', 'date'])

    def init_leave(self):
        """
        初始化请假申请
        """
        self.init_base(LeaveInitSerializer, unique_fields=['employee', 'start_date', 'end_date'])

    def run(self):
        self.init_employee()
        self.init_attendance()
        self.init_leave()


if __name__ == "__main__":
    Initialize(app='dvadmin.hrms').run()