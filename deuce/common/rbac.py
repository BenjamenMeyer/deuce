"""
RBAC Denotations
"""
from functools import wraps
import inspect

# RBAC Permission Levels
#   Observer - View Only
#   Creator - View, Create, Edit
#   Admin - View, Create, Edit, Delete
RBAC_Permissions = (None, 'observer', 'creator', 'admin')

RBAC_OBSERVER = RBAC_Permissions[1]
RBAC_CREATOR = RBAC_Permissions[2]
RBAC_ADMIN = RBAC_Permissions[3]


class RbacError(ValueError):
    pass

def rbac_require(permission_level):
    
    def runner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_spec = inspect.getargspec(func)
            func_params = dict()
            func_params.update(zip(func_spec.args, args))
            func_params.update(kwargs)

            assert permission_level in RBAC_Permissions
            return func(args[0], **func_params)
        return wrapper
    return runner
