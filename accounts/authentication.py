from dataclasses import dataclass

from bson import ObjectId
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from core.db import get_collection


@dataclass
class MongoUser:
    id: str
    email: str
    role: str
    full_name: str
    status: str

    @property
    def is_authenticated(self):
        return True


class MongoJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        try:
            prefix, token = auth_header.split(' ')
        except ValueError:
            raise AuthenticationFailed('Invalid authorization header.')
        if prefix.lower() != 'bearer':
            return None
        try:
            access = AccessToken(token)
            user_id = access.get('user_id')
        except Exception as exc:
            raise AuthenticationFailed('Invalid token.') from exc
        if not user_id:
            raise AuthenticationFailed('Invalid token payload.')
        user = get_collection('users').find_one({'_id': ObjectId(user_id)})
        if not user or user.get('status') != 'ACTIVE':
            raise AuthenticationFailed('User is inactive.')
        mongo_user = MongoUser(
            id=str(user['_id']),
            email=user['email'],
            role=user['role'],
            full_name=user.get('full_name', ''),
            status=user['status'],
        )
        return mongo_user, access
