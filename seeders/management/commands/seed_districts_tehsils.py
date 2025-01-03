from django.core.management.base import BaseCommand
from your_app.models import TblDivisions, TblDistricts, TblTehsils


class Command(BaseCommand):
    help = "Seed Divisions, Districts, and Tehsils for Punjab, Pakistan"

    def handle(self, *args, **kwargs):
        self.seed_divisions()
        self.seed_districts()
        self.seed_tehsils()

    def seed_divisions(self):
        divisions = [
            {"division_id": 1, "division_name": "Lahore", "division_code": "LHR"},
            {"division_id": 2, "division_name": "Faisalabad", "division_code": "FSD"},
            {"division_id": 3, "division_name": "Rawalpindi", "division_code": "RWP"},
            {"division_id": 4, "division_name": "Sargodha", "division_code": "SGD"},
            {"division_id": 5, "division_name": "Multan", "division_code": "MLT"},
            {"division_id": 6, "division_name": "Sahiwal", "division_code": "SWL"},
            {"division_id": 7, "division_name": "Gujranwala", "division_code": "GWL"},
            {"division_id": 8, "division_name": "Bahawalpur", "division_code": "BWP"},
            {"division_id": 9, "division_name": "Dera Ghazi Khan", "division_code": "DGK"},
            {"division_id": 10, "division_name": "Gujrat", "division_code": "GRT"},
        ]

        for division in divisions:
            obj, created = TblDivisions.objects.get_or_create(
                division_id=division["division_id"],
                defaults={
                    "division_name": division["division_name"],
                    "division_code": division["division_code"],
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Division {obj.division_name} created'))
            else:
                self.stdout.write(self.style.WARNING(f'Division {obj.division_name} already exists'))

    def seed_districts(self):
        districts = [
            {"district_id": 1, "division_id": 1, "district_name": "Lahore", "district_code": "LHR"},
            {"district_id": 2, "division_id": 1, "district_name": "Kasur", "district_code": "KSR"},
            {"district_id": 3, "division_id": 1, "district_name": "Sheikhupura", "district_code": "SKP"},
            {"district_id": 4, "division_id": 1, "district_name": "Nankana Sahib", "district_code": "NNS"},
            {"district_id": 5, "division_id": 2, "district_name": "Faisalabad", "district_code": "FSD"},
            {"district_id": 6, "division_id": 2, "district_name": "Jhang", "district_code": "JHG"},
            {"district_id": 7, "division_id": 2, "district_name": "Toba Tek Singh", "district_code": "TTS"},
            {"district_id": 8, "division_id": 2, "district_name": "Chiniot", "district_code": "CHT"},
            {"district_id": 9, "division_id": 3, "district_name": "Rawalpindi", "district_code": "RWP"},
            {"district_id": 10, "division_id": 3, "district_name": "Attock", "district_code": "ATK"},
            {"district_id": 11, "division_id": 3, "district_name": "Jhelum", "district_code": "JLM"},
            {"district_id": 12, "division_id": 3, "district_name": "Chakwal", "district_code": "CKL"},
            {"district_id": 13, "division_id": 4, "district_name": "Sargodha", "district_code": "SGD"},
            {"district_id": 14, "division_id": 4, "district_name": "Khushab", "district_code": "KSB"},
            {"district_id": 15, "division_id": 4, "district_name": "Mianwali", "district_code": "MWL"},
            {"district_id": 16, "division_id": 4, "district_name": "Bhakkar", "district_code": "BKR"},
            {"district_id": 17, "division_id": 5, "district_name": "Multan", "district_code": "MLT"},
            {"district_id": 18, "division_id": 5, "district_name": "Lodhran", "district_code": "LDN"},
            {"district_id": 19, "division_id": 5, "district_name": "Vehari", "district_code": "VHR"},
            {"district_id": 20, "division_id": 5, "district_name": "Khanewal", "district_code": "KNW"},
            {"district_id": 21, "division_id": 6, "district_name": "Sahiwal", "district_code": "SWL"},
            {"district_id": 22, "division_id": 6, "district_name": "Pakpattan", "district_code": "PPT"},
            {"district_id": 23, "division_id": 6, "district_name": "Okara", "district_code": "OKR"},
            {"district_id": 24, "division_id": 7, "district_name": "Gujranwala", "district_code": "GWL"},
            {"district_id": 25, "division_id": 7, "district_name": "Gujrat", "district_code": "GRT"},
            {"district_id": 26, "division_id": 7, "district_name": "Hafizabad", "district_code": "HZD"},
            {"district_id": 27, "division_id": 7, "district_name": "Mandi Bahauddin", "district_code": "MBD"},
            {"district_id": 28, "division_id": 7, "district_name": "Narowal", "district_code": "NWL"},
            {"district_id": 29, "division_id": 7, "district_name": "Sialkot", "district_code": "SLK"},
            {"district_id": 30, "division_id": 8, "district_name": "Bahawalpur", "district_code": "BWP"},
            {"district_id": 31, "division_id": 8, "district_name": "Bahawalnagar", "district_code": "BWN"},
            {"district_id": 32, "division_id": 8, "district_name": "Rahim Yar Khan", "district_code": "RYK"},
            {"district_id": 33, "division_id": 9, "district_name": "Dera Ghazi Khan", "district_code": "DGK"},
            {"district_id": 34, "division_id": 9, "district_name": "Rajanpur", "district_code": "RJP"},
            {"district_id": 35, "division_id": 9, "district_name": "Muzaffargarh", "district_code": "MZG"},
            {"district_id": 36, "division_id": 9, "district_name": "Layyah", "district_code": "LYH"},
        ]

        for district in districts:
            obj, created = TblDistricts.objects.get_or_create(
                district_id=district["district_id"],
                defaults={
                    "division_id": district["division_id"],
                    "district_name": district["district_name"],
                    "district_code": district["district_code"],
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'District {obj.district_name} created'))
            else:
                self.stdout.write(self.style.WARNING(f'District {obj.district_name} already exists'))

    def seed_tehsils(self):
        # Add tehsils logic here based on districts
        pass  # Implement similarly with tehsil-specific data.