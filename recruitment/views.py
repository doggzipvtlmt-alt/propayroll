from datetime import date

from django.conf import settings
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Candidate
from .utils import STATUS_COLORS, send_whatsapp_simulated, should_send_reminder


ROLE_SESSION_KEYS = {
    'interviewer': 'recruitment_interviewer_ok',
    'hr': 'recruitment_hr_ok',
    'admin': 'recruitment_admin_ok',
}


def _get_pin(role: str) -> str:
    default_pins = {
        'interviewer': '1234',
        'hr': '5678',
        'admin': '9999',
    }
    setting_key = f'RECRUITMENT_{role.upper()}_PIN'
    return getattr(settings, setting_key, default_pins[role])


def _require_pin(request, role: str):
    if request.session.get(ROLE_SESSION_KEYS[role]):
        return None
    return redirect('recruitment-pin', role=role)


def home(request):
    return render(request, 'recruitment/home.html')


@require_http_methods(['GET', 'POST'])
def intake(request):
    if request.method == 'POST':
        candidate = Candidate.objects.create(
            name=request.POST.get('name', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            area=request.POST.get('area', '').strip(),
            role=request.POST.get('role', '').strip(),
            availability=request.POST.get('availability'),
        )
        return redirect('recruitment-pipeline')

    return render(request, 'recruitment/intake.html', {
        'availability_choices': Candidate.Availability.choices,
    })


@require_http_methods(['GET'])
def pipeline(request):
    status_filter = request.GET.get('status')
    candidates = Candidate.objects.all().order_by('-created_at')
    if status_filter:
        candidates = candidates.filter(status=status_filter)
    today = date.today()
    reminder_ids = {
        candidate.id for candidate in candidates if should_send_reminder(candidate)
    }
    context = {
        'candidates': candidates,
        'status_choices': Candidate.Status.choices,
        'status_filter': status_filter,
        'status_colors': STATUS_COLORS,
        'today': today,
        'reminder_ids': reminder_ids,
    }
    return render(request, 'recruitment/pipeline.html', context)


@require_http_methods(['POST'])
def update_status(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    new_status = request.POST.get('status')
    interview_date = request.POST.get('interview_date')
    interview_time = request.POST.get('interview_time')
    if interview_date:
        candidate.interview_date = interview_date
    if interview_time:
        candidate.interview_time = interview_time

    if new_status == Candidate.Status.SELECTED:
        candidate.status = Candidate.Status.DOCUMENT_PENDING
        candidate.aadhaar_status = Candidate.DocumentStatus.PENDING
        candidate.bank_status = Candidate.DocumentStatus.PENDING
        send_whatsapp_simulated(candidate, 'document_request')
    else:
        candidate.status = new_status

    if new_status == Candidate.Status.INTERVIEW_SCHEDULED:
        send_whatsapp_simulated(candidate, 'interview_confirmation')

    candidate.save()
    return redirect('recruitment-pipeline')


@require_http_methods(['POST'])
def send_reminder(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    send_whatsapp_simulated(candidate, 'interview_reminder')
    return redirect('recruitment-pipeline')


@require_http_methods(['GET', 'POST'])
def pin_login(request, role):
    if role not in ROLE_SESSION_KEYS:
        return redirect('recruitment-home')

    error = None
    if request.method == 'POST':
        pin = request.POST.get('pin')
        if pin == _get_pin(role):
            request.session[ROLE_SESSION_KEYS[role]] = True
            if role == 'interviewer':
                return redirect('recruitment-interviewer-today')
            if role == 'hr':
                return redirect('recruitment-hr-panel')
            if role == 'admin':
                return redirect('recruitment-admin-dashboard')
        else:
            error = 'PIN galat hai. Dobara try karo.'

    return render(request, 'recruitment/pin_login.html', {
        'role': role,
        'error': error,
    })


@require_http_methods(['GET', 'POST'])
def interviewer_today(request):
    redirect_response = _require_pin(request, 'interviewer')
    if redirect_response:
        return redirect_response

    today = timezone.localdate()
    interviews = Candidate.objects.filter(
        interview_date=today,
        status__in=[Candidate.Status.INTERVIEW_SCHEDULED, Candidate.Status.CONFIRMED],
    ).order_by('interview_time')

    return render(request, 'recruitment/interviewer_today.html', {
        'candidates': interviews,
        'today': today,
        'status_colors': STATUS_COLORS,
    })


@require_http_methods(['POST'])
def interviewer_action(request, candidate_id):
    redirect_response = _require_pin(request, 'interviewer')
    if redirect_response:
        return redirect_response

    candidate = get_object_or_404(Candidate, id=candidate_id)
    action = request.POST.get('action')
    if action == 'select':
        candidate.status = Candidate.Status.DOCUMENT_PENDING
        candidate.aadhaar_status = Candidate.DocumentStatus.PENDING
        candidate.bank_status = Candidate.DocumentStatus.PENDING
        send_whatsapp_simulated(candidate, 'document_request')
    elif action == 'reject':
        candidate.status = Candidate.Status.REJECTED
    elif action == 'hold':
        candidate.status = Candidate.Status.HOLD
    candidate.interview_done_at = timezone.now()
    candidate.save()
    return redirect('recruitment-interviewer-today')


@require_http_methods(['GET'])
def hr_panel(request):
    redirect_response = _require_pin(request, 'hr')
    if redirect_response:
        return redirect_response

    candidates = Candidate.objects.filter(
        status__in=[Candidate.Status.DOCUMENT_PENDING, Candidate.Status.DOCUMENT_COMPLETED],
    ).order_by('-updated_at')

    return render(request, 'recruitment/hr_panel.html', {
        'candidates': candidates,
        'status_colors': STATUS_COLORS,
    })


@require_http_methods(['POST'])
def hr_update_document(request, candidate_id):
    redirect_response = _require_pin(request, 'hr')
    if redirect_response:
        return redirect_response

    candidate = get_object_or_404(Candidate, id=candidate_id)
    doc_type = request.POST.get('doc_type')
    doc_status = request.POST.get('doc_status')
    if doc_type == 'aadhaar':
        candidate.aadhaar_status = doc_status
    elif doc_type == 'bank':
        candidate.bank_status = doc_status

    if (
        candidate.aadhaar_status == Candidate.DocumentStatus.RECEIVED
        and candidate.bank_status == Candidate.DocumentStatus.RECEIVED
    ):
        candidate.status = Candidate.Status.DOCUMENT_COMPLETED

    candidate.save()
    return redirect('recruitment-hr-panel')


@require_http_methods(['POST'])
def hr_finalize(request, candidate_id):
    redirect_response = _require_pin(request, 'hr')
    if redirect_response:
        return redirect_response

    candidate = get_object_or_404(Candidate, id=candidate_id)
    action = request.POST.get('action')
    if action == 'joined':
        candidate.status = Candidate.Status.JOINED
    elif action == 'dropped':
        candidate.status = Candidate.Status.DROPPED
    candidate.save()
    return redirect('recruitment-hr-panel')


@require_http_methods(['GET'])
def admin_dashboard(request):
    redirect_response = _require_pin(request, 'admin')
    if redirect_response:
        return redirect_response

    today = timezone.localdate()
    interviews_today = Candidate.objects.filter(interview_date=today).count()
    confirmed_today = Candidate.objects.filter(
        interview_date=today,
        status=Candidate.Status.CONFIRMED,
    ).count()
    not_confirmed_today = Candidate.objects.filter(
        interview_date=today,
        status=Candidate.Status.INTERVIEW_SCHEDULED,
    ).count()
    selected = Candidate.objects.filter(status=Candidate.Status.DOCUMENT_PENDING).count()
    dropouts = Candidate.objects.filter(status=Candidate.Status.DROPPED).count()
    joinings = Candidate.objects.filter(status=Candidate.Status.JOINED).count()
    status_counts = Candidate.objects.values('status').annotate(total=Count('id'))

    return render(request, 'recruitment/admin_dashboard.html', {
        'interviews_today': interviews_today,
        'confirmed_today': confirmed_today,
        'not_confirmed_today': not_confirmed_today,
        'selected': selected,
        'dropouts': dropouts,
        'joinings': joinings,
        'status_counts': status_counts,
        'today': today,
        'status_colors': STATUS_COLORS,
    })
