from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.decorators import action

from dvadmin.hrms.models import Employee
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse


class EmployeeSerializer(CustomModelSerializer):
    """
    员工-序列化器
    """
    dept_name = serializers.CharField(source='dept.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    
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
        fields = '__all__'


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
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['name', 'employee_id', 'status', 'dept', 'position']

    def list(self, request, *args, **kwargs):
        print("0000000000"+request.query_params)
        return super().list(request, *args, **kwargs)
    
    @action(methods=['GET'], detail=False)
    def get_employee_count(self, request):
        """获取员工统计数据"""
        total_count = self.queryset.count()
        active_count = self.queryset.filter(status=0).count()
        trial_count = self.queryset.filter(status=2).count()
        departed_count = self.queryset.filter(status=1).count()
        
        data = {
            'total': total_count,
            'active': active_count,
            'trial': trial_count,
            'departed': departed_count
        }
        
        return DetailResponse(data=data, msg="获取成功")