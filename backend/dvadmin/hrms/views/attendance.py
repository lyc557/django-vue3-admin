import django_filters
from rest_framework import serializers

from dvadmin.hrms.models import Attendance, Employee
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class AttendanceSerializer(CustomModelSerializer):
    """
    考勤记录-序列化器
    """
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ["id"]


class AttendanceCreateUpdateSerializer(CustomModelSerializer):
    """
    考勤记录 创建/更新时的列化器
    """

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ["id"]


class AttendanceFilter(django_filters.FilterSet):
    """
    考勤记录 过滤器
    """
    employee_name = django_filters.CharFilter(field_name='employee__name', lookup_expr='icontains')
    date_range = django_filters.DateFromToRangeFilter(field_name='date')

    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'status']


class AttendanceViewSet(CustomModelViewSet):
    """
    考勤记录接口
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
    filter_class = AttendanceFilter
    search_fields = ('employee__name',)