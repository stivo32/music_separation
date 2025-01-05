from fourier.dao.base import BaseDAO
from fourier.auth.models import User, Role


class UsersDAO(BaseDAO):
    model = User


class RoleDAO(BaseDAO):
    model = Role
