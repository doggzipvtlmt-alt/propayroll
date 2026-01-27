from datetime import datetime

from bson import ObjectId
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import HROnly, MakerOnly, RoleAnyPermission
from core.db import get_collection
from core.excel import workbook_from_rows, excel_response


def _mask_aadhaar(value):
    if not value:
        return value
    value = str(value)
    if len(value) <= 4:
        return value
    return '*' * (len(value) - 4) + value[-4:]


class EmployeeListCreateView(APIView):
    permission_classes = [HROnly]

    def get(self, request):
        employees = list(get_collection('employees').find())
        for item in employees:
            item['id'] = str(item.pop('_id'))
        if request.query_params.get('export') == 'true':
            workbook = workbook_from_rows(employees)
            return excel_response(workbook, 'employees.xlsx')
        return Response({'results': employees})

    def post(self, request):
        payload = request.data.copy()
        designation = payload.get('designation')
        salary_ctc = float(payload.get('salary_ctc', 0))
        limit = get_collection('salary_limits').find_one({'designation': designation})
        if limit and salary_ctc > float(limit.get('max_ctc', 0)):
            return Response(
                {
                    'error': 'Salary exceeds allowed limit.',
                    'suggested_max_ctc': limit.get('max_ctc'),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        payload['aadhaar'] = _mask_aadhaar(payload.get('aadhaar'))
        payload['status'] = 'INACTIVE'
        payload['approval_stage'] = 'FINANCE_REVIEW'
        payload['created_at'] = datetime.utcnow()
        payload['updated_at'] = datetime.utcnow()
        get_collection('employees').insert_one(payload)
        return Response({'message': 'Employee created and sent for finance review.'}, status=status.HTTP_201_CREATED)


class EmployeeDetailView(APIView):
    permission_classes = [HROnly]

    def get(self, request, employee_id):
        employee = get_collection('employees').find_one({'_id': ObjectId(employee_id)})
        if not employee:
            return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)
        employee['id'] = str(employee.pop('_id'))
        return Response(employee)

    def put(self, request, employee_id):
        payload = request.data.copy()
        payload['aadhaar'] = _mask_aadhaar(payload.get('aadhaar'))
        payload['updated_at'] = datetime.utcnow()
        result = get_collection('employees').update_one({'_id': ObjectId(employee_id)}, {'$set': payload})
        if result.matched_count == 0:
            return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'Employee updated.'})

    def delete(self, request, employee_id):
        result = get_collection('employees').delete_one({'_id': ObjectId(employee_id)})
        if result.deleted_count == 0:
            return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeeApprovalView(APIView):
    permission_classes = [RoleAnyPermission]
    allowed_roles = {'FINANCE', 'MD', 'MAKER', 'SUPERUSER'}

    def post(self, request, employee_id):
        employees = get_collection('employees')
        employee = employees.find_one({'_id': ObjectId(employee_id)})
        if not employee:
            return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)
        role = request.user.role
        if role == 'FINANCE' and employee.get('approval_stage') == 'FINANCE_REVIEW':
            next_stage = 'MD_REVIEW'
        elif role == 'MD' and employee.get('approval_stage') == 'MD_REVIEW':
            next_stage = 'MAKER_REVIEW'
        elif role in {'MAKER', 'MD', 'SUPERUSER'}:
            next_stage = 'APPROVED'
        else:
            return Response({'error': 'Not allowed at this stage.'}, status=status.HTTP_400_BAD_REQUEST)
        update = {
            'approval_stage': next_stage,
            'updated_at': datetime.utcnow(),
        }
        if next_stage == 'APPROVED':
            update['status'] = 'ACTIVE'
        employees.update_one({'_id': employee['_id']}, {'$set': update})
        return Response({'message': f'Employee moved to {next_stage}.'})


class EmployeeRejectView(APIView):
    permission_classes = [RoleAnyPermission]
    allowed_roles = {'FINANCE', 'MD', 'MAKER', 'SUPERUSER'}

    def post(self, request, employee_id):
        reason = request.data.get('reason', 'Rejected')
        result = get_collection('employees').update_one(
            {'_id': ObjectId(employee_id)},
            {'$set': {'approval_stage': 'REJECTED', 'status': 'INACTIVE', 'rejection_reason': reason}},
        )
        if result.matched_count == 0:
            return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'Employee rejected.'})


class SalaryLimitView(APIView):
    permission_classes = [MakerOnly]

    def post(self, request):
        designation = request.data.get('designation')
        max_ctc = request.data.get('max_ctc')
        if not designation or max_ctc is None:
            return Response({'error': 'designation and max_ctc are required'}, status=status.HTTP_400_BAD_REQUEST)
        get_collection('salary_limits').update_one(
            {'designation': designation},
            {'$set': {'designation': designation, 'max_ctc': float(max_ctc), 'updated_at': datetime.utcnow()}},
            upsert=True,
        )
        return Response({'message': 'Salary limit set.'})


class HRDashboardView(APIView):
    permission_classes = [RoleAnyPermission]
    allowed_roles = {'HR', 'MAKER', 'MD', 'FINANCE', 'SUPERUSER'}

    def get(self, request):
        employees = get_collection('employees')
        return Response(
            {
                'total': employees.count_documents({}),
                'active': employees.count_documents({'status': 'ACTIVE'}),
                'pending_finance': employees.count_documents({'approval_stage': 'FINANCE_REVIEW'}),
                'pending_md': employees.count_documents({'approval_stage': 'MD_REVIEW'}),
                'pending_maker': employees.count_documents({'approval_stage': 'MAKER_REVIEW'}),
            }
        )
