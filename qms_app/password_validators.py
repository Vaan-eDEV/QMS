import re
from django.core.exceptions import ValidationError

class StrongPasswordValidator:

    def validate(self, password, user=None):

        if len(password) < 12:
            raise ValidationError("Password must be at least 12 characters.")

        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain one uppercase letter.")

        if not re.search(r'[0-9]', password):
            raise ValidationError("Password must contain one number.")

        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            raise ValidationError("Password must contain one special character.")

    def get_help_text(self):
        return "Password must be 12 characters with uppercase, number and special symbol."