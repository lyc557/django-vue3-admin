from rest_framework import serializers
from django.contrib.auth import get_user_model
from dvadmin.kb.models import Document, DocumentCategory, DocumentTag, DocumentVersion, DocumentAttachment

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    """用户简单序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'name', 'avatar')

class DocumentTagSerializer(serializers.ModelSerializer):
    """文档标签序列化器"""
    class Meta:
        model = DocumentTag
        fields = '__all__'
        read_only_fields = ('id', 'create_datetime', 'update_datetime')

class DocumentCategorySerializer(serializers.ModelSerializer):
    """文档分类序列化器"""
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    
    class Meta:
        model = DocumentCategory
        fields = '__all__'
        read_only_fields = ('id', 'create_datetime', 'update_datetime')

class DocumentAttachmentSerializer(serializers.ModelSerializer):
    """文档附件序列化器"""
    creator_name = serializers.CharField(source='creator.name', read_only=True)
    
    class Meta:
        model = DocumentAttachment
        fields = '__all__'
        read_only_fields = ('id', 'create_datetime', 'update_datetime', 'creator_name')

class DocumentVersionSerializer(serializers.ModelSerializer):
    """文档版本序列化器"""
    creator_name = serializers.CharField(source='creator.name', read_only=True)
    
    class Meta:
        model = DocumentVersion
        fields = '__all__'
        read_only_fields = ('id', 'create_datetime', 'update_datetime', 'creator_name')

class DocumentSerializer(serializers.ModelSerializer):
    """文档序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    creator_name = serializers.CharField(source='creator.name', read_only=True)
    tags_info = DocumentTagSerializer(source='tags', many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('id', 'create_datetime', 'update_datetime', 'creator_name', 'category_name', 'tags_info', 'status_display', 'view_count')

class DocumentDetailSerializer(DocumentSerializer):
    """文档详情序列化器"""
    attachments = DocumentAttachmentSerializer(many=True, read_only=True)
    versions = DocumentVersionSerializer(many=True, read_only=True)
    creator = UserSimpleSerializer(read_only=True)
    
    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ('attachments', 'versions')