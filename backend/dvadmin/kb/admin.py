from django.contrib import admin
from dvadmin.kb.models import *

admin.site.register(Document)
admin.site.register(DocumentCategory)
admin.site.register(DocumentTag)
admin.site.register(DocumentVersion)
admin.site.register(DocumentAttachment)