from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import EmployeeOnly
from core.db import get_collection


class EmployeeProfileView(APIView):
    permission_classes = [EmployeeOnly]

    def get(self, request):
        employee = get_collection('employees').find_one({'official_email': request.user.email})
        if not employee:
            return Response({'error': 'Employee profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        employee['id'] = str(employee.pop('_id'))
        return Response(employee)


class EmployeeDocumentView(APIView):
    permission_classes = [EmployeeOnly]

    def post(self, request):
        payload = request.data.copy()
        payload['employee_email'] = request.user.email
        payload['created_at'] = datetime.utcnow()
        get_collection('employee_documents').insert_one(payload)
        return Response({'message': 'Document metadata saved.'}, status=status.HTTP_201_CREATED)


class LeaveRequestView(APIView):
    permission_classes = [EmployeeOnly]

    def post(self, request):
        payload = request.data.copy()
        payload['employee_email'] = request.user.email
        payload['status'] = 'PENDING'
        payload['created_at'] = datetime.utcnow()
        get_collection('leave_requests').insert_one(payload)
        return Response({'message': 'Leave request submitted.'}, status=status.HTTP_201_CREATED)


class SalarySlipView(APIView):
    permission_classes = [EmployeeOnly]

    def get(self, request):
        slips = list(get_collection('salary_slips').find({'employee_email': request.user.email}))
        for slip in slips:
            slip['id'] = str(slip.pop('_id'))
        return Response({'results': slips})


class GrievanceView(APIView):
    permission_classes = [EmployeeOnly]

    def post(self, request):
        payload = request.data.copy()
        payload['employee_email'] = request.user.email
        payload['status'] = 'OPEN'
        payload['created_at'] = datetime.utcnow()
        get_collection('grievances').insert_one(payload)
        return Response({'message': 'Grievance ticket submitted.'}, status=status.HTTP_201_CREATED)


class NoticesView(APIView):
    permission_classes = [EmployeeOnly]

    def get(self, request):
        notices = list(get_collection('notices').find())
        for notice in notices:
            notice['id'] = str(notice.pop('_id'))
        return Response({'results': notices})


class SurveysView(APIView):
    permission_classes = [EmployeeOnly]

    def get(self, request):
        surveys = list(get_collection('surveys').find())
        for survey in surveys:
            survey['id'] = str(survey.pop('_id'))
        return Response({'results': surveys})
