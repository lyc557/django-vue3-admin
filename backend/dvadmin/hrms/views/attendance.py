from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.decorators import action
from datetime import datetime, timedelta

from dvadmin.hrms.models import Attendance, Employee
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse


class AttendanceSerializer(CustomModelSerializer):
    """
    考勤-序列化器
    """
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    dept_name = serializers.CharField(source='employee.dept.name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ["id"]


class AttendanceCreateUpdateSerializer(CustomModelSerializer):
    """
    考勤管理 创建/更新时的列化器
    """
    
    class Meta:
        model = Attendance
        fields = '__all__'


class AttendanceViewSet(CustomModelViewSet):
    """
    考勤管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    create_serializer_class = AttendanceCreateUpdateSerializer
    update_serializer_class = AttendanceCreateUpdateSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['employee', 'date', 'status']
    
    @action(methods=['POST'], detail=False)
    def check_in(self, request):
        """员工签到"""
        employee_id = request.data.get('employee_id')
        if not employee_id:
            return DetailResponse(data=None, msg="请提供员工ID", code=4000)
        
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return DetailResponse(data=None, msg="员工不存在", code=4000)
        
        today = datetime.now().date()
        now = datetime.now()
        
        # 检查是否已经签到
        attendance = Attendance.objects.filter(employee=employee, date=today).first()
        if attendance and attendance.check_in:
            return DetailResponse(data=None, msg="今日已签到", code=4000)
        
        # 判断是否迟到
        work_start_time = datetime.combine(today, datetime.strptime('09:00', '%H:%M').time())
        status = 1 if now > work_start_time else 0
        
        if attendance:
            attendance.check_in = now
            attendance.status = status
            attendance.save()
        else:
            attendance = Attendance.objects.create(
                employee=employee,
                date=today,
                check_in=now,
                status=status
            )
        
        return DetailResponse(data=AttendanceSerializer(attendance).data, msg="签到成功")
    
    @action(methods=['POST'], detail=False)
    def check_out(self, request):
        """员工签退"""
        employee_id = request.data.get('employee_id')
        if not employee_id:
            return DetailResponse(data=None, msg="请提供员工ID", code=4000)
        
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return DetailResponse(data=None, msg="员工不存在", code=4000)
        
        today = datetime.now().date()
        now = datetime.now()
        
        # 检查是否已经签到
        attendance = Attendance.objects.filter(employee=employee, date=today).first()
        if not attendance:
            return DetailResponse(data=None, msg="今日未签到，无法签退", code=4000)
        
        if attendance.check_out:
            return DetailResponse(data=None, msg="今日已签退", code=4000)
        
        # 判断是否早退
        work_end_time = datetime.combine(today, datetime.strptime('18:00', '%H:%M').time())
        
        # 如果已经是迟到状态，则保持迟到状态，否则判断是否早退
        if attendance.status != 1:
            attendance.status = 2 if now < work_end_time else 0
        
        attendance.check_out = now
        attendance.save()
        
        return DetailResponse(data=AttendanceSerializer(attendance).data, msg="签退成功")