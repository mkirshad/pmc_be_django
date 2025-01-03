import decimal
import re

from django.core.exceptions import ValidationError


def validate_latitude(value):
    # Convert the value to string to check format
    value_str = format(value, '.6f')  # Ensures 6 decimal places

    # Regex to ensure format: two digits before decimal and six after
    if not re.match(r'^\d{2}\.\d{6}$', value_str):
        raise ValidationError(
            "Latitude must be in the format XX.XXXXXX, with exactly 2 digits before and 6 digits after the decimal point.")

    # Ensure the value is between 20.000000 and 40.000000
    if value < decimal.Decimal('20.000000') or value > decimal.Decimal('40.000000'):
        raise ValidationError("Latitude must be between 20.000000 and 40.000000.")


def validate_longitude(value):
    # Convert the value to string to check format
    value_str = format(value, '.6f')  # Ensures 6 decimal places

    # Regex to ensure format: two digits before decimal and six after
    if not re.match(r'^\d{2}\.\d{6}$', value_str):
        raise ValidationError(
            "Longitude must be in the format XX.XXXXXX, with exactly 2 digits before and 6 digits after the decimal point.")

    if value < 60 or value > 80:
        raise ValidationError("Latitude must be between 60.000000 and 80.000000.")
