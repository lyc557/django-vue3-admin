from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.decorators import action
from datetime import datetime

from dvadmin.hrms.models import Leave, Employee
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse


class LeaveSerializer(CustomModelSerializer):
    """
    请假-序列化器
    """
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    dept_name = serializers.CharField(source='employee.dept.name', read_only=True)
    approver_name = serializers.CharField(source='approver.name', read_only=True)
    
    class Meta:
        model = Leave
        fields = "__all__"
        read_only_fields = ["id"]


class LeaveCreateUpdateSerializer(CustomModelSerializer):
    """
    请假管理 创建/更新时的列化器
    """
    
    class Meta:
        model = Leave
        fields = '__all__'


class LeaveViewSet(CustomModelViewSet):
    """
    请假管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    create_serializer_class = LeaveCreateUpdateSerializer
    update_serializer_class = LeaveCreateUpdateSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['employee', 'leave_type', 'status']
    
    @action(methods=['POST'], detail=True)
    def approve(self, request, pk=None):
        """审批请假申请"""
        leave = self.get_object()
        
        if leave.status != 0:
            return DetailResponse(data=None, msg="该申请已处理", code=4000)
        
        status = request.data.get('status')
        remark = request.data.get('remark', '')
        
        if status not in [1, 2]:
            return DetailResponse(data=None, msg="审批状态无效", code=4000)
        
        leave.status = status
        leave.approver = request.user
        leave.approval_time = datetime.now()
        leave.approval_remark = remark
        leave.save()
        
        return DetailResponse(data=LeaveSerializer(leave).data, msg="审批成功")
    
    @action(methods=['GET'], detail=False)
    def my_leaves(self, request):
        """获取当前用户的请假记录"""
        user = request.user
        try:
            employee = Employee.objects.get(name=user.name)
        except Employee.DoesNotExist:
            return DetailResponse(data=[], msg="未找到员工信息")
        
        queryset = self.queryset.filter(employee=employee)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")