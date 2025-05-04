import re

from django.core.validators import EmailValidator, ValidationError
from django.utils.encoding import punycode
from django.utils.translation import gettext as _


class CustomEmailValidator(EmailValidator):
    """
    Email validator for block ru and by emails
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invalid_emails = [".ru", ".by"]
        self.message = "login__email"

    def __call__(self, value):
        if not value or "@" not in value:
            raise ValidationError(self.message, code=self.code, params={"value": value})

        user_part, domain_part = value.rsplit("@", 1)

        if not self.user_regex.match(user_part):
            raise ValidationError(self.message, code=self.code, params={"value": value})

        if any(domain_part.endswith(invalid_domain) for invalid_domain in self.invalid_emails):
            raise ValidationError("ru__email", code=self.code, params={"value": value})

        if domain_part not in self.domain_allowlist and not self.validate_domain_part(
                domain_part
        ):
            # Try for possible IDN domain-part
            try:
                domain_part = punycode(domain_part)
            except UnicodeError:
                pass
            else:
                if self.validate_domain_part(domain_part):
                    return
            raise ValidationError(self.message, code=self.code, params={"value": value})


class CustomPasswordValidator:
    def validate(self, password):
        if len(password) < 8:
            raise ValidationError(_("The password must be at least 8 characters long."))

        if not re.search(r"[A-Z]", password):
            raise ValidationError(_("The password must contain at least one uppercase letter."))

        if not re.search(r"[a-z]", password):
            raise ValidationError(_("The password must contain at least one lowercase letter."))

        if not re.search(r"\d", password):
            raise ValidationError(_("The password must contain at least one digit."))

        if not re.search(r"[!@#$%^&*()_\-+=\[\]{};:,.<>?/\\|`~]", password):
            raise ValidationError(_("The password must contain at least one special character."))

    def get_help_text(self):
        return _(
            "Your password must be at least 8 characters long and contain at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character."
        )


validate_email = EmailValidator()