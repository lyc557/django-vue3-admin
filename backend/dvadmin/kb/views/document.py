from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.db.models import Q

from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.kb.models import Document, DocumentCategory, DocumentTag, DocumentVersion, DocumentAttachment
from dvadmin.kb.serializers import (
    DocumentSerializer, DocumentCategorySerializer,
    DocumentTagSerializer, DocumentVersionSerializer, DocumentAttachmentSerializer
)

class DocumentCategoryViewSet(CustomModelViewSet):
    """
    文档分类管理
    list:查询
    create:新增
    update:修改
    destroy:删除
    """
    queryset = DocumentCategory.objects.all()
    serializer_class = DocumentCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'parent']

class DocumentTagViewSet(CustomModelViewSet):
    """
    文档标签管理
    list:查询
    create:新增
    update:修改
    destroy:删除
    """
    queryset = DocumentTag.objects.all()
    serializer_class = DocumentTagSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name']
    search_fields = ['name']

class DocumentViewSet(CustomModelViewSet):
    """
    文档管理
    list:查询
    create:新增
    update:修改
    destroy:删除
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'status', 'creator']
    search_fields = ['title', 'content']

    def create(self, request, *args, **kwargs):
        """
        创建文档并打印POST参数
        """
        print('=== POST 参数 ===')
        print('请求数据:', request.data)
        print('请求头:', request.headers)
        
        return super().create(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return DocumentDetailSerializer
        return DocumentSerializer    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 关键词搜索
        keywords = self.request.query_params.get('keywords', None)
        if keywords:
            queryset = queryset.filter(
                Q(title__icontains=keywords) | 
                Q(content__icontains=keywords) |
                Q(tags__name__icontains=keywords)
            ).distinct()
        
        # 标签过滤
        tag_id = self.request.query_params.get('tag_id', None)
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
            
        return queryset
    
    def perform_create(self, serializer):
        # 设置创建人为当前用户
        serializer.save(creator=self.request.user)
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        # 如果内容有变化，创建新版本
        if 'content' in serializer.validated_data or 'title' in serializer.validated_data:
            # 获取最新版本号
            latest_version = instance.versions.order_by('-version').first()
            new_version_num = latest_version.version + 1 if latest_version else 1
            
            # 创建新版本
            DocumentVersion.objects.create(
                document=instance,
                title=serializer.validated_data.get('title', instance.title),
                content=serializer.validated_data.get('content', instance.content),
                version=new_version_num,
                creator=request.user
            )
        
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        """增加文档浏览次数"""
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        return Response({'status': 'success'})
    
    @action(detail=True, methods=['post'])
    def rollback_version(self, request, pk=None):
        """回滚到指定版本"""
        instance = self.get_object()
        version_id = request.data.get('version_id')
        
        try:
            version = DocumentVersion.objects.get(id=version_id, document=instance)
            instance.title = version.title
            instance.content = version.content
            instance.save()
            
            # 创建新版本记录(回滚操作)
            latest_version = instance.versions.order_by('-version').first()
            new_version_num = latest_version.version + 1 if latest_version else 1
            
            DocumentVersion.objects.create(
                document=instance,
                title=version.title,
                content=version.content,
                version=new_version_num,
                creator=request.user
            )
            
            return Response({'status': 'success'})
        except DocumentVersion.DoesNotExist:
            return Response({'error': '指定版本不存在'}, status=status.HTTP_404_NOT_FOUND)

class DocumentAttachmentViewSet(CustomModelViewSet):
    """
    文档附件管理
    list:查询
    create:新增
    update:修改
    destroy:删除
    """
    queryset = DocumentAttachment.objects.all()
    serializer_class = DocumentAttachmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document']
    
    def perform_create(self, serializer):
        # 设置上传人为当前用户
        serializer.save(creator=self.request.user)

class DocumentVersionViewSet(CustomModelViewSet):
    """
    文档版本管理
    list:查询
    """
    queryset = DocumentVersion.objects.all()
    serializer_class = DocumentVersionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document']
    http_method_names = ['get', 'head', 'options']  # 只允许查询操作
