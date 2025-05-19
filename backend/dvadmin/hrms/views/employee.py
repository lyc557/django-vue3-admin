from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.decorators import action

from dvadmin.hrms.models import Employee
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.json_response import DetailResponse, SuccessResponse
from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.utils.crud_mixin import FastCrudMixin
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.permission import CustomPermission

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


class EmployeeViewSet(CustomModelViewSet, FastCrudMixin,FieldPermissionMixin):
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

    def list(self, request, *args, **kwargs):
        self.request.query_params._mutable = True
        params = self.request.query_params
        known_params = {'page', 'limit', 'pcode'}
        # 使用集合操作检查是否有未知参数
        other_params_exist = any(param not in known_params for param in params)
        if other_params_exist:
            queryset = self.queryset.filter(enable=True)
        else:
            pcode = params.get('pcode', None)
            params['limit'] = 999
            if params and pcode:
                queryset = self.queryset.filter(enable=True, pcode=pcode)
            else:
                queryset = self.queryset.filter(enable=True, level=1)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, request=request)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(data=serializer.data, msg="获取成功")
