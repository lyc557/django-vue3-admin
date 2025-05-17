# -*- coding: utf-8 -*-
import os

from rest_framework import serializers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
import django

django.setup()
from dvadmin.hrms.models import Employee, Attendance, Leave
from dvadmin.utils.serializers import CustomModelSerializer


class EmployeeInitSerializer(CustomModelSerializer):
    """
    初始化员工信息(用于生成初始化json文件)
    """
    dept_key = serializers.SerializerMethodField()

    def get_dept_key(self, obj):
        if obj.dept:
            return obj.dept.key
        else:
            return None

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        dept_key = self.initial_data.get('dept_key', None)
        if dept_key:
            from dvadmin.system.models import Dept
            dept_id = Dept.objects.filter(key=dept_key).first()
            instance.dept = dept_id
            instance.save()
        return instance

    class Meta:
        model = Employee
        fields = "__all__"
        read_only_fields = ['id']


class AttendanceInitSerializer(CustomModelSerializer):
    """
    初始化考勤记录(用于生成初始化json文件)
    """
    employee_id = serializers.CharField(source='employee.employee_id')

    def save(self, **kwargs):
        employee_id = self.initial_data.get('employee_id', None)
        if employee_id:
            employee = Employee.objects.filter(employee_id=employee_id).first()
            if employee:
                self.initial_data['employee'] = employee.id
        return super().save(**kwargs)

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ['id']


class LeaveInitSerializer(CustomModelSerializer):
    """
    初始化请假申请(用于生成初始化json文件)
    """
    employee_id = serializers.CharField(source='employee.employee_id')
    approver_username = serializers.CharField(source='approver.username', required=False, allow_null=True)

    def save(self, **kwargs):
        employee_id = self.initial_data.get('employee_id', None)
        if employee_id:
            employee = Employee.objects.filter(employee_id=employee_id).first()
            if employee:
                self.initial_data['employee'] = employee.id
        
        approver_username = self.initial_data.get('approver_username', None)
        if approver_username:
            from dvadmin.system.models import Users
            approver = Users.objects.filter(username=approver_username).first()
            if approver:
                self.initial_data['approver'] = approver.id
        
        return super().save(**kwargs)

    class Meta:
        model = Leave
        fields = "__all__"
        read_only_fields = ['id']