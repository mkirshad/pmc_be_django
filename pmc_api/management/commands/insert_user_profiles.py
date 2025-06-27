from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from pmc_api.models import UserProfile, TblDistricts

class Command(BaseCommand):
    help = "Insert UserProfile records for users in the 'DO' group based on their district."

    def handle(self, *args, **kwargs):
        try:
            # ✅ Get the 'DO' group
            do_group = Group.objects.get(name="DO")

            # ✅ Get all users in the 'DO' group
            do_users = User.objects.filter(groups=do_group)

            created_count = 0
            updated_count = 0

            for user in do_users:
                username = user.username.lower()  # Convert username to lowercase
                parts = username.split(".")  # Extract district from username
                
                if len(parts) < 2:
                    self.stdout.write(self.style.WARNING(f"Skipping user '{user.username}' - Invalid format"))
                    continue  # Skip invalid usernames

                district_code = parts[-1]  # Extract district short name from the username

                # ✅ Find the district by short_name (case-insensitive)
                district = TblDistricts.objects.filter(short_name__iexact=district_code).first()

                if not district:
                    self.stdout.write(self.style.WARNING(f"Skipping user '{user.username}' - No matching district found"))
                    continue  # Skip if no matching district

                # ✅ Create or update the UserProfile
                user_profile, created = UserProfile.objects.update_or_create(
                    user=user,
                    defaults={"district": district}
                )

                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Created UserProfile for {user.username} in {district.district_name}"))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated UserProfile for {user.username} in {district.district_name}"))

            self.stdout.write(self.style.SUCCESS(f"✅ Finished! {created_count} created, {updated_count} updated."))

        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ 'DO' group does not exist."))
