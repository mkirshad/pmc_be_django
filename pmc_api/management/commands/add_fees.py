from django.core.management.base import BaseCommand
from pmc_api.models import ApplicantDetail, ApplicantFee, Producer
from decimal import Decimal
from pmc_api.models_choices import *

class Command(BaseCommand):
    help = "Add fees for existing ApplicantDetail records where status != 'Created'"

    def handle(self, *args, **kwargs):

        # Fetch all ApplicantDetail records where status != 'Created'
        applicants = ApplicantDetail.objects.exclude(application_status='Created')

        for applicant in applicants:
            # Determine fee based on logic
            license_type = applicant.registration_for
            fee = None

            if license_type == 'Producer':
                producer = getattr(applicant, 'producer', None)
                if producer and producer.number_of_machines:
                    machines = int(producer.number_of_machines)
                    if machines <= 5:
                        fee = fee_structure['Producer']['upto_5_machines']
                    elif 6 <= machines <= 10:
                        fee = fee_structure['Producer']['from_6_to_10_machines']
                    else:
                        fee = fee_structure['Producer']['more_than_10_machines']
            elif license_type in fee_structure:
                try:
                    # Safely access businessprofile and entity_type
                    entity_type = getattr(applicant.businessprofile, 'entity_type', 'Individual')
                    fee = fee_structure.get(license_type, {}).get(entity_type, Decimal('0.00'))
                except AttributeError:
                    # Skip the record if businessprofile is not present
                    self.stdout.write(f"Skipped Applicant ID: {applicant.id} - No business profile found")
                    continue

            if fee:
                # Check if fee already exists
                existing_fee = ApplicantFee.objects.filter(applicant=applicant, fee_amount=fee).exists()
                if not existing_fee:
                    # Create a new ApplicantFee
                    ApplicantFee.objects.create(
                        applicant=applicant,
                        fee_amount=fee,
                        is_settled=False,
                        reason="Initial fee for existing record"
                    )
                    self.stdout.write(f"Fee added for Applicant ID: {applicant.id} - Amount: {fee}")
                else:
                    self.stdout.write(f"Fee already exists for Applicant ID: {applicant.id}")
            else:
                self.stdout.write(f"No fee applicable for Applicant ID: {applicant.id}")

        self.stdout.write("Fee addition process completed.")
