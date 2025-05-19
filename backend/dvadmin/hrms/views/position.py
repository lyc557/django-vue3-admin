from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers

from dvadmin.hrms.models import Position
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class PositionSerializer(CustomModelSerializer):
    """
    职位-序列化器
    """
    
    class Meta:
        model = Position
        fields = "__all__"
        read_only_fields = ["id"]


class PositionCreateUpdateSerializer(CustomModelSerializer):
    """
    职位管理 创建/更新时的列化器
    """
    
    class Meta:
        model = Position
        fields = '__all__'


class PositionViewSet(CustomModelViewSet):
    """
    职位管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    create_serializer_class = PositionCreateUpdateSerializer
    update_serializer_class = PositionCreateUpdateSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['name', 'code']