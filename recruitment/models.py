from django.db import models
from django.utils import timezone


class Candidate(models.Model):
    class Availability(models.TextChoices):
        MORNING = 'MORNING', 'Morning'
        EVENING = 'EVENING', 'Evening'

    class Status(models.TextChoices):
        NEW = 'NEW', '🟢 New'
        INTERVIEW_SCHEDULED = 'INTERVIEW_SCHEDULED', '🟡 Interview Scheduled'
        CONFIRMED = 'CONFIRMED', '🟡 Confirmed'
        INTERVIEW_DONE = 'INTERVIEW_DONE', '🟡 Interview Done'
        SELECTED = 'SELECTED', '🟢 Selected'
        REJECTED = 'REJECTED', '🔴 Rejected'
        HOLD = 'HOLD', '🟡 Hold'
        DOCUMENT_PENDING = 'DOCUMENT_PENDING', '🟡 Document Pending'
        DOCUMENT_COMPLETED = 'DOCUMENT_COMPLETED', '🟢 Document Completed'
        JOINED = 'JOINED', '🟢 Joined'
        DROPPED = 'DROPPED', '🔴 Dropped'

    class DocumentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RECEIVED = 'RECEIVED', 'Received'

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    area = models.CharField(max_length=120)
    role = models.CharField(max_length=120)
    availability = models.CharField(max_length=20, choices=Availability.choices)
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.NEW)
    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.TimeField(null=True, blank=True)
    interview_done_at = models.DateTimeField(null=True, blank=True)
    aadhaar_status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.PENDING,
    )
    bank_status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_interview_done(self):
        self.interview_done_at = timezone.now()
        self.status = self.Status.INTERVIEW_DONE

    def __str__(self):
        return f"{self.name} ({self.phone})"


class WhatsAppMessage(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='whatsapp_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.name}: {self.message[:30]}"
