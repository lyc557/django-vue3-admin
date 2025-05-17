import logging
from django.core.management.base import BaseCommand

from dvadmin.hrms.fixtures.initialize import Initialize

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    初始化人力资源管理系统
    python manage.py init_hrms
    """

    def handle(self, *args, **options):
        Initialize(app='dvadmin.hrms').run()
        print("人力资源管理系统初始化数据完成！")