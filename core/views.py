import json
from datetime import datetime
from pathlib import Path

from django.http import JsonResponse
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.db import get_collection
from core.excel import workbook_from_rows, excel_response, load_rows_from_upload
from core.hrms import (
    CANDIDATES_FILE,
    ONBOARDING_FILE,
    append_row,
    build_onboarding_row,
    candidate_exists,
    create_candidate_id,
    load_rows,
    save_files,
)
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


class CandidateListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'candidates': load_rows(CANDIDATES_FILE)})

    def post(self, request):
        required_fields = [
            'candidate_name',
            'mobile_number',
            'email',
            'position_applied_for',
            'source',
            'interview_scheduled',
            'interview_status',
            'selection_status',
            'offer_released',
            'final_status',
            'remarks',
        ]
        data = request.data
        missing = [field for field in required_fields if not str(data.get(field, '')).strip()]
        if missing:
            return Response(
                {'error': f"Missing required fields: {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            validate_email(data.get('email'))
        except ValidationError:
            return Response({'error': 'Invalid email address.'}, status=status.HTTP_400_BAD_REQUEST)

        mobile_number = str(data.get('mobile_number')).strip()
        if not mobile_number.isdigit():
            return Response({'error': 'Mobile number must be numeric.'}, status=status.HTTP_400_BAD_REQUEST)

        interview_scheduled = data.get('interview_scheduled')
        interview_date = data.get('interview_date', '')
        if interview_scheduled == 'Yes' and not interview_date:
            return Response({'error': 'Interview date is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if interview_scheduled == 'No':
            interview_date = ''

        selection_status = data.get('selection_status')
        joining_date = data.get('joining_date', '')
        if selection_status == 'Selected' and not joining_date:
            return Response({'error': 'Joining date is required for selected candidates.'}, status=status.HTTP_400_BAD_REQUEST)
        if selection_status != 'Selected':
            joining_date = ''

        candidate_id = create_candidate_id()
        row = {
            'candidate_id': candidate_id,
            'created_at': datetime.utcnow().isoformat(),
            'candidate_name': data.get('candidate_name'),
            'mobile_number': mobile_number,
            'email': data.get('email'),
            'position_applied_for': data.get('position_applied_for'),
            'source': data.get('source'),
            'interview_scheduled': interview_scheduled,
            'interview_date': interview_date,
            'interview_status': data.get('interview_status'),
            'selection_status': selection_status,
            'offer_released': data.get('offer_released'),
            'joining_date': joining_date,
            'final_status': data.get('final_status'),
            'remarks': data.get('remarks'),
        }
        append_row(CANDIDATES_FILE, row)
        return Response({'candidate_id': candidate_id}, status=status.HTTP_201_CREATED)


class OnboardingCreateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        data = request.data
        candidate_id = data.get('candidate_id')
        category = data.get('category')
        if not candidate_id or not category:
            return Response({'error': 'Candidate ID and category are required.'}, status=status.HTTP_400_BAD_REQUEST)

        candidate = candidate_exists(candidate_id)
        if not candidate:
            return Response({'error': 'Candidate not found.'}, status=status.HTTP_400_BAD_REQUEST)
        if candidate.get('selection_status') != 'Selected':
            return Response({'error': 'Onboarding allowed only for selected candidates.'}, status=status.HTTP_400_BAD_REQUEST)

        if data.get('hr_verification') not in ('on', 'true', 'True', 'yes', 'Yes'):
            return Response({'error': 'HR verification is mandatory.'}, status=status.HTTP_400_BAD_REQUEST)

        allowed_ext = {'.pdf', '.jpg', '.jpeg', '.png'}

        def validate_files(field_name: str, required: bool, multiple: bool = False):
            files = request.FILES.getlist(field_name) if multiple else request.FILES.getlist(field_name)
            if required and not files:
                return None, f'Missing required document: {field_name}'
            for file_obj in files:
                ext = Path(file_obj.name).suffix.lower()
                if ext not in allowed_ext:
                    return None, f'Invalid file type for {field_name}'
            return files, None

        uploaded_docs: dict[str, list[str]] = {}
        optional_docs: dict[str, list[str]] = {}
        file_payload = []

        if category == 'formal':
            required_fields = [
                ('formal_aadhaar_card', False),
                ('formal_pan_card', False),
                ('formal_address_proof', False),
                ('formal_educational_certificates', True),
                ('formal_marksheet_10_12', False),
                ('formal_graduation_diploma', False),
                ('formal_resume_cv', False),
                ('formal_passport_photo', False),
                ('formal_bank_details', False),
                ('formal_pan_card_repeat', False),
                ('formal_medical_fitness', False),
            ]
            for field, multiple in required_fields:
                files, error = validate_files(field, True, multiple)
                if error:
                    return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
                uploaded_docs[field] = [file_obj.name for file_obj in files]
                file_payload.append((field, files))

            if data.get('formal_experienced') not in ('Yes', 'No'):
                return Response({'error': 'Experience selection is required.'}, status=status.HTTP_400_BAD_REQUEST)
            if data.get('formal_experienced') == 'Yes':
                exp_fields = [
                    ('formal_offer_letter', False),
                    ('formal_experience_letter', False),
                    ('formal_salary_slips', True),
                ]
                for field, multiple in exp_fields:
                    files, error = validate_files(field, True, multiple)
                    if error:
                        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
                    uploaded_docs[field] = [file_obj.name for file_obj in files]
                    file_payload.append((field, files))
            else:
                exp_fields = [
                    ('formal_offer_letter', False),
                    ('formal_experience_letter', False),
                    ('formal_salary_slips', True),
                ]
                for field, multiple in exp_fields:
                    files, error = validate_files(field, False, multiple)
                    if files:
                        optional_docs[field] = [file_obj.name for file_obj in files]
                        file_payload.append((field, files))
                    if error:
                        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

            optional_fields = [
                ('formal_post_graduation', False),
            ]
            for field, multiple in optional_fields:
                files, error = validate_files(field, False, multiple)
                if files:
                    optional_docs[field] = [file_obj.name for file_obj in files]
                    file_payload.append((field, files))
                if error:
                    return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        elif category == 'non_formal':
            text_fields = [
                'non_decl_name',
                'non_decl_age',
                'non_decl_address',
                'non_decl_skill',
                'non_decl_willingness',
                'non_decl_signature',
                'non_skill_proof_type',
            ]
            missing_text = [field for field in text_fields if not str(data.get(field, '')).strip()]
            if missing_text:
                return Response(
                    {'error': f"Missing required fields: {', '.join(missing_text)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            required_fields = [
                ('non_aadhaar_card', False),
                ('non_address_proof', False),
                ('non_passport_photo', False),
                ('non_bank_details', False),
                ('non_self_declaration', False),
                ('non_skill_proof_file', False),
            ]
            for field, multiple in required_fields:
                files, error = validate_files(field, True, multiple)
                if error:
                    return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
                uploaded_docs[field] = [file_obj.name for file_obj in files]
                file_payload.append((field, files))

            optional_fields = [('non_medical_fitness', False)]
            for field, multiple in optional_fields:
                files, error = validate_files(field, False, multiple)
                if files:
                    optional_docs[field] = [file_obj.name for file_obj in files]
                    file_payload.append((field, files))
                if error:
                    return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid category.'}, status=status.HTTP_400_BAD_REQUEST)

        optional_common = [
            ('opt_police_verification', False),
            ('opt_pf_esic', False),
            ('opt_emergency_contact', False),
            ('opt_signed_offer', False),
        ]
        for field, multiple in optional_common:
            files, error = validate_files(field, False, multiple)
            if files:
                optional_docs[field] = [file_obj.name for file_obj in files]
                file_payload.append((field, files))
            if error:
                return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        if not str(data.get('final_notes', '')).strip():
            return Response({'error': 'Final onboarding status is required.'}, status=status.HTTP_400_BAD_REQUEST)

        save_files(candidate_id, category, file_payload)

        row = build_onboarding_row(
            candidate_id=candidate_id,
            category=category,
            document_status='Complete',
            hr_verified='Yes',
            final_onboarding_status='Submitted',
            uploaded_documents=json.dumps(uploaded_docs),
            optional_documents=json.dumps(optional_docs),
            notes=data.get('final_notes'),
        )
        append_row(ONBOARDING_FILE, row)
        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)
