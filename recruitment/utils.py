from datetime import timedelta
from django.conf import settings
from django.utils import timezone

from .models import Candidate, WhatsAppMessage

STATUS_COLORS = {
    Candidate.Status.NEW: 'status-new',
    Candidate.Status.INTERVIEW_SCHEDULED: 'status-scheduled',
    Candidate.Status.CONFIRMED: 'status-confirmed',
    Candidate.Status.INTERVIEW_DONE: 'status-done',
    Candidate.Status.SELECTED: 'status-selected',
    Candidate.Status.REJECTED: 'status-rejected',
    Candidate.Status.HOLD: 'status-hold',
    Candidate.Status.DOCUMENT_PENDING: 'status-docs',
    Candidate.Status.DOCUMENT_COMPLETED: 'status-docs-done',
    Candidate.Status.JOINED: 'status-joined',
    Candidate.Status.DROPPED: 'status-dropped',
}

WHATSAPP_TEMPLATES = {
    'interview_confirmation': (
        "Namaste {name}! {role} interview fix ho gaya hai. "
        "Kal {date} {time} pe aana. Reply 'YES' ya 'NO' karein."
    ),
    'interview_reminder': (
        "Reminder: {name}, kal {date} {time} interview hai. "
        "Aap confirm kar rahe ho? Reply 'YES' ya 'NO'."
    ),
    'document_request': (
        "Shabash {name}! Aap select ho gaye. "
        "Please Aadhaar aur bank details bhej do. Dhanyavaad!"
    ),
}


def get_setting(name: str, default: str) -> str:
    return getattr(settings, name, default)


def send_whatsapp_simulated(candidate: Candidate, template_key: str) -> str:
    template = WHATSAPP_TEMPLATES[template_key]
    message = template.format(
        name=candidate.name,
        role=candidate.role,
        date=candidate.interview_date.strftime('%d %b') if candidate.interview_date else 'aaj',
        time=candidate.interview_time.strftime('%I:%M %p') if candidate.interview_time else 'time',
    )
    WhatsAppMessage.objects.create(candidate=candidate, message=message)
    return message


def should_send_reminder(candidate: Candidate) -> bool:
    if candidate.status != Candidate.Status.INTERVIEW_SCHEDULED or not candidate.updated_at:
        return False
    deadline = candidate.updated_at + timedelta(hours=12)
    return timezone.now() >= deadline
