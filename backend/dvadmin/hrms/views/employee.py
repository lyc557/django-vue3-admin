import django_filters
from rest_framework import serializers

from dvadmin.hrms.models import Employee
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class EmployeeSerializer(CustomModelSerializer):
    """
    员工-序列化器
    """
    dept_name = serializers.CharField(source='dept.name', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Employee
        fields = "__all__"
        read_only_fields = ["id"]


class EmployeeCreateUpdateSerializer(CustomModelSerializer):
    """
    员工管理 创建/更新时的列化器
    """

    class Meta:
        model = Employee
        fields = "__all__"
        read_only_fields = ["id"]


class EmployeeFilter(django_filters.FilterSet):
    """
    员工管理 过滤器
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    employee_id = django_filters.CharFilter(lookup_expr='icontains')
    dept_id = django_filters.CharFilter(field_name='dept__id')

    class Meta:
        model = Employee
        fields = ['employee_id', 'name', 'gender', 'status', 'dept_id']


class EmployeeViewSet(CustomModelViewSet):
    """
    员工管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    create_serializer_class = EmployeeCreateUpdateSerializer
    update_serializer_class = EmployeeCreateUpdateSerializer
    filter_class = EmployeeFilter
    search_fields = ('name', 'employee_id', 'phone')
    export_field_label = {
        "employee_id": "员工编号",
        "name": "员工姓名",
        "gender": "性别",
        "phone": "联系电话",
        "email": "邮箱",
        "dept": "所属部门",
        "position": "职位",
        "hire_date": "入职日期",
        "status": "员工状态",
        "creator": "创建者",
        "modifier": "修改者",
        "create_datetime": "创建时间",
        "update_datetime": "更新时间",
    }
    export_serializer_class = EmployeeSerializer