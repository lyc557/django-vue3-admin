from django.core.management.base import BaseCommand
from dvadmin.kb.models import DocumentTag, DocumentCategory

class KnowledgeInitialize:
    """
    知识库数据初始化类
    """
    def __init__(self, reset=False):
        self.reset = reset

    def run(self):
        """
        执行初始化流程
        """
        self.init_categories()
        self.init_tags()

    def init_categories(self):
        """
        初始化知识库分类
        """
        from dvadmin.kb.models import DocumentCategory
        
        categories = [
            {"name": "技术文档", "order": 1},
            {"name": "产品文档", "order": 2},
            {"name": "帮助中心", "order": 3}
        ]
        
        for category in categories:
            DocumentCategory.objects.get_or_create(
                name=category['name'],
                defaults={
                    'order': category['order']
                }
            )
        print("知识库分类初始化完成")

    def init_tags(self):
        """
        初始化知识库标签
        """
        tags = [
            {"name": "Python", "order": 1},
            {"name": "Django", "order": 2},
            {"name": "Vue", "order": 3},
            {"name": "JavaScript", "order": 4},
            {"name": "TypeScript", "order": 5},
            {"name": "HTML/CSS", "order": 6},
            {"name": "MySQL", "order": 7},
            {"name": "PostgreSQL", "order": 8},
            {"name": "Redis", "order": 9},
            {"name": "Docker", "order": 10},
            {"name": "Kubernetes", "order": 11},
            {"name": "Git", "order": 12},
        ]
        
        for tag in tags:
            DocumentTag.objects.get_or_create(
                name=tag['name'],

            )
        print("知识库标签初始化完成")

class Command(BaseCommand):
    """
    知识库初始化命令
    """
    def add_arguments(self, parser):
        parser.add_argument('-y', '--yes', action='store_true', help='重置已有数据')

    def handle(self, *args, **options):
        reset = options.get('yes', False)
        KnowledgeInitialize(reset=reset).run()