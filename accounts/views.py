import re
import secrets
from datetime import datetime

from bson import ObjectId
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.permissions import MakerOnly
from core.db import get_collection

EMAIL_PATTERN = re.compile(r'^[A-Za-z0-9._%+-]+@doggzi\.com$')


def _validate_doggzi_email(email):
    return bool(EMAIL_PATTERN.match(email or ''))


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data
        required_fields = ['full_name', 'email', 'phone_number', 'role_requested']
        for field in required_fields:
            if not payload.get(field):
                return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        email = payload['email'].lower().strip()
        if not _validate_doggzi_email(email):
            return Response({'error': 'Only @doggzi.com emails are allowed.'}, status=status.HTTP_400_BAD_REQUEST)
        signup_requests = get_collection('signup_requests')
        if signup_requests.find_one({'email': email, 'status': 'PENDING'}):
            return Response({'error': 'Signup request already pending.'}, status=status.HTTP_400_BAD_REQUEST)
        signup_requests.insert_one(
            {
                'full_name': payload['full_name'],
                'email': email,
                'phone_number': payload['phone_number'],
                'role_requested': payload['role_requested'],
                'status': 'PENDING',
                'created_at': datetime.utcnow(),
            }
        )
        return Response({'message': 'Signup request submitted.'}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': 'email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = get_collection('users').find_one({'email': email})
        if not user or user.get('status') != 'ACTIVE':
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        if not check_password(password, user.get('password_hash', '')):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken()
        refresh['user_id'] = str(user['_id'])
        refresh['email'] = user['email']
        refresh['role'] = user['role']
        access = refresh.access_token
        profile = {
            'id': str(user['_id']),
            'email': user['email'],
            'full_name': user.get('full_name'),
            'role': user['role'],
            'status': user['status'],
        }
        return Response({'access': str(access), 'refresh': str(refresh), 'user': profile})


class PendingSignupView(APIView):
    permission_classes = [MakerOnly]

    def get(self, request):
        pending = list(get_collection('signup_requests').find({'status': 'PENDING'}))
        for item in pending:
            item['id'] = str(item.pop('_id'))
        return Response({'results': pending})


class ApproveSignupView(APIView):
    permission_classes = [MakerOnly]

    def post(self, request, request_id):
        signup_requests = get_collection('signup_requests')
        signup = signup_requests.find_one({'_id': ObjectId(request_id)})
        if not signup or signup.get('status') != 'PENDING':
            return Response({'error': 'Signup request not found.'}, status=status.HTTP_404_NOT_FOUND)
        password = request.data.get('password') or secrets.token_urlsafe(10)
        user = {
            'full_name': signup['full_name'],
            'email': signup['email'],
            'phone_number': signup['phone_number'],
            'role': signup['role_requested'],
            'status': 'ACTIVE',
            'password_hash': make_password(password),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        users = get_collection('users')
        users.insert_one(user)
        signup_requests.update_one(
            {'_id': signup['_id']},
            {
                '$set': {
                    'status': 'APPROVED',
                    'approved_at': datetime.utcnow(),
                    'approved_by': request.user.email,
                }
            },
        )
        return Response({'message': 'User approved.', 'temporary_password': password})


class RejectSignupView(APIView):
    permission_classes = [MakerOnly]

    def post(self, request, request_id):
        reason = request.data.get('reason', 'Rejected by maker')
        signup_requests = get_collection('signup_requests')
        result = signup_requests.update_one(
            {'_id': ObjectId(request_id), 'status': 'PENDING'},
            {
                '$set': {
                    'status': 'REJECTED',
                    'rejected_at': datetime.utcnow(),
                    'rejected_by': request.user.email,
                    'reason': reason,
                }
            },
        )
        if result.matched_count == 0:
            return Response({'error': 'Signup request not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'Signup request rejected.'})
