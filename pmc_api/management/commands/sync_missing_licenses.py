from django.core.management.base import BaseCommand
from pmc_api.models import ApplicantDetail, License
from pmc_api.views import create_or_update_license  # Adjust path if needed
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create licenses for applicants with assigned_group="Download License" if missing'

    def handle(self, *args, **kwargs):
        applicants = ApplicantDetail.objects.filter(
            assigned_group='Download License'
        ).exclude(
            id__in=License.objects.values_list('applicant_id', flat=True)
        )

        created_count = 0
        for applicant in applicants:
            # You can pass `user=None` or a superuser if required
            create_or_update_license(applicant, user=None)
            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'{created_count} license(s) created successfully for Download License applicants.'
        ))
