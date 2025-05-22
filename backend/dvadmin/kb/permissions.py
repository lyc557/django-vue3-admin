from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    自定义权限：对象的创建者或管理员可以修改/删除
    """
    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # 管理员可以做任何操作
        if request.user.is_superuser:
            return True
            
        # 检查对象是否有creator属性
        if hasattr(obj, 'creator'):
            return obj.creator == request.user
            
        return False