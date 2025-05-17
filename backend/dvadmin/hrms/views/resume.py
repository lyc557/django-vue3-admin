# -*- coding: utf-8 -*-
"""
@author: 简历上传
@contact: 
@Created on: 2023
@Remark: 简历上传管理
"""

from rest_framework import serializers

from dvadmin.hrms.models import ResumeFile
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser


class ResumeFileSerializer(CustomModelSerializer):
    """
    简历文件-序列化器
    """
    class Meta:
        model = ResumeFile
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class ResumeFileCreateUpdateSerializer(CustomModelSerializer):
    """
    简历文件管理 创建/更新时的序列化器
    """
    class Meta:
        model = ResumeFile
        fields = "__all__"


class ResumeFileViewSet(CustomModelViewSet):
    """
    简历文件管理接口
    list:查询
    create:新增
    update:修改
    destroy:删除
    """
    queryset = ResumeFile.objects.all()
    serializer_class = ResumeFileSerializer
    create_serializer_class = ResumeFileCreateUpdateSerializer
    update_serializer_class = ResumeFileCreateUpdateSerializer
    filter_fields = ['name', 'candidate_name', 'position', 'status']
    search_fields = ['name', 'candidate_name', 'position']
    parser_classes = [MultiPartParser, FormParser]  # 确保这行存在
    
    @action(methods=['post'], detail=False, url_path='upload')
    def upload_resume(self, request):
        print("----------------------------")
        """
        上传简历文件
        """
        file_obj = request.FILES.get('file')
        if not file_obj:
            return DetailResponse(data=None, msg="未获取到上传文件", code=400)
        
        # 获取其他表单数据
        candidate_name = request.data.get('candidate_name', '')
        position = request.data.get('position', '')
        
        # 创建简历文件记录
        resume_file = ResumeFile(
            name=file_obj.name,
            url=file_obj,
            candidate_name=candidate_name,
            position=position,
            status=0  # 默认未处理状态
        )
        resume_file.save()
        
        # 返回文件信息
        serializer = self.get_serializer(resume_file)
        return DetailResponse(data=serializer.data, msg="上传成功")