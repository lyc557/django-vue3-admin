from django.db import models
from django.contrib.auth import get_user_model
from dvadmin.utils.models import CoreModel, table_prefix

User = get_user_model()

# 文档分类
class DocumentCategory(CoreModel):
    name = models.CharField(max_length=100, verbose_name="分类名称")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, verbose_name="父级分类")
    order = models.IntegerField(default=1, verbose_name="显示顺序")
    
    class Meta:
        db_table = table_prefix + "document_category"
        verbose_name = "文档分类"
        verbose_name_plural = verbose_name
        ordering = ("order",)
    
    def __str__(self):
        return self.name

# 文档标签
class DocumentTag(CoreModel):
    name = models.CharField(max_length=50, unique=True, verbose_name="标签名称")
    
    class Meta:
        db_table = table_prefix + "document_tag"
        verbose_name = "文档标签"
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name

# 文档主表
class Document(CoreModel):
    STATUS_CHOICES = (
        (0, "草稿"),
        (1, "已发布"),
    )
    
    title = models.CharField(max_length=200, verbose_name="文档标题")
    content = models.TextField(verbose_name="文档内容", help_text="支持Markdown格式")
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, verbose_name="所属分类")
    tags = models.ManyToManyField(DocumentTag, blank=True, verbose_name="标签")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人", related_name="created_documents")
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name="状态")
    view_count = models.IntegerField(default=0, verbose_name="浏览次数")
    vector_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="向量ID", help_text="用于AI检索")
    
    class Meta:
        db_table = table_prefix + "document"
        verbose_name = "知识文档"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # 如果是新创建的文档，保存后创建一个初始版本
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            DocumentVersion.objects.create(
                document=self,
                title=self.title,
                content=self.content,
                version=1,
                creator=self.creator
            )
        
# 文档版本历史
class DocumentVersion(CoreModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="versions", verbose_name="所属文档")
    title = models.CharField(max_length=200, verbose_name="文档标题")
    content = models.TextField(verbose_name="文档内容")
    version = models.IntegerField(verbose_name="版本号")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    
    class Meta:
        db_table = table_prefix + "document_version"
        verbose_name = "文档版本"
        verbose_name_plural = verbose_name
        ordering = ("-version",)
        unique_together = ("document", "version")
    
    def __str__(self):
        return f"{self.document.title} v{self.version}"

# 文档附件
class DocumentAttachment(CoreModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="attachments", verbose_name="所属文档")
    file = models.FileField(upload_to="document_attachments/%Y/%m/%d/", verbose_name="附件文件")
    name = models.CharField(max_length=200, verbose_name="附件名称")
    file_type = models.CharField(max_length=50, verbose_name="文件类型")
    file_size = models.IntegerField(verbose_name="文件大小(字节)")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="上传人")
    
    class Meta:
        db_table = table_prefix + "document_attachment"
        verbose_name = "文档附件"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
    
    def __str__(self):
        return self.name