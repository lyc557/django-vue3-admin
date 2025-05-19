# ... existing code ...
import os
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from dvadmin.hrms.models import Resume
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from dvadmin.utils.viewset import CustomModelViewSet

class ResumeSerializer(CustomModelSerializer):
    """简历序列化器"""
    
    class Meta:
        model = Resume
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]

class ResumeViewSet(CustomModelViewSet):
    """简历管理"""
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    
    @action(methods=["POST"], detail=False)
    def upload(self, request):
        """上传简历文件"""
        file = request.FILES.get("file")
        if not file:
            return Response({"code": 4000, "msg": "请上传文件"})
            
        # 获取文件信息
        file_name = file.name
        file_size = round(file.size / 1024)
        file_type = file_name.split(".")[-1]
        
        # 保存文件
        resume = Resume.objects.create(
            file=file,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size
        )
        
        return Response({
            "code": 2000,
            "msg": "上传成功",
            "data": {
                "id": resume.id,
                "file_name": resume.file_name,
                "url": resume.file.url if hasattr(resume.file, 'url') else None
            }
        })
    
    @action(methods=["POST"], detail=False)
    def analyze(self, request):
        """分析简历内容"""
        file_id = request.data.get("file_id")
        job_description = request.data.get("job_description", "")
        
        if not file_id:
            return Response({"code": 4000, "msg": "请提供文件ID"})
            
        try:
            resume = Resume.objects.get(id=file_id)
        except Resume.DoesNotExist:
            return Response({"code": 4000, "msg": "文件不存在"})
            
        # 这里可以添加简历解析逻辑
        # 例如：调用第三方API或使用NLP库解析简历内容
        
        # 示例分析结果
        analysis_result = {
            "name": "示例姓名",
            "education": "本科",
            "experience": "3年",
            "skills": ["Python", "Django", "Vue"],
            "match_score": 85
        }
        
        # 更新分析结果
        resume.analysis_result = analysis_result
        resume.save()
        
        return Response({
            "code": 2000,
            "msg": "分析成功",
            "data": analysis_result
        })