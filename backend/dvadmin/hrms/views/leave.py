import django_filters
from rest_framework import serializers
from rest_framework.decorators import action

from dvadmin.hrms.models import Leave
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse


class LeaveSerializer(CustomModelSerializer):
    """
    请假申请-序列化器
    """
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approver_name = serializers.CharField(source='approver.name', read_only=True)

    class Meta:
        model = Leave
        fields = "__all__"
        read_only_fields = ["id"]


class LeaveCreateUpdateSerializer(CustomModelSerializer):
    """
    请假申请 创建/更新时的列化器
    """

    class Meta:
        model = Leave
        fields = "__all__"
        read_only_fields = ["id"]


class LeaveFilter(django_filters.FilterSet):
    """
    请假申请 过滤器
    """
    employee_name = django_filters.CharFilter(field_name='employee__name', lookup_expr='icontains')
    start_date_range = django_filters.DateFromToRangeFilter(field_name='start_date')

    class Meta:
        model = Leave
        fields = ['employee', 'leave_type', 'status']


class LeaveViewSet(CustomModelViewSet):
    """
    请假申请接口
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
    filter_class = LeaveFilter
    search_fields = ('employee__name',)

    @action(methods=['POST'], detail=True)
    def approve(self, request, *args, **kwargs):
        """
        审批请假申请
        """
        instance = self.get_object()
        status = request.data.get('status')
        remark = request.data.get('remark', '')
        
        if status not in [1, 2]:  # 1: 批准, 2: 拒绝
            return ErrorResponse(msg="审批状态无效")
        
        if instance.status != 0:  # 0: 待审批
            return ErrorResponse(msg="只能审批待审批状态的申请")
        
        instance.status = status
        instance.approver = request.user
        instance.approve_time = timezone.now()
        instance.approve_remark = remark
        instance.save()
        
        return SuccessResponse(msg="审批成功")