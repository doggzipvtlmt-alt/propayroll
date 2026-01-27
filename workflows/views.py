from datetime import datetime

from bson import ObjectId
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import HROnly, RoleAnyPermission
from core.db import get_collection


class AppraisalListCreateView(APIView):
    permission_classes = [HROnly]

    def get(self, request):
        appraisals = list(get_collection('appraisals').find())
        for item in appraisals:
            item['id'] = str(item.pop('_id'))
        return Response({'results': appraisals})

    def post(self, request):
        payload = request.data.copy()
        payload['status'] = 'DRAFT'
        payload['created_at'] = datetime.utcnow()
        get_collection('appraisals').insert_one(payload)
        return Response({'message': 'Appraisal cycle created.'}, status=status.HTTP_201_CREATED)


class AppraisalSubmitView(APIView):
    permission_classes = [HROnly]

    def post(self, request, appraisal_id):
        result = get_collection('appraisals').update_one(
            {'_id': ObjectId(appraisal_id)},
            {'$set': {'status': 'SUBMITTED', 'submitted_at': datetime.utcnow()}},
        )
        if result.matched_count == 0:
            return Response({'error': 'Appraisal not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'Appraisal submitted for finance review.'})


class AppraisalApproveView(APIView):
    permission_classes = [RoleAnyPermission]
    allowed_roles = {'FINANCE', 'MD', 'MAKER', 'SUPERUSER'}

    def post(self, request, appraisal_id):
        appraisals = get_collection('appraisals')
        appraisal = appraisals.find_one({'_id': ObjectId(appraisal_id)})
        if not appraisal:
            return Response({'error': 'Appraisal not found.'}, status=status.HTTP_404_NOT_FOUND)
        status_map = {
            'FINANCE': 'FINANCE_APPROVED',
            'MD': 'MD_APPROVED',
            'MAKER': 'MAKER_APPROVED',
            'SUPERUSER': 'MAKER_APPROVED',
        }
        next_status = status_map.get(request.user.role)
        appraisals.update_one(
            {'_id': appraisal['_id']},
            {'$set': {'status': next_status, 'updated_at': datetime.utcnow()}},
        )
        return Response({'message': f'Appraisal moved to {next_status}.'})


class PromotionListCreateView(APIView):
    permission_classes = [HROnly]

    def get(self, request):
        promotions = list(get_collection('promotions').find())
        for item in promotions:
            item['id'] = str(item.pop('_id'))
        return Response({'results': promotions})

    def post(self, request):
        payload = request.data.copy()
        payload['status'] = 'PENDING_MD'
        payload['created_at'] = datetime.utcnow()
        get_collection('promotions').insert_one(payload)
        return Response({'message': 'Promotion request created.'}, status=status.HTTP_201_CREATED)


class PromotionApproveView(APIView):
    permission_classes = [RoleAnyPermission]
    allowed_roles = {'MD', 'MAKER', 'SUPERUSER'}

    def post(self, request, promotion_id):
        promotions = get_collection('promotions')
        promotion = promotions.find_one({'_id': ObjectId(promotion_id)})
        if not promotion:
            return Response({'error': 'Promotion not found.'}, status=status.HTTP_404_NOT_FOUND)
        status_value = 'MAKER_APPROVED' if request.user.role in {'MAKER', 'SUPERUSER'} else 'MD_APPROVED'
        promotions.update_one(
            {'_id': promotion['_id']},
            {'$set': {'status': status_value, 'updated_at': datetime.utcnow()}},
        )
        return Response({'message': f'Promotion moved to {status_value}.'})


class PromotionRejectView(APIView):
    permission_classes = [RoleAnyPermission]
    allowed_roles = {'MD', 'MAKER', 'SUPERUSER'}

    def post(self, request, promotion_id):
        reason = request.data.get('reason', 'Rejected')
        result = get_collection('promotions').update_one(
            {'_id': ObjectId(promotion_id)},
            {'$set': {'status': 'REJECTED', 'reason': reason, 'updated_at': datetime.utcnow()}},
        )
        if result.matched_count == 0:
            return Response({'error': 'Promotion not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'Promotion rejected.'})
