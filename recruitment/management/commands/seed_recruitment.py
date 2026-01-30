from django.core.management.base import BaseCommand
from django.utils import timezone

from recruitment.models import Candidate


class Command(BaseCommand):
    help = 'Seed sample recruitment candidates.'

    def handle(self, *args, **options):
        today = timezone.localdate()
        samples = [
            {
                'name': 'Raju Kumar',
                'phone': '9000000001',
                'area': 'Noida',
                'role': 'Delivery Rider',
                'availability': Candidate.Availability.MORNING,
                'status': Candidate.Status.NEW,
            },
            {
                'name': 'Pooja Devi',
                'phone': '9000000002',
                'area': 'Delhi',
                'role': 'Warehouse Picker',
                'availability': Candidate.Availability.EVENING,
                'status': Candidate.Status.INTERVIEW_SCHEDULED,
                'interview_date': today,
                'interview_time': timezone.now().time().replace(second=0, microsecond=0),
            },
            {
                'name': 'Imran Khan',
                'phone': '9000000003',
                'area': 'Gurgaon',
                'role': 'Driver',
                'availability': Candidate.Availability.MORNING,
                'status': Candidate.Status.CONFIRMED,
                'interview_date': today,
                'interview_time': timezone.now().time().replace(second=0, microsecond=0),
            },
            {
                'name': 'Sunita Singh',
                'phone': '9000000004',
                'area': 'Ghaziabad',
                'role': 'Helper',
                'availability': Candidate.Availability.EVENING,
                'status': Candidate.Status.DOCUMENT_PENDING,
                'aadhaar_status': Candidate.DocumentStatus.RECEIVED,
                'bank_status': Candidate.DocumentStatus.PENDING,
            },
        ]
        for data in samples:
            Candidate.objects.create(**data)
        self.stdout.write(self.style.SUCCESS('Sample recruitment candidates created.'))
