import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from django.contrib.auth.password_validation import MinimumLengthValidator, CommonPasswordValidator


class PasswordValidator(MinimumLengthValidator, CommonPasswordValidator):
    """
        This validates that a password is at least of size 8(Using the MinimumLengthValidator),
        The password isn't soo common (Using the CommonPasswordValidator).
        In addition to this, it ensures that a password has at least one special character.
        [ !"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]
    """
    def __init__(self, min_length=8):
        super().__init__(min_length)
        self.min_length = min_length

    def validate(self, password, user=None):
        super(PasswordValidator, self).validate(password, user)

        regex = re.compile(r"[ !#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]")

        if not regex.findall(password):
            # This password has no special character
            raise ValidationError(
                _("This password must contain at least one special character"),
                code='no_special_character',
            )

    def get_help_text(self):
        return _(
            "Your password must contain one of the following characters. "
            "[ !#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]"
        )


def validate_email(email):
    # Ensures an email is of valid valid format using a regex.
    if not re.match(r"^[A-Za-z0-9.+_-]+@[A-Za-z0-9._-]+\.[a-zA-Z]*$", email):
        raise ValidationError(
                _("This is not a valid email format."),
                code='not_valid_format',
            )
