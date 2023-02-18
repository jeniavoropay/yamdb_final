import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

MESSAGE_REGEX = 'Некорректные символы: {}'
MESSAGE_RESERVED_USERNAMES = 'Нельзя указывать {} в качестве username.'
MESSAGE_YEAR = (
    'Год выпуска произведения не может быть больше текущего: {current_year}. '
    'Указанный год: {value}.'
)
USERNAME_REGEX = r'([\w.@+-]+)'


def regex_validator(value):
    invalid_simbols = ''.join(set(re.sub(USERNAME_REGEX, '', str(value))))
    if invalid_simbols:
        raise ValidationError(MESSAGE_REGEX.format(invalid_simbols))
    return value


def reserved_names_validator(value):
    for reserved_username in settings.RESERVED_USERNAMES:
        if value == reserved_username:
            raise ValidationError(MESSAGE_RESERVED_USERNAMES.format(value))
    return value


def validate_year(value):
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            MESSAGE_YEAR.format(current_year=current_year, value=value)
        )
    return value
