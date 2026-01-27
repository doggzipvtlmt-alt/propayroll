from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.db import get_collection
from core.excel import workbook_from_rows, excel_response, load_rows_from_upload
from accounts.permissions import MakerOnly


def root_view(request):
    accept_header = request.headers.get('accept', '')
    if 'text/html' in accept_header:
        return render(request, 'index.html')
    return JsonResponse({'name': 'Doggzi Office OS API', 'status': 'ok'})


def health_view(request):
    return JsonResponse({'status': 'healthy'})


class TemplateDownloadView(APIView):
    permission_classes = [MakerOnly]

    def get(self, request, module):
        templates = {
            'employees': [
                'employee_code', 'full_name', 'official_email', 'personal_email', 'phone',
                'department', 'designation', 'salary_ctc', 'salary_basic', 'status',
            ],
            'revenue': ['source', 'amount', 'date', 'notes'],
            'expenses': ['category', 'vendor', 'amount', 'date', 'notes'],
            'payroll': ['employee_code', 'month', 'amount', 'notes'],
            'budgets': ['department', 'amount', 'fiscal_year', 'notes'],
        }
        headers = templates.get(module)
        if not headers:
            return Response({'error': 'Unknown module'}, status=status.HTTP_400_BAD_REQUEST)
        workbook = workbook_from_rows([dict.fromkeys(headers, '')])
        return excel_response(workbook, f'{module}_template.xlsx')


class ImportModuleView(APIView):
    permission_classes = [MakerOnly]

    def post(self, request, module):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'file is required'}, status=status.HTTP_400_BAD_REQUEST)
        rows = load_rows_from_upload(file_obj)
        collection_map = {
            'employees': 'employees',
            'revenue': 'revenue_entries',
            'expenses': 'expense_entries',
            'payroll': 'payroll_records',
            'budgets': 'budget_entries',
        }
        collection_name = collection_map.get(module)
        if not collection_name:
            return Response({'error': 'Unknown module'}, status=status.HTTP_400_BAD_REQUEST)
        collection = get_collection(collection_name)
        for row in rows:
            row['created_at'] = datetime.utcnow()
        if rows:
            collection.insert_many(rows)
        return Response({'inserted': len(rows)})
