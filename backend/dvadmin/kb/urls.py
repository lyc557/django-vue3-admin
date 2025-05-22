from rest_framework.routers import SimpleRouter
from django.urls import path, include
from dvadmin.kb.views.document import (
    DocumentViewSet, DocumentCategoryViewSet, DocumentTagViewSet,
    DocumentVersionViewSet, DocumentAttachmentViewSet
)

router = SimpleRouter()
router.register("document", DocumentViewSet)
router.register("category", DocumentCategoryViewSet)
router.register("tag", DocumentTagViewSet)
router.register("version", DocumentVersionViewSet)
router.register("attachment", DocumentAttachmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]