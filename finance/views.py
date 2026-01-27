from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import FinanceOnly, RoleAnyPermission
from core.db import get_collection
from core.excel import workbook_from_rows, excel_response


def _list_or_export(collection_name, request):
    items = list(get_collection(collection_name).find())
    for item in items:
        item['id'] = str(item.pop('_id'))
    if request.query_params.get('export') == 'true':
        workbook = workbook_from_rows(items)
        return excel_response(workbook, f'{collection_name}.xlsx')
    return Response({'results': items})


def _create(collection_name, payload):
    payload['created_at'] = datetime.utcnow()
    get_collection(collection_name).insert_one(payload)


class RevenueView(APIView):
    permission_classes = [FinanceOnly]

    def get(self, request):
        return _list_or_export('revenue_entries', request)

    def post(self, request):
        _create('revenue_entries', request.data.copy())
        return Response({'message': 'Revenue entry created.'}, status=status.HTTP_201_CREATED)


class ExpenseView(APIView):
    permission_classes = [FinanceOnly]

    def get(self, request):
        return _list_or_export('expense_entries', request)

    def post(self, request):
        _create('expense_entries', request.data.copy())
        return Response({'message': 'Expense entry created.'}, status=status.HTTP_201_CREATED)


class PayrollView(APIView):
    permission_classes = [FinanceOnly]

    def get(self, request):
        return _list_or_export('payroll_records', request)

    def post(self, request):
        _create('payroll_records', request.data.copy())
        return Response({'message': 'Payroll record created.'}, status=status.HTTP_201_CREATED)


class BudgetView(APIView):
    permission_classes = [FinanceOnly]

    def get(self, request):
        return _list_or_export('budget_entries', request)

    def post(self, request):
        _create('budget_entries', request.data.copy())
        return Response({'message': 'Budget entry created.'}, status=status.HTTP_201_CREATED)


class ReportExportView(APIView):
    permission_classes = [RoleAnyPermission]
    allowed_roles = {'FINANCE', 'MAKER', 'MD', 'SUPERUSER'}

    def get(self, request):
        report_type = request.query_params.get('type', 'summary')
        data = [
            {'metric': 'total_revenue', 'value': get_collection('revenue_entries').count_documents({})},
            {'metric': 'total_expenses', 'value': get_collection('expense_entries').count_documents({})},
        ]
        workbook = workbook_from_rows(data)
        return excel_response(workbook, f'{report_type}_report.xlsx')
